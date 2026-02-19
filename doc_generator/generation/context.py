"""Context building and file grouping utilities for documentation generation.

Design decision: Context builders are separated from the orchestrator
because they are pure data-transformation functions with no LLM interaction.
This makes them independently testable and keeps the orchestrator focused
on pipeline coordination.
"""

import re
import logging
from collections import defaultdict
from typing import Dict, List, Optional, Tuple

from ..models import FileInfo, ProjectInfo
from ..parsing import CodeParser

logger = logging.getLogger(__name__)


class ContextBuilder:
    """Builds structured context from parsed source code for LLM prompts.

    Design decision: All grouping, metadata formatting, and feature
    detection live here so the orchestrator stays thin and delegates
    data preparation to a single, cohesive helper.
    """

    def __init__(self, parser: CodeParser):
        """Initialise with the code parser (for classification and URL building).

        Args:
            parser: Configured CodeParser instance.
        """
        self.parser = parser

    # ------------------------------------------------------------------
    # File grouping
    # ------------------------------------------------------------------

    def group_by_category(
        self,
        source_projects: List[ProjectInfo],
    ) -> Dict[Tuple[str, Optional[str], Optional[str]], List[FileInfo]]:
        """Group source files by classification category.

        Returns:
            Dict keyed by (category, doc_file, doc_title) -> list of FileInfo.
        """
        groups: Dict[Tuple, List[FileInfo]] = defaultdict(list)
        for proj in source_projects:
            for fi in proj.files:
                cat, doc_file, doc_title = self.parser.classifier.classify_file(
                    fi.relative_path
                )
                groups[(cat, doc_file, doc_title)].append(fi)
        return dict(groups)

    def group_project_files(
        self, project: ProjectInfo
    ) -> Dict[Tuple[str, Optional[str], Optional[str]], List[FileInfo]]:
        """Group files within a single project by category."""
        groups: Dict[Tuple, List[FileInfo]] = defaultdict(list)
        for fi in project.files:
            cat, doc_file, doc_title = self.parser.classifier.classify_file(
                fi.relative_path
            )
            groups[(cat, doc_file, doc_title)].append(fi)
        return dict(groups)

    @staticmethod
    def all_files(projects: List[ProjectInfo]) -> List[FileInfo]:
        """Flatten all files across projects."""
        return [fi for proj in projects for fi in proj.files]

    @staticmethod
    def api_folder_name(source_projects: List[ProjectInfo]) -> str:
        """Derive the API folder name from the first source project."""
        if source_projects:
            return source_projects[0].name
        return "API"

    # ------------------------------------------------------------------
    # Content assembly for prompts
    # ------------------------------------------------------------------

    @staticmethod
    def combine_file_content(files: List[FileInfo], max_chars: int = 60_000) -> str:
        """Combine content of multiple files with headers."""
        parts: List[str] = []
        total = 0
        included = 0
        for fi in files:
            header = f"\n// FILE: {fi.relative_path}\n"
            if total + len(header) + len(fi.content) > max_chars:
                skipped = len(files) - included
                logger.warning(
                    "Source content cap (%d chars) reached. "
                    "Skipping %d remaining file(s); classes in those files "
                    "will not appear in the generated documentation.",
                    max_chars, skipped,
                )
                break
            parts.append(header)
            parts.append(fi.content)
            total += len(header) + len(fi.content)
            included += 1
        return "".join(parts)

    def build_class_metadata(
        self, files: List[FileInfo], project_source_prefix: str = ""
    ) -> str:
        """Build a structured summary of classes in the given files.

        Args:
            files: Parsed file metadata.
            project_source_prefix: Path prefix from repo root to the project
                directory (e.g., ``src/Ordering.API``). Used to construct
                correct GitHub source URLs.
        """
        lines: List[str] = []
        for fi in files:
            for cls in fi.classes:
                if project_source_prefix:
                    repo_path = f"{project_source_prefix}/{fi.relative_path}"
                else:
                    repo_path = fi.relative_path
                source = self.parser.classifier.source_url(
                    repo_path,
                    cls.line_number,
                )
                lines.append(f"- {cls.name} ({cls.kind}) at line {cls.line_number}")
                lines.append(f"  Source: {source}")
                if cls.base_class:
                    lines.append(f"  Extends: {cls.base_class}")
                if cls.interfaces:
                    lines.append(f"  Implements: {', '.join(cls.interfaces)}")
                for method in cls.methods:
                    lines.append(
                        f"  - Method: {method.signature} (line {method.line_number})"
                    )
                    if method.calls:
                        call_strs = [c.get("chain", c["method"]) for c in method.calls]
                        lines.append(f"    Calls: {', '.join(call_strs)}")
                for prop in cls.properties:
                    lines.append(
                        f"  - Property: {prop.prop_type} {prop.name} "
                        f"(line {prop.line_number})"
                    )
        return "\n".join(lines) if lines else "(no class metadata available)"

    def build_handler_context(
        self, endpoint_file: FileInfo, all_projects: List[ProjectInfo]
    ) -> str:
        """Build context about handlers and models related to an endpoint."""
        lines: List[str] = []
        for proj in all_projects:
            for fi in proj.files:
                if fi.category in ("command_handler", "query", "domain_event_handler"):
                    for cls in fi.classes:
                        lines.append(
                            f"- {cls.name} in {fi.relative_path} "
                            f"(line {cls.line_number})"
                        )
                        for m in cls.methods:
                            lines.append(f"  Method: {m.signature}")
        return "\n".join(lines[:100]) if lines else "(no handler context available)"

    @staticmethod
    def build_component_summary(projects: List[ProjectInfo]) -> str:
        """Build a high-level summary of all components across projects."""
        lines: List[str] = []
        for proj in projects:
            lines.append(f"\n### {proj.name} ({proj.total_files} files)")
            for fi in proj.files:
                for cls in fi.classes:
                    lines.append(f"- {cls.name} ({cls.kind}, {fi.category})")
        return "\n".join(lines)

    @staticmethod
    def detect_features(
        endpoint_file: FileInfo,
        feature_keywords: Optional[Dict[str, str]] = None,
    ) -> List[str]:
        """Detect feature names from an endpoint file based on method grouping.

        Design decision: Feature keywords are loaded from project_config.yml
        so they can be customised per-codebase (e.g., add 'Search', 'Browse'
        for Catalog). Falls back to a sensible default set if not provided.

        Args:
            endpoint_file: Parsed API endpoint file.
            feature_keywords: Mapping of method keyword -> feature suffix,
                loaded from ``feature_detection.feature_keywords`` in YAML.
        """
        if feature_keywords is None:
            feature_keywords = {
                "Create": "Creation",
                "Cancel": "Cancellation",
                "Ship": "Shipping",
                "Get": "Retrieval",
                "Delete": "Deletion",
                "Update": "Update",
            }
        features: List[str] = []
        for cls in endpoint_file.classes:
            for method in cls.methods:
                for keyword, feature_suffix in feature_keywords.items():
                    if keyword.lower() in method.name.lower():
                        entity = (
                            endpoint_file.filename
                            .replace("Api.cs", "")
                            .replace("Controller.cs", "")
                        )
                        if entity.endswith("s"):
                            entity = entity[:-1]
                        name = f"{entity} {feature_suffix}"
                        if name not in features:
                            features.append(name)
        return features

    @staticmethod
    def template_key_for(prompt_type: str) -> str:
        """Map a prompt type to its template_examples key."""
        return {
            "handler_doc": "handler",
            "query_doc": "handler",
            "aggregate_doc": "aggregate",
            "simple_doc": "simple",
            "infrastructure_doc": "infrastructure",
            "feature_doc": "feature",
            "overview_doc": "overview",
        }.get(prompt_type, "simple")
