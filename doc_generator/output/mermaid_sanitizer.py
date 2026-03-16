"""Post-generation mermaid diagram sanitizer.

Deterministic post-processor that validates and repairs common LLM-generated
mermaid syntax errors.  Applied after every LLM call, before writing to disk.

This module does NOT rely on the LLM -- all fixes are regex-based, so they
are guaranteed to execute regardless of model behaviour.
"""

import os
import re
import logging
from typing import Optional, Set

logger = logging.getLogger(__name__)

_MERMAID_BLOCK_RE = re.compile(
    r"(```mermaid\s*\n)(.*?)(```)", re.DOTALL
)

_BLOCK_KEYWORDS = {"alt", "opt", "rect", "loop", "par", "critical", "break"}


def sanitize_mermaid_blocks(
    content: str,
    repo_url: Optional[str] = None,
) -> str:
    """Find every mermaid code block in *content* and repair known issues.

    Args:
        content: Full markdown string (may contain zero or more mermaid blocks).
        repo_url: Configured repository URL.  ``click`` directives pointing
            to a different GitHub repo are commented out.

    Returns:
        The markdown with all mermaid blocks sanitized.
    """

    def _fix_block(match: re.Match) -> str:
        prefix = match.group(1)
        body = match.group(2)
        suffix = match.group(3)

        body = _fix_graph_keyword(body)
        body = _fix_class_diagram_braces(body)
        body = _fix_unbalanced_braces(body)
        body = _fix_missing_end_keywords(body)
        body = _fix_click_href_keyword(body)
        body = _fix_click_directives(body, repo_url)
        body = _fix_broken_link_directives(body)
        body = _strip_style_directives(body)
        body = _fix_special_chars_in_labels(body)
        body = _escape_html_angles(body)

        return prefix + body + suffix

    content = _close_unclosed_mermaid_fences(content)
    result = _MERMAID_BLOCK_RE.sub(_fix_block, content)
    return result


def fix_click_links_to_github(
    content: str,
    source_root: str,
    repo_url: str,
    branch: str = "main",
) -> str:
    """Replace non-GitHub ``click`` URLs with GitHub source links.

    Scans all Mermaid blocks for ``click`` directives whose URL is a
    local anchor (``#...``) or relative doc path (``../../...``).  For
    each, extracts the class name from the tooltip, looks up the
    corresponding ``.cs`` file under *source_root*, and rewrites the
    URL to a GitHub blob link.  Directives that cannot be mapped are
    commented out so they don't produce broken links.

    This function is idempotent and safe to call on every build.
    """
    class_to_github: dict = {}
    for root, _dirs, files in os.walk(source_root):
        for fname in files:
            if not fname.endswith(".cs"):
                continue
            fpath = os.path.join(root, fname)
            github = f"{repo_url}/blob/{branch}/{fpath}"
            try:
                with open(fpath, "r", encoding="utf-8", errors="ignore") as fh:
                    src = fh.read()
            except OSError:
                continue
            for m in re.finditer(r"\b(?:class|interface|record|struct)\s+(\w+)", src):
                class_to_github[m.group(1).lower()] = github
            stem = fname.replace(".cs", "").lower()
            if stem not in class_to_github:
                class_to_github[stem] = github

    _CLICK_URL_RE = re.compile(
        r'^(\s*click\s+\w+\s+href\s+)"([^"]+)"\s+"([^"]+)"\s*$',
        re.MULTILINE,
    )

    def _fix_block(match: re.Match) -> str:
        prefix = match.group(1)
        body = match.group(2)
        suffix = match.group(3)

        def _rewrite(cm: re.Match) -> str:
            before, url, tooltip = cm.group(1), cm.group(2), cm.group(3)
            if url.startswith("http"):
                return cm.group(0)
            cls = tooltip.replace(" constructor", "").split(".")[0].strip().lower()
            gh = class_to_github.get(cls)
            if gh:
                return f'{before}"{gh}" "{tooltip}"'
            return f"    %% Removed: no GitHub source for {tooltip}"

        body = _CLICK_URL_RE.sub(_rewrite, body)
        return prefix + body + suffix

    return _MERMAID_BLOCK_RE.sub(_fix_block, content)


