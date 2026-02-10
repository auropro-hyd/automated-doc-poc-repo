"""Regex-based source code parser for .NET C# projects.

Design decision: Uses regex-based extraction (not AST/Roslyn) to keep
the tool lightweight, language-agnostic, and dependency-free beyond the
standard library. Regex reliably handles ~70% of call chains (simple
instance calls, constructors, 2-level chains). Complex patterns (LINQ,
lambdas, nested expressions) are delegated to the LLM during content
generation.

All scanning rules -- file extensions, exclude patterns -- are loaded
from project_config.yml via the constructor's config dict.
"""

import re
import logging
import fnmatch
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ..models import ClassInfo, FileInfo, MethodInfo, ProjectInfo, PropertyInfo
from .classifier import FileClassifier

logger = logging.getLogger(__name__)


class CodeParser:
    """Config-driven source code parser.

    Design decision: The parser owns file scanning, reading, and structural
    extraction. Classification and URL building are delegated to the
    companion ``FileClassifier`` (same config dict). Line numbers are
    extracted for every declaration to enable clickable source URLs
    downstream.
    """

    # -- Regex patterns for C# constructs --------------------------------

    # Namespace declaration
    _RE_NAMESPACE = re.compile(r'namespace\s+([\w.]+)')

    # Type declaration: public/internal/private [modifiers] class/interface/record/enum Name [: bases] {
    _RE_TYPE_DECL = re.compile(
        r'(?P<access>public|internal|private|protected)'
        r'(?:\s+(?P<modifiers>(?:(?:static|abstract|sealed|partial|readonly)\s+)*))?'
        r'\s*(?P<kind>class|interface|record|enum)\s+'
        r'(?P<name>\w+)'
        r'(?:\s*:\s*(?P<bases>[^{]+?))?'
        r'\s*\{',
        re.MULTILINE
    )

    # Method declaration: public [static] [async] [virtual|override] ReturnType Name(params)
    _RE_METHOD = re.compile(
        r'(?P<access>public|protected|private|internal)'
        r'(?:\s+(?:static\s+))?'
        r'(?P<async>\s*async\s+)?'
        r'(?:\s*(?:virtual|override|sealed|new)\s+)?'
        r'(?P<return>[\w<>\[\],\s\?]+?)\s+'
        r'(?P<name>\w+)\s*'
        r'\((?P<params>[^)]*)\)',
        re.MULTILINE
    )

    # Property / field declaration
    _RE_PROPERTY = re.compile(
        r'(?P<access>public|protected|private|internal)'
        r'(?:\s+(?:static|readonly|virtual|override|abstract)\s+)*'
        r'\s+(?P<type>[\w<>\[\],\?\s]+?)\s+'
        r'(?P<name>\w+)\s*'
        r'(?:\{|\s*[;=])',
        re.MULTILINE
    )

    # Call chain patterns for method body analysis
    _RE_INSTANCE_CALL = re.compile(r'(?:_\w+|\w+)\s*\.\s*(\w+)\s*\(')
    _RE_CHAIN_CALL = re.compile(r'(?:_\w+|\w+)\s*\.\s*(\w+)\s*\.\s*(\w+)\s*\(')
    _RE_CONSTRUCTOR = re.compile(r'new\s+(\w+)\s*\(')

    def __init__(self, config: Dict[str, Any]):
        """Initialise the parser with configuration from project_config.yml.

        Args:
            config: The full parsed YAML configuration dictionary.
        """
        self.config = config
        self.classifier = FileClassifier(config)
        self._file_extensions: List[str] = config.get("file_extensions", ["*.cs"])
        self._exclude_folders: List[str] = config.get("exclude_folders", [])
        self._exclude_files: List[str] = config.get("exclude_files", [])

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def parse_project(self, project_path: Path) -> ProjectInfo:
        """Parse all matching source files in a project directory.

        Args:
            project_path: Absolute or relative path to the project root.

        Returns:
            ProjectInfo with parsed file metadata.
        """
        project = ProjectInfo(name=project_path.name, path=project_path)
        if not project_path.exists():
            logger.warning("Project path does not exist: %s", project_path)
            return project

        for pattern in self._file_extensions:
            for file_path in project_path.rglob(pattern):
                if self._is_excluded(file_path):
                    continue
                file_info = self._parse_file(file_path, project_path)
                if file_info:
                    project.files.append(file_info)

        logger.info("Parsed %d files from %s", len(project.files), project.name)
        return project

    def parse_multiple_projects(self, project_paths: List[Path]) -> List[ProjectInfo]:
        """Parse several project directories.

        Args:
            project_paths: List of project root paths.

        Returns:
            List of ProjectInfo objects.
        """
        return [self.parse_project(p) for p in project_paths]

    def get_combined_content(
        self, projects: List[ProjectInfo], max_chars: int = 100_000
    ) -> str:
        """Concatenate source content from all projects, respecting a char limit.

        Args:
            projects: Parsed project list.
            max_chars: Soft character budget.

        Returns:
            Combined source string with file headers.
        """
        parts: List[str] = []
        total = 0
        for proj in projects:
            header = f"\n{'=' * 60}\n# PROJECT: {proj.name}\n{'=' * 60}\n"
            parts.append(header)
            total += len(header)
            for fi in proj.files:
                fh = f"\n// FILE: {fi.relative_path}\n"
                if total + len(fh) + len(fi.content) > max_chars:
                    remaining = max_chars - total - len(fh) - 100
                    if remaining > 500:
                        parts.append(fh)
                        parts.append(fi.content[:remaining])
                        parts.append("\n// ... (truncated)")
                    break
                parts.append(fh)
                parts.append(fi.content)
                total += len(fh) + len(fi.content)
        return "".join(parts)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _is_excluded(self, file_path: Path) -> bool:
        """Check whether a file should be skipped based on config rules."""
        for folder in self._exclude_folders:
            if folder in file_path.parts:
                return True
        for pattern in self._exclude_files:
            if fnmatch.fnmatch(file_path.name, pattern):
                return True
        return False

    def _parse_file(self, file_path: Path, project_path: Path) -> Optional[FileInfo]:
        """Parse a single source file and extract structured metadata."""
        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception as exc:
            logger.error("Could not read %s: %s", file_path, exc)
            return None

        rel = str(file_path.relative_to(project_path)).replace("\\", "/")
        category, _, _ = self.classifier.classify_file(rel)

        fi = FileInfo(
            path=file_path,
            filename=file_path.name,
            relative_path=rel,
            content=content,
            category=category,
        )

        fi.namespace = self._extract_namespace(content)
        fi.classes = self._extract_classes(content)

        logger.debug(
            "Parsed %s -> %d classes, category=%s",
            rel, len(fi.classes), category,
        )
        return fi

    # ------------------------------------------------------------------
    # Extraction methods
    # ------------------------------------------------------------------

    def _extract_namespace(self, content: str) -> Optional[str]:
        """Extract the first namespace declaration."""
        m = self._RE_NAMESPACE.search(content)
        return m.group(1) if m else None

    def _extract_classes(self, content: str) -> List[ClassInfo]:
        """Extract all type declarations (class, interface, record, enum)."""
        results: List[ClassInfo] = []

        for match in self._RE_TYPE_DECL.finditer(content):
            line_number = content[: match.start()].count("\n") + 1
            name = match.group("name")
            kind = match.group("kind")
            access = match.group("access")
            modifiers_raw = (match.group("modifiers") or "").split()
            bases_raw = match.group("bases") or ""

            base_class, interfaces = self._parse_bases(bases_raw)

            body_start = match.end() - 1  # position of '{'
            body = self._extract_brace_block(content, body_start)

            ci = ClassInfo(
                name=name,
                line_number=line_number,
                kind=kind,
                access_modifier=access,
                base_class=base_class,
                interfaces=interfaces,
                modifiers=modifiers_raw,
            )

            if body:
                ci.properties = self._extract_properties(body, line_number)
                ci.methods = self._extract_methods(body, line_number)

            results.append(ci)

        return results

    def _parse_bases(self, raw: str) -> Tuple[Optional[str], List[str]]:
        """Split a C# base list into base class and interfaces.

        Design decision: Heuristic -- names starting with 'I' followed by an
        uppercase letter are treated as interfaces.
        """
        if not raw.strip():
            return None, []
        parts = [p.strip() for p in raw.split(",")]
        clean = [re.sub(r"<.*?>", "", p).strip() for p in parts]
        base_class = None
        interfaces: List[str] = []
        for orig, name in zip(parts, clean):
            if re.match(r"^I[A-Z]", name):
                interfaces.append(orig.strip())
            elif base_class is None:
                base_class = orig.strip()
            else:
                interfaces.append(orig.strip())
        return base_class, interfaces

    def _extract_brace_block(self, content: str, start: int) -> Optional[str]:
        """Extract text between a matched pair of braces starting at *start*."""
        if start >= len(content) or content[start] != "{":
            return None
        depth = 0
        for i in range(start, len(content)):
            if content[i] == "{":
                depth += 1
            elif content[i] == "}":
                depth -= 1
                if depth == 0:
                    return content[start + 1: i]
        return None

    def _extract_properties(self, body: str, class_line: int) -> List[PropertyInfo]:
        """Extract property and field declarations from a class body."""
        results: List[PropertyInfo] = []
        seen: set = set()
        for match in self._RE_PROPERTY.finditer(body):
            name = match.group("name")
            if name in seen or name[0].islower():
                continue
            seen.add(name)
            line = class_line + body[: match.start()].count("\n")
            results.append(PropertyInfo(
                name=name,
                prop_type=match.group("type").strip(),
                line_number=line,
                access_modifier=match.group("access"),
            ))
        return results

    def _extract_methods(self, body: str, class_line: int) -> List[MethodInfo]:
        """Extract method declarations with full signatures and call chains."""
        results: List[MethodInfo] = []
        for match in self._RE_METHOD.finditer(body):
            name = match.group("name")
            line = class_line + body[: match.start()].count("\n")
            params_raw = match.group("params").strip()
            parameters = self._parse_params(params_raw)
            return_type = match.group("return").strip()
            is_async = bool(match.group("async"))

            search_start = match.end()
            brace_pos = body.find("{", search_start)
            method_body = ""
            if brace_pos != -1:
                method_body = self._extract_brace_block(body, brace_pos) or ""

            calls = self._extract_calls(method_body) if method_body else []

            results.append(MethodInfo(
                name=name,
                line_number=line,
                signature=f"{return_type} {name}({params_raw})",
                return_type=return_type,
                parameters=parameters,
                access_modifier=match.group("access"),
                is_async=is_async,
                body=method_body,
                calls=calls,
            ))
        return results

    def _parse_params(self, raw: str) -> List[Dict[str, str]]:
        """Parse a comma-separated parameter list into structured dicts."""
        if not raw:
            return []
        params: List[Dict[str, str]] = []
        for part in raw.split(","):
            part = part.strip()
            if not part:
                continue
            part = part.split("=")[0].strip()
            tokens = part.rsplit(None, 1)
            if len(tokens) == 2:
                params.append({"type": tokens[0].strip(), "name": tokens[1].strip()})
            else:
                params.append({"type": part, "name": ""})
        return params

    def _extract_calls(self, body: str) -> List[Dict[str, str]]:
        """Extract method invocations from a method body.

        Design decision: Only simple patterns are extracted via regex.
        Complex patterns (LINQ, lambdas) are left for the LLM.
        """
        calls: List[Dict[str, str]] = []
        seen: set = set()

        for m in self._RE_CHAIN_CALL.finditer(body):
            prop, method = m.group(1), m.group(2)
            key = f"{prop}.{method}"
            if key not in seen:
                seen.add(key)
                calls.append({"receiver": prop, "method": method, "chain": key})

        for m in self._RE_INSTANCE_CALL.finditer(body):
            method = m.group(1)
            if method not in seen and method[0].isupper():
                seen.add(method)
                calls.append({"receiver": "", "method": method})

        for m in self._RE_CONSTRUCTOR.finditer(body):
            cls = m.group(1)
            key = f"new {cls}"
            if key not in seen:
                seen.add(key)
                calls.append({"receiver": "new", "method": cls})

        return calls
