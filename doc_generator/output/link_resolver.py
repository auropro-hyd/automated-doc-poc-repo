"""Post-generation link resolver for generated documentation.

Design decision: The LLM generates cross-page links without awareness of
the actual file inventory or MkDocs anchor slugification. This module
runs after all docs are generated and before writing to disk. It builds
a deterministic inventory of files and headings, then repairs broken
internal links by redirecting to correct targets or stripping invalid links.

It also validates GitHub source URLs (in both markdown links and mermaid
click directives) against the actual repository filesystem, fixing
hallucinated paths and placeholder repository URLs.
"""

import logging
import re
import urllib.parse
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# Match markdown links [text](target), excluding those inside code blocks
_LINK_RE = re.compile(r'\[([^\]]*)\]\(([^)]+)\)')
# Match ## headings (with optional link syntax)
_HEADING_RE = re.compile(r'^##\s+(.+)$', re.MULTILINE)
# Strip [linktext](url) to get linktext
_LINK_TEXT_RE = re.compile(r'\[([^\]]+)\]\([^)]+\)')
# Match mermaid click directives: click NodeName href "URL" or click NodeName "URL"
_MERMAID_CLICK_RE = re.compile(
    r'(click\s+\w+\s+(?:href\s+)?")(https?://[^"]+)(")'
)
# Match GitHub-style URLs pointing to source files
_GITHUB_SOURCE_RE = re.compile(
    r'https?://github\.com/[^/]+/[^/]+/blob/[^/]+/(src/[^#"\s)]+)'
)


def _slugify(text: str) -> str:
    """Compute MkDocs-compatible anchor slug from heading text.

    MkDocs slugs: lowercase, replace spaces with hyphens, remove/replace
    special characters. Strips markdown link syntax first.
    """
    # Strip markdown link: [OrderingContext.cs](url) -> OrderingContext.cs
    stripped = _LINK_TEXT_RE.sub(r'\1', text).strip()
    # Lowercase
    s = stripped.lower()
    # Replace spaces and underscores with hyphens
    s = re.sub(r'[\s_]+', '-', s)
    # Remove characters that aren't alphanumeric or hyphen
    s = re.sub(r'[^a-z0-9-]', '', s)
    # Collapse multiple hyphens
    s = re.sub(r'-+', '-', s).strip('-')
    return s or 'section'


def _extract_entity_name(heading_text: str) -> Optional[str]:
    """Extract primary entity/class name from heading for lookup.

    Examples:
      "Order (Aggregate)" -> "Order"
      "[OrderingContext.cs](url)" -> "OrderingContext"
      "[CreateOrderCommandHandler](url)" -> "CreateOrderCommandHandler"
    """
    stripped = _LINK_TEXT_RE.sub(r'\1', heading_text).strip()
    if not stripped:
        return None
    # Take first "word" (before space or paren)
    match = re.match(r'^([\w.]+)', stripped)
    return match.group(1) if match else None


def _resolve_path(from_path: str, target: str) -> str:
    """Resolve a relative link target to a normalized doc path.

    Returns a path like "Ordering.Infrastructure/DataContext.md" or
    "Ordering.Domain/Aggregate.md". Handles ./ and ../
    """
    target = target.strip()
    if not target or target.startswith(('http://', 'https://')):
        return ""
    if '#' in target:
        path_part, _ = target.split('#', 1)
        path_part = path_part.strip()
    else:
        path_part = target
    if not path_part or not path_part.endswith('.md'):
        return ""
    path_part = urllib.parse.unquote(path_part).replace('\\', '/')
    from_parts = Path(from_path).parent.parts
    if path_part.startswith('./'):
        path_part = path_part[2:]
    elif path_part.startswith('../'):
        ups = 0
        while path_part.startswith('../'):
            path_part = path_part[3:].lstrip('/')
            ups += 1
        if ups >= len(from_parts):
            path_part = path_part
        else:
            parent = from_parts[:-ups]
            prefix = '/'.join(parent) + '/'
            if path_part.startswith(prefix):
                path_part = path_part[len(prefix):]
            path_part = prefix + path_part if parent else path_part
    if path_part.startswith('/'):
        path_part = path_part[1:]
    return path_part