def fix_mermaid_links_for_mkdocs(
    content: str,
    docs_root: str,
    page_rel_path: str,
) -> str:
    """Post-process Mermaid link/click directives for MkDocs compatibility.

    MkDocs ``use_directory_urls`` turns ``Foo.md`` into ``Foo/index.html``
    served at ``Foo/``.  This adds one URL directory level that breaks
    relative ``.md`` paths inside Mermaid diagrams.  This function:

    1. Validates each relative ``.md`` target against *docs_root*.
    2. For valid targets: prepends ``../`` and replaces ``.md`` with ``/``
       so the browser-relative URL matches the MkDocs directory layout.
    3. For hallucinated targets (file not found): comments out the directive.

    Args:
        content: Full markdown string.
        docs_root: Absolute path to the ``docs/`` folder (e.g. ``src/docs/docs``).
        page_rel_path: Path of the current page relative to *docs_root*
            (e.g. ``Ordering.API/OrdersApi/OrderCreation.md``).
    """
    page_dir = os.path.dirname(page_rel_path)

    existing_files: Set[str] = set()
    for root, _dirs, files in os.walk(docs_root):
        for f in files:
            rel = os.path.relpath(os.path.join(root, f), docs_root)
            existing_files.add(os.path.normpath(rel))

    def _fix_link_in_block(match: re.Match) -> str:
        prefix = match.group(1)
        body = match.group(2)
        suffix = match.group(3)

        body = _transform_relative_links(body, page_dir, existing_files)
        return prefix + body + suffix

    return _MERMAID_BLOCK_RE.sub(_fix_link_in_block, content)


def _transform_relative_links(
    body: str,
    page_dir: str,
    existing_files: Set[str],
) -> str:
    """Transform or remove relative .md links inside a single Mermaid block."""
    _LINK_RE = re.compile(
        r'^(\s*(?:click|link)\s+\w+\s+)"(\.\.?/[^"]*\.md[^"]*)"(.*)$',
        re.MULTILINE,
    )

    def _replace(m: re.Match) -> str:
        before = m.group(1)
        url = m.group(2)
        after = m.group(3)

        anchor = ""
        path_part = url
        if "#" in url:
            path_part, anchor = url.rsplit("#", 1)
            anchor = "#" + anchor

        decoded = path_part.replace("%20", " ")
        resolved = os.path.normpath(os.path.join(page_dir, decoded))

        if resolved in existing_files:
            new_path = "../" + path_part.replace(".md", "/")
            return f'{before}"{new_path}{anchor}"{after}'
        else:
            node_match = re.match(r'\s*(?:click|link)\s+(\w+)', m.group(0))
            node = node_match.group(1) if node_match else "?"
            logger.debug("Removing hallucinated Mermaid link: %s -> %s", node, url)
            return f"    %% Removed: hallucinated link ({url})"

    return _LINK_RE.sub(_replace, body)


def _close_unclosed_mermaid_fences(content: str) -> str:
    """Detect ``mermaid`` code fences that were never closed and close them.

    This happens when an LLM output is truncated mid-diagram or when chunk
    concatenation leaves an orphan opening fence.  Without the closing
    fence the regex-based sanitizer cannot match the block.
    """
    lines = content.split("\n")
    result: list = []
    in_mermaid = False
    in_other_fence = False

    for line in lines:
        stripped = line.strip()

        if not in_mermaid and not in_other_fence:
            if stripped.startswith("```mermaid"):
                in_mermaid = True
                result.append(line)
                continue
            elif stripped.startswith("```") and len(stripped) > 3:
                in_other_fence = True
                result.append(line)
                continue
        elif in_mermaid:
            if stripped == "```":
                in_mermaid = False
                result.append(line)
                continue
            if stripped == "---":
                result.append("```")
                in_mermaid = False
                result.append(line)
                continue
            result.append(line)
            continue
        elif in_other_fence:
            if stripped.startswith("```"):
                in_other_fence = False
            result.append(line)
            continue

        result.append(line)

    if in_mermaid:
        result.append("```")

    return "\n".join(result)


