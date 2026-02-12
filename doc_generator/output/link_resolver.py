"""Post-generation link resolver for generated documentation.

Design decision: The LLM generates cross-page links without awareness of
the actual file inventory or MkDocs anchor slugification. This module
runs after all docs are generated and before writing to disk. It builds
a deterministic inventory of files and headings, then repairs broken
internal links by redirecting to correct targets or stripping invalid links.
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

    def __init__(self, generated: Dict[str, str]):
        """Initialise with the generated content dict.

        Args:
            generated: Dict mapping relative doc paths to markdown content.
        """
        self._generated = generated
        self._file_to_anchors: Dict[str, List[Tuple[str, str]]] = {}
        self._entity_to_location: Dict[str, Tuple[str, str]] = {}

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
        result = {}
        for rel_path, content in self._generated.items():
            result[rel_path] = self._process_content(content, rel_path)
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