class LinkResolver:
    """Resolves broken internal links in generated documentation."""

    def __init__(
        self,
        generated: Dict[str, str],
        repo_root: Optional[Path] = None,
        repo_url: Optional[str] = None,
    ):
        """Initialise with the generated content dict.

        Args:
            generated: Dict mapping relative doc paths to markdown content.
            repo_root: Absolute path to the repository root. When provided,
                GitHub source URLs are validated against the filesystem.
            repo_url: Configured repository URL (e.g.
                ``https://github.com/org/repo``). Used to fix placeholder
                URLs like ``github.com/your-repo/``.
        """
        self._generated = generated
        self._repo_root = repo_root
        self._repo_url = repo_url
        self._file_to_anchors: Dict[str, List[Tuple[str, str]]] = {}
        self._entity_to_location: Dict[str, Tuple[str, str]] = {}
        self._source_file_index: Dict[str, str] = {}  # basename -> repo-relative path

    def _build_inventory(self) -> None:
        """Build file and entity indexes from all generated content."""
        self._file_to_anchors.clear()
        self._entity_to_location.clear()

        for rel_path, content in self._generated.items():
            anchors: List[Tuple[str, str]] = []
            for m in _HEADING_RE.finditer(content):
                raw = m.group(1).strip()
                slug = _slugify(raw)
                entity = _extract_entity_name(raw)
                anchors.append((slug, raw))
                if entity and entity not in self._entity_to_location:
                    self._entity_to_location[entity] = (rel_path, slug)
            self._file_to_anchors[rel_path] = anchors

        logger.debug(
            "LinkResolver: built inventory for %d files, %d entities",
            len(self._file_to_anchors), len(self._entity_to_location),
        )

    def _build_source_file_index(self) -> None:
        """Scan the repository for source files and build a basename lookup.

        This enables finding the correct path for a hallucinated filename
        (e.g., ``UserRepository.cs`` might be at ``src/Identity.API/Data/...``).
        """
        self._source_file_index.clear()
        if not self._repo_root or not self._repo_root.exists():
            return
        src_dir = self._repo_root / "src"
        if not src_dir.exists():
            return
        skip = {"bin", "obj", "node_modules", ".vs", "packages", "wwwroot"}
        for path in src_dir.rglob("*.cs"):
            if any(part in skip for part in path.parts):
                continue
            rel = str(path.relative_to(self._repo_root)).replace("\\", "/")
            basename = path.name
            if basename not in self._source_file_index:
                self._source_file_index[basename] = rel
        logger.debug(
            "LinkResolver: indexed %d source files", len(self._source_file_index)
        )

    def _validate_github_url(self, url: str) -> str:
        """Validate a GitHub source URL against the actual filesystem.

        Returns the corrected URL, or empty string if the file cannot be found.
        """
        if not self._repo_root:
            return url

        # Try to extract a file path from GitHub blob URLs.
        m = _GITHUB_SOURCE_RE.search(url)
        if m:
            src_path = m.group(1)
        else:
            # Try broader pattern: /blob/branch/<any path ending in .cs>
            m2 = re.search(
                r'https?://github\.com/[^/]+/[^/]+/blob/[^/]+/([^#"\s)]+\.cs)',
                url,
            )
            if m2:
                src_path = m2.group(1)
            else:
                return url

        # Strip anchor fragment and query for filesystem check.
        clean_path = src_path.split("#")[0].split("?")[0]
        full_path = self._repo_root / clean_path
        if full_path.exists():
            return url

        # File doesn't exist. Try to find the correct path by basename.
        basename = Path(clean_path).name
        correct_rel = self._source_file_index.get(basename)
        if correct_rel:
            repo_url = self._repo_url or self._extract_repo_url(url)
            branch = self._extract_branch(url)
            anchor = ""
            if "#" in src_path:
                anchor = "#" + src_path.split("#", 1)[1]
            return f"{repo_url}/blob/{branch}/{correct_rel}{anchor}"

        logger.debug("Cannot find source file for: %s", src_path)
        return ""

    def _fix_placeholder_url(self, url: str) -> str:
        """Replace placeholder repository URLs with the configured one."""
        if not self._repo_url:
            return url
        placeholder_re = re.compile(
            r'https?://github\.com/(?:your-repo(?:-link)?|OWNER/REPO)/[^/]+'
        )
        if placeholder_re.search(url):
            m = re.match(
                r'https?://github\.com/[^/]+/[^/]+/(.*)', url
            )
            if m:
                return f"{self._repo_url}/{m.group(1)}"
        return url

    @staticmethod
    def _extract_repo_url(url: str) -> str:
        """Extract the repo base URL from a full GitHub URL."""
        m = re.match(r'(https?://github\.com/[^/]+/[^/]+)', url)
        return m.group(1) if m else ""

    @staticmethod
    def _extract_branch(url: str) -> str:
        """Extract the branch name from a GitHub blob URL."""
        m = re.match(r'https?://github\.com/[^/]+/[^/]+/blob/([^/]+)', url)
        return m.group(1) if m else "main"

    def _fix_github_urls_in_content(self, content: str) -> str:
        """Fix hallucinated GitHub URLs in both markdown and mermaid blocks."""
        # Fix placeholder URLs (your-repo, your-repo-link) by rebuilding
        # the entire URL with the correct repo base and validated path.
        if self._repo_url:
            def _fix_placeholder(m: re.Match) -> str:
                full_url = m.group(0)
                blob_match = re.search(r'/blob/([^/]+)/(.*)', full_url)
                if blob_match:
                    branch = blob_match.group(1)
                    file_path = blob_match.group(2)
                    rebuilt = f"{self._repo_url}/blob/{branch}/{file_path}"
                    return rebuilt
                # Simple format: github.com/your-repo/FileName.cs
                basename_match = re.search(r'/([^/]+\.cs(?:#.*)?)$', full_url)
                if basename_match:
                    raw = basename_match.group(1)
                    fname = raw.split("#")[0]
                    anchor = "#" + raw.split("#", 1)[1] if "#" in raw else ""
                    rel = self._source_file_index.get(fname)
                    if rel:
                        return f"{self._repo_url}/blob/main/{rel}{anchor}"
                    # File truly doesn't exist; mark for removal.
                    return "__INVALID_PLACEHOLDER__"
                return full_url

            content = re.sub(
                r'https?://github\.com/your-repo(?:-link)?/[^\s")\]]+',
                _fix_placeholder,
                content,
            )

        # Fix mermaid click directives with invalid source URLs.
        def _fix_mermaid_click(m: re.Match) -> str:
            prefix, url, suffix = m.group(1), m.group(2), m.group(3)
            if "__INVALID_PLACEHOLDER__" in url:
                return f"    %% Removed: invalid source link"
            fixed = self._validate_github_url(url)
            if not fixed:
                return f"    %% Removed: invalid source link"
            return f"{prefix}{fixed}{suffix}"

        content = _MERMAID_CLICK_RE.sub(_fix_mermaid_click, content)

        # Also catch any remaining __INVALID_PLACEHOLDER__ in mermaid
        # click lines that didn't match the regex above.
        content = re.sub(
            r'^\s*click\s+\w+[^\n]*__INVALID_PLACEHOLDER__[^\n]*$',
            lambda m: "    %% Removed: invalid source link",
            content,
            flags=re.MULTILINE,
        )

        # Fix markdown links pointing to GitHub source files.
        def _fix_md_github_link(m: re.Match) -> str:
            link_text, target = m.group(1), m.group(2)
            if "__INVALID_PLACEHOLDER__" in target:
                return link_text
            if not _GITHUB_SOURCE_RE.search(target):
                # Also check for broader github blob URLs.
                if not re.search(
                    r'https?://github\.com/[^/]+/[^/]+/blob/', target
                ):
                    return m.group(0)
            fixed = self._validate_github_url(target)
            if not fixed:
                return link_text
            if fixed != target:
                return f"[{link_text}]({fixed})"
            return m.group(0)

        content = _LINK_RE.sub(_fix_md_github_link, content)

        # Clean up any remaining placeholder markers.
        content = content.replace("__INVALID_PLACEHOLDER__", "")
        return content

    def _normalize_path_for_lookup(self, path: str) -> Optional[str]:
        """Check if path exists in generated files, with normalization."""
        path = path.replace('\\', '/')
        if path in self._generated:
            return path
        decoded = urllib.parse.unquote(path)
        if decoded in self._generated:
            return decoded
        deduplicated = re.sub(r'([^/]+)/\1/', r'\1/', path)
        if deduplicated != path and deduplicated in self._generated:
            return deduplicated
        base = Path(path).name
        for k in self._generated:
            if k.endswith('/' + base) or k == base:
                return k
        return None

    def _find_anchor_in_file(
        self, file_path: str, wanted_anchor: str, entity_hint: Optional[str] = None
    ) -> Optional[str]:
        """Find best matching anchor in a file."""
        anchors = self._file_to_anchors.get(file_path, [])
        wanted_lower = wanted_anchor.lower().replace('_', '')
        for slug, _ in anchors:
            if slug == wanted_anchor or slug == wanted_lower:
                return slug
            if wanted_lower in slug or slug in wanted_lower:
                return slug
        if entity_hint:
            for slug, raw in anchors:
                if entity_hint.lower() in raw.lower():
                    return slug
        return anchors[0][0] if anchors else None

    def _resolve_link(
        self, link_text: str, target: str, current_path: str
    ) -> Tuple[str, bool]:
        """Resolve a single link. Returns (resolved_target, was_modified)."""
        target = target.strip()
        if not target or target.startswith(('http://', 'https://')):
            return target, False

        if '#' in target:
            path_part, anchor_part = target.split('#', 1)
            path_part = path_part.strip()
            anchor_part = anchor_part.strip()
        else:
            path_part = target
            anchor_part = ""

        if anchor_part and re.match(r'^L\d+$', anchor_part):
            return link_text, True

        resolved_path = _resolve_path(current_path, path_part)
        if not resolved_path:
            return target, False

        normalized = self._normalize_path_for_lookup(resolved_path)
        if not normalized:
            for alias in _path_aliases(resolved_path):
                normalized = self._normalize_path_for_lookup(alias)
                if normalized:
                    break
        if not normalized:
            entity = (
                _guess_entity_from_link_text(link_text)
                or _guess_entity_from_anchor(anchor_part)
                or _guess_entity_from_path(resolved_path)
            )
            if entity and entity in self._entity_to_location:
                npath, nanchor = self._entity_to_location[entity]
                rel = self._relative_link(current_path, npath, nanchor)
                return rel, True
            if link_text and link_text in self._entity_to_location:
                npath, nanchor = self._entity_to_location[link_text]
                rel = self._relative_link(current_path, npath, nanchor)
                return rel, True
            return link_text, True

        anchors = self._file_to_anchors.get(normalized, [])
        if anchor_part:
            match = self._find_anchor_in_file(
                normalized, anchor_part, _guess_entity_from_anchor(anchor_part)
            )
            if match:
                rel = self._relative_link(current_path, normalized, match)
                return rel, True
            elif anchors:
                best = self._find_anchor_in_file(normalized, anchor_part, link_text)
                if best:
                    rel = self._relative_link(current_path, normalized, best)
                    return rel, True
        elif anchors:
            rel = self._relative_link(current_path, normalized, anchors[0][0])
            return rel, True

        rel = self._relative_link(current_path, normalized, "")
        return rel.rstrip('#'), True

    def _relative_link(self, from_path: str, to_path: str, anchor: str) -> str:
        """Compute relative link from from_path to to_path with anchor."""
        from_dir = Path(from_path).parent
        to_parts = Path(to_path).parts
        from_parts = from_dir.parts
        common = 0
        for a, b in zip(from_parts, to_parts):
            if a != b:
                break
            common += 1
        up = len(from_parts) - common
        rest = to_parts[common:]
        rel = Path("../" * up) / Path(*rest) if rest else Path("../" * up)
        result = str(rel).replace('\\', '/')
        if anchor:
            result += f"#{anchor}"
        return result

    def _process_content(self, content: str, current_path: str) -> str:
        """Process a single doc's content, repairing broken links."""
        parts = []
        last = 0
        in_block = False
        for m in _LINK_RE.finditer(content):
            before = content[last:m.start()]
            if not in_block:
                in_block = (_block_count(before) % 2) == 1
            if in_block:
                parts.append(content[last:m.end()])
                last = m.end()
                continue
            link_text, target = m.group(1), m.group(2)
            resolved, modified = self._resolve_link(link_text, target, current_path)
            parts.append(before)
            if modified and not resolved.startswith(('http://', 'https://')):
                if '#' in resolved or resolved.endswith('.md') or '.md#' in resolved:
                    parts.append(f"[{link_text}]({resolved})")
                else:
                    parts.append(link_text)
            else:
                parts.append(m.group(0))
            last = m.end()
        parts.append(content[last:])
        return "".join(parts)

    def resolve_all(self) -> Dict[str, str]:
        """Resolve all broken links across generated content.

        Returns:
            Updated dict with repaired content.
        """
        self._build_inventory()
        self._build_source_file_index()

        result = {}
        for rel_path, content in self._generated.items():
            # Fix GitHub source URLs (markdown + mermaid) first.
            content = self._fix_github_urls_in_content(content)
            # Then fix internal doc cross-links.
            content = self._process_content(content, rel_path)
            result[rel_path] = content
        return result