def _fix_graph_keyword(body: str) -> str:
    """Replace ``graph LR/TD/TB/RL/BT`` with ``flowchart`` equivalent."""
    return re.sub(
        r"^(\s*)graph\s+(LR|TD|TB|RL|BT)\b",
        r"\1flowchart \2",
        body,
        count=1,
        flags=re.MULTILINE,
    )


def _fix_class_diagram_braces(body: str) -> str:
    """Fix ``class Foo {}`` pattern where members are listed outside the class body.

    LLMs frequently generate::

        class OrdersApi {}
            +MethodA()
            +MethodB()
        }

    The correct syntax is ``class OrdersApi {`` (opening only), members
    inside, then ``}``.  This function detects the pattern and removes
    the premature ``}`` from the class declaration line.
    """
    first_line = body.strip().split("\n", 1)[0].strip().lower()
    if "classdiagram" not in first_line.replace(" ", ""):
        return body

    return re.sub(
        r"^(\s*class\s+\w+\s*)\{\}",
        r"\1{",
        body,
        flags=re.MULTILINE,
    )


def _fix_unbalanced_braces(body: str) -> str:
    """Ensure decision-node braces ``{ }`` are balanced on each line.

    Mermaid decision nodes use ``{text}`` syntax.  If the LLM forgets a
    closing brace the diagram fails to render.  We only fix lines that
    look like node definitions (contain ``{`` but no matching ``}``).

    Lines starting with ``class `` in class diagrams are skipped because
    they intentionally have an opening ``{`` that is closed on a later line.
    """
    first_line = body.strip().split("\n", 1)[0].strip().lower()
    is_class_diagram = "classdiagram" in first_line.replace(" ", "")

    lines = body.split("\n")
    fixed = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith(("%%", "click", "link", "style", "classDef")):
            fixed.append(line)
            continue
        if is_class_diagram and re.match(r"^\s*class\s+\w+", stripped):
            fixed.append(line)
            continue
        open_count = stripped.count("{")
        close_count = stripped.count("}")
        if open_count > close_count:
            line = line + "}" * (open_count - close_count)
        fixed.append(line)
    return "\n".join(fixed)


def _fix_missing_end_keywords(body: str) -> str:
    """Append missing ``end`` keywords for sequence-diagram block constructs.

    Sequence diagrams use ``alt``, ``opt``, ``rect``, ``loop``, ``par``,
    ``critical``, and ``break`` which all require a closing ``end``.
    """
    first_line = body.strip().split("\n", 1)[0].strip().lower()
    if "sequencediagram" not in first_line.replace(" ", ""):
        return body

    lines = body.split("\n")
    depth = 0
    for line in lines:
        stripped = line.strip().lower()
        token = stripped.split()[0] if stripped.split() else ""
        if token in _BLOCK_KEYWORDS:
            depth += 1
        elif token == "end":
            depth -= 1

    if depth > 0:
        for _ in range(depth):
            lines.append("    end")
    return "\n".join(lines)


def _fix_click_href_keyword(body: str) -> str:
    """Ensure ``click`` directives use the ``href`` keyword for URL navigation.

    Mermaid 10.x requires ``click nodeId href "URL" "tooltip"`` for links.
    Without ``href``, Mermaid interprets the URL as a JavaScript callback
    name, making the node non-clickable.
    """
    return re.sub(
        r'^(\s*click\s+\w+)\s+"([^"]+)"\s+"([^"]+)"\s*$',
        r'\1 href "\2" "\3"',
        body,
        flags=re.MULTILINE,
    )


def _fix_click_directives(body: str, repo_url: Optional[str]) -> str:
    """Comment out ``click`` directives whose URL is hallucinated."""
    if not repo_url:
        return body

    def _check_click(match: re.Match) -> str:
        full_line = match.group(0)
        url_match = re.search(r'https?://[^\s"\']+', full_line)
        if not url_match:
            return full_line
        url = url_match.group(0).rstrip('"').rstrip("'")
        if "github.com" in url and not url.startswith(repo_url):
            return f"    %% Removed: hallucinated click URL"
        return full_line

    return re.sub(
        r"^\s*click\s+.+$",
        _check_click,
        body,
        flags=re.MULTILINE,
    )


def _fix_broken_link_directives(body: str) -> str:
    """Comment out ``link`` directives whose target path doesn't look valid.

    LLMs often hallucinate paths like ``../Queries/IOrderQueries.md`` that
    don't exist. We detect link targets that reference non-existent subdirs
    and comment them out.
    """
    first_line = body.strip().split("\n", 1)[0].strip().lower()
    if "classdiagram" not in first_line.replace(" ", ""):
        return body

    def _check_link(m: re.Match) -> str:
        full_line = m.group(0)
        url_match = re.search(r'"([^"]+)"', full_line)
        if not url_match:
            return full_line
        target = url_match.group(1)
        if target.startswith(("http://", "https://")):
            return full_line
        parts = target.replace("\\", "/").split("/")
        leaf = parts[-1] if parts else ""
        if not leaf.endswith(".md"):
            return full_line
        stem = leaf.replace(".md", "")
        if any(ch.isupper() for ch in stem) and "/" in target:
            deeper = [p for p in parts if p not in (".", "..")]
            if len(deeper) >= 2:
                logger.debug("Commenting out suspicious link: %s", full_line.strip())
                return f"    %% Removed: broken link directive ({target})"
        return full_line

    return re.sub(
        r"^\s*link\s+\w+\s+.+$",
        _check_link,
        body,
        flags=re.MULTILINE,
    )


def _escape_html_angles(body: str) -> str:
    """Escape ``<Text>`` patterns that Mermaid ``loose`` mode would treat as HTML.

    With ``securityLevel: loose`` Mermaid allows HTML in labels.  C# generics
    like ``IEnumerable<OrderSummary>`` get eaten *in flowchart node labels*
    (rendered via ``<foreignObject>`` with embedded HTML).

    Sequence diagrams render message text in SVG ``<text>`` elements which
    do NOT interpret HTML, so escaping ``<`` to ``&lt;`` there actually
    *breaks* the Mermaid parser.  We therefore skip sequence diagrams.

    Class diagram stereotypes (``<<interface>>``) are also preserved.
    """
    first_line = body.strip().split("\n", 1)[0].strip().lower()
    is_class_diagram = "classdiagram" in first_line.replace(" ", "")
    is_sequence_diagram = "sequencediagram" in first_line.replace(" ", "")

    if is_sequence_diagram:
        return body

    lines = body.split("\n")
    fixed = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith(("%%", "click ", "link ", "classDef")):
            fixed.append(line)
            continue

        if is_class_diagram and re.search(r"<<\w+>>", line):
            fixed.append(line)
            continue

        if re.search(r"<\w+>", line) and not stripped.startswith(("click ", "link ")):
            line = re.sub(
                r"(?<!<)<(\w[\w.]*?)>(?!>)",
                r"&lt;\1&gt;",
                line,
            )
        fixed.append(line)
    return "\n".join(fixed)


def _strip_style_directives(body: str) -> str:
    """Remove explicit ``style`` and ``classDef`` lines (break in dark mode)."""
    return re.sub(
        r"^\s*(style\s+|classDef\s+|:::).+$",
        "",
        body,
        flags=re.MULTILINE,
    )


def _fix_special_chars_in_labels(body: str) -> str:
    r"""Wrap node labels containing problematic characters in quotes.

    Mermaid chokes on unquoted ``()``, ``[]``, ``<>`` inside node labels
    that use the ``[label]`` form.  We selectively quote those.
    """
    def _quote_label(m: re.Match) -> str:
        node_id = m.group(1)
        bracket = m.group(2)
        label = m.group(3)
        close = m.group(4)
        if label.startswith('"') and label.endswith('"'):
            return m.group(0)
        needs_quoting = any(ch in label for ch in "<>")
        if needs_quoting:
            label = f'"{label}"'
        return f"{node_id}{bracket}{label}{close}"

    return re.sub(
        r"(\w+)(\[)([^\]]+?)(\])",
        _quote_label,
        body,
    )