def _block_count(text: str) -> int:
    """Count ``` occurrences (code block delimiters)."""
    return len(re.findall(r'```', text))


def _path_aliases(broken_path: str) -> List[str]:
    """Return known alias paths for common hallucinations."""
    path = broken_path.replace('\\', '/')
    aliases = []
    if 'Data Interactions' in path or 'Data%20Interactions' in path:
        aliases.append(path.replace('Data Interactions.md', 'DataContext.md'))
        aliases.append(path.replace('Data%20Interactions.md', 'DataContext.md'))
    if 'ValueObject' in path:
        aliases.append(path.replace('ValueObject.md', 'Models.md'))
        aliases.append(path.replace('ValueObject.md', 'Aggregate.md'))
    if 'DomainEvent' in path:
        aliases.append(path.replace('DomainEvent.md', 'Models.md'))
    if 'Entities' in path:
        aliases.append(path.replace('Entities.md', 'Aggregate.md'))
        aliases.append(path.replace('Entities.md', 'Models.md'))
    if 'BaseDomainDefinition' in path:
        aliases.append(path.replace('BaseDomainDefinition.md', 'Models.md'))
    if 'DataInteraction' in path:
        aliases.append(path.replace('DataInteraction.md', 'Repositories.md'))
    if 'eShop.' in path:
        aliases.append(re.sub(r'\.\./eShop\.\w+\.API/', '../', path))
    return aliases


def _guess_entity_from_link_text(text: str) -> Optional[str]:
    """Use link text as entity name if it looks like a class/method."""
    if not text or len(text) < 2:
        return None
    if re.match(r'^[A-Za-z][\w.]*$', text):
        return text
    return None


def _guess_entity_from_anchor(anchor: str) -> Optional[str]:
    """Extract entity name from anchor slug for lookup."""
    if not anchor or anchor.startswith('L') and anchor[1:].isdigit():
        return None
    clean = re.sub(r'[-_\d]+', '', anchor)
    if len(clean) >= 3:
        return clean
    return None


def _guess_entity_from_path(path: str) -> Optional[str]:
    """Extract entity hint from path (e.g., filename without extension)."""
    name = Path(path).stem
    if name and name not in ('index', 'README'):
        return name
    return None
