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
    content = _fix_inline_closing_fences(content)
    content = _strip_absolute_local_paths(content)

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


def build_class_map(
    source_root: str,
    repo_url: str,
    branch: str = "main",
) -> dict:
    """Build a mapping from lowercase class/interface names to GitHub URLs.

    Scans all ``.cs`` files under *source_root* and returns a dict
    ``{class_name_lower: github_blob_url}``.  This map is used by
    :func:`fix_click_links_to_github` and :func:`fix_sequence_legends`.
    """
    class_to_github: dict = {}
    abs_source = os.path.abspath(source_root)
    repo_root = os.path.dirname(abs_source)

    for root, _dirs, files in os.walk(source_root):
        for fname in files:
            if not fname.endswith(".cs"):
                continue
            fpath = os.path.join(root, fname)
            rel_fpath = os.path.relpath(fpath, repo_root)
            github = f"{repo_url}/blob/{branch}/{rel_fpath}"
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
    return class_to_github


def fix_click_links_to_github(
    content: str,
    source_root: str,
    repo_url: str,
    branch: str = "main",
    class_to_github: Optional[dict] = None,
) -> str:
    """Replace non-GitHub ``click`` URLs with GitHub source links and
    append ``#Lxx`` line-number anchors for precise navigation.

    Scans all Mermaid blocks for ``click`` and ``link`` directives.
    For non-HTTP URLs, extracts the class name from the tooltip, looks
    up the corresponding ``.cs`` file under *source_root*, and rewrites
    the URL to a GitHub blob link.  For URLs already pointing to the
    repository, appends or corrects the ``#Lxx`` fragment so clicking
    a diagram node jumps directly to the relevant line of code.

    Directives that cannot be mapped are commented out so they don't
    produce broken links.

    This function is idempotent and safe to call on every build.
    """
    if class_to_github is None:
        class_to_github = build_class_map(source_root, repo_url, branch)

    line_index: dict = {}  # (file_path, symbol_name) -> line_number
    github_base = f"{repo_url}/blob/{branch}/"

    abs_source = os.path.abspath(source_root)
    repo_root = os.path.dirname(abs_source)

    for root, _dirs, files in os.walk(source_root):
        for fname in files:
            if not fname.endswith(".cs"):
                continue
            fpath = os.path.join(root, fname)
            rel_fpath = os.path.relpath(fpath, repo_root)

            try:
                with open(fpath, "r", encoding="utf-8", errors="ignore") as fh:
                    src_lines = fh.readlines()
            except OSError:
                continue

            for i, line in enumerate(src_lines, 1):
                stripped = line.strip()
                cm = re.match(
                    r"(?:public\s+)?(?:abstract\s+)?(?:sealed\s+)?(?:partial\s+)?"
                    r"(?:class|record|struct|interface)\s+(\w+)",
                    stripped,
                )
                if cm:
                    line_index[(rel_fpath, cm.group(1))] = i

                cm = re.match(
                    r"(?:public|protected|private|internal)\s+"
                    r"(?:static\s+)?(?:async\s+)?(?:override\s+)?(?:virtual\s+)?"
                    r"[\w<>\[\],\s]+?\s+(\w+)\s*\(",
                    stripped,
                )
                if cm:
                    mname = cm.group(1)
                    if mname not in (
                        "if", "for", "while", "switch", "catch",
                        "using", "return", "throw", "new", "get", "set",
                    ):
                        line_index[(rel_fpath, mname)] = i

                cm = re.match(
                    r"(?:public|protected|private|internal)\s+"
                    r"(\w+)\s*\(",
                    stripped,
                )
                if cm and (rel_fpath, cm.group(1)) in line_index:
                    line_index[(rel_fpath, f"{cm.group(1)}_ctor")] = i

    def _find_line(file_path: str, tooltip: str) -> Optional[int]:
        """Look up the source line for a tooltip label in *file_path*.

        Tries, in order: exact method name (last part), then
        intermediate property names (middle parts only, skipping the
        first part which is typically the class name — matching it
        would just land on the class declaration, not the property).
        """
        clean = tooltip.strip()
        search_names: list = []
        if " constructor" in clean:
            cn = clean.replace(" constructor", "").replace(" (constructor)", "").split(".")[-1]
            search_names = [f"{cn}_ctor", cn]
        elif "." in clean:
            parts = clean.split(".")
            search_names = [parts[-1]]
            if len(parts) >= 3:
                for p in reversed(parts[1:-1]):
                    search_names.append(p)
        else:
            search_names = [clean]
        for name in search_names:
            key = (file_path, name)
            if key in line_index:
                return line_index[key]
        return None

    def _append_line_anchor(github_url: str, tooltip: str) -> str:
        """Append ``#Lxx`` to *github_url* if the symbol can be found."""
        url_no_fragment = github_url.split("#")[0]
        file_path = url_no_fragment.replace(github_base, "")
        line_num = _find_line(file_path, tooltip)
        if line_num is not None:
            return f"{url_no_fragment}#L{line_num}"
        if "#L" in github_url:
            return url_no_fragment
        return github_url

    _CLICK_URL_RE = re.compile(
        r'^(\s*click\s+\w+\s+href\s+)"([^"]+)"\s+"([^"]+)"\s*$',
        re.MULTILINE,
    )
    _LINK_URL_RE = re.compile(
        r'^(\s*link\s+(\w+)\s+)"([^"]+)"\s+"([^"]+)"\s*$',
        re.MULTILINE,
    )

    _NODE_LABEL_RE = re.compile(
        r"\b(\w+)\s*\(\[\s*(.+?)\s*\]\)",
    )

    def _fix_block(match: re.Match) -> str:
        prefix = match.group(1)
        body = match.group(2)
        suffix = match.group(3)

        def _normalize_github_url(url: str) -> str:
            """Strip embedded absolute local paths from a GitHub URL."""
            m = re.search(r'/blob/[^/]+//', url)
            if m:
                idx = m.end()
                abs_prefix = url[idx:]
                prefix_match = re.match(r'.*/src/', abs_prefix)
                if prefix_match:
                    url = url[:m.end() - 1] + 'src/' + abs_prefix[prefix_match.end():]
            return url

        def _rewrite_click(cm: re.Match) -> str:
            before, url, tooltip = cm.group(1), cm.group(2), cm.group(3)
            if url.startswith("http"):
                if url.startswith(github_base) or url.startswith(repo_url):
                    url = _normalize_github_url(url)
                    url = _append_line_anchor(url, tooltip)
                return f'{before}"{url}" "{tooltip}"'
            cls = tooltip.replace(" constructor", "").split(".")[0].strip().lower()
            gh = class_to_github.get(cls)
            if gh:
                gh = _append_line_anchor(gh, tooltip)
                return f'{before}"{gh}" "{tooltip}"'
            return f"    %% Removed: no GitHub source for {tooltip}"

        def _rewrite_link(cm: re.Match) -> str:
            before, node_name, url, tooltip = (
                cm.group(1), cm.group(2), cm.group(3), cm.group(4),
            )
            if url.startswith("http"):
                if url.startswith(github_base) or url.startswith(repo_url):
                    url = _normalize_github_url(url)
                    url = _append_line_anchor(url, tooltip)
                return f'{before}"{url}" "{tooltip}"'
            cls = node_name.lower()
            gh = class_to_github.get(cls)
            if not gh:
                cls = tooltip.replace("View ", "").replace(" source", "").replace(" documentation", "").split(".")[0].strip().lower()
                gh = class_to_github.get(cls)
            if gh:
                gh = _append_line_anchor(gh, tooltip)
                return f'{before}"{gh}" "{tooltip}"'
            return f"    %% Removed: no GitHub source for {node_name}"

        body = _CLICK_URL_RE.sub(_rewrite_click, body)
        body = _LINK_URL_RE.sub(_rewrite_link, body)

        first_line = body.strip().split("\n")[0].strip().lower()
        is_flowchart = first_line.startswith("flowchart") or first_line.startswith("graph")
        if is_flowchart:
            existing_click_nodes: set = set()
            for cm in re.finditer(r"^\s*click\s+(\w+)\s", body, re.MULTILINE):
                existing_click_nodes.add(cm.group(1))

            injected: list = []
            for nm in _NODE_LABEL_RE.finditer(body):
                node_id = nm.group(1)
                label = nm.group(2).strip()
                if node_id in existing_click_nodes:
                    continue
                clean_label = label.replace(" constructor", "").replace(" (constructor)", "")
                cls_name = clean_label.split(".")[0].strip().lower()
                gh = class_to_github.get(cls_name)
                if not gh:
                    cls_name = clean_label.split()[0].strip().lower()
                    gh = class_to_github.get(cls_name)
                if not gh:
                    parts = clean_label.split(".")
                    if len(parts) > 1:
                        cls_name = parts[0].strip().lower()
                        gh = class_to_github.get(cls_name)
                if gh:
                    gh = _append_line_anchor(gh, label)
                    injected.append(
                        f'    click {node_id} href "{gh}" "{label}"'
                    )

            if injected:
                body = body.rstrip() + "\n" + "\n".join(injected) + "\n"

        return prefix + body + suffix

    result = _MERMAID_BLOCK_RE.sub(_fix_block, content)
    result = _fix_inline_closing_fences(result)
    return result


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


def _fix_inline_closing_fences(content: str) -> str:
    """Move closing ``` from end-of-content lines to their own line.

    LLMs sometimes generate ``click A href "url" "tip"``` with the
    closing fence glued to the last line.  The markdown parser needs
    the fence on its own line to recognise the code block.
    """
    return re.sub(r'^(.+[^`])```\s*$', r'\1\n```', content, flags=re.MULTILINE)


def fix_table_formatting(content: str) -> str:
    """Ensure markdown tables are preceded by a blank line.

    Python-Markdown (used by MkDocs) requires a blank line before a
    pipe table.  Without it, the table rows are rendered as inline text
    in the preceding paragraph.  This function inserts the blank line
    where it's missing.
    """
    lines = content.split("\n")
    result: list = []
    for i, line in enumerate(lines):
        if i > 0 and re.match(r"^\|[\s\w]", line):
            prev = lines[i - 1].strip()
            if prev and not prev.startswith("|") and not prev.startswith("---"):
                result.append("")
        result.append(line)
    return "\n".join(result)


def fix_sequence_legends(content: str, class_to_github: dict) -> str:
    """Reformat ``??? Sequence Diagram Legend`` blocks for MkDocs.

    The LLM often generates legend content as unindented numbered lists::

        ??? Sequence Diagram Legend
        1. **Client** sends a request.
        2. **OrdersApi** forwards the command.

    ``pymdownx.details`` requires 4-space indentation for content inside
    a ``???`` block.  This function converts unindented numbered items to
    properly indented bullet lists and adds clickable GitHub links for
    component names that exist in *class_to_github*.

    Already-formatted blocks (4-space indented bullets) are left
    untouched, making the function idempotent.
    """
    _LEGEND_HEADER = "??? Sequence Diagram Legend"
    _NUM_RE = re.compile(
        r"^(\d+)\.\s+(.+)$"
    )
    _BOLD_RE = re.compile(r"\*\*(.+?)\*\*")

    lines = content.split("\n")
    result: list = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.strip() == _LEGEND_HEADER:
            result.append(line)
            i += 1
            if i < len(lines) and lines[i].startswith("    "):
                continue
            while i < len(lines):
                raw = lines[i]
                m = _NUM_RE.match(raw.strip())
                if not m:
                    if raw.strip() == "" or raw.strip().startswith("-"):
                        break
                    result.append(raw)
                    i += 1
                    continue
                num, body = m.group(1), m.group(2)
                bold_m = _BOLD_RE.search(body)
                if not bold_m:
                    result.append(f"    - **{num}.** {body}")
                    i += 1
                    continue
                component = bold_m.group(1)
                rest = body[bold_m.end():].lstrip(" ,.:-").strip()
                clean_name = component.replace("The ", "").strip()
                cls_key = clean_name.lower()
                gh = class_to_github.get(cls_key)
                if not gh:
                    parts = clean_name.split()
                    if parts:
                        gh = class_to_github.get(parts[0].lower())
                if gh:
                    entry = (
                        f"    - **{num}. {component}** -- "
                        f"[{clean_name}]({gh}) -- {rest}"
                    )
                else:
                    entry = f"    - **{num}. {component}** -- {rest}"
                result.append(entry)
                i += 1
        else:
            result.append(line)
            i += 1
    return "\n".join(result)


def _strip_absolute_local_paths(content: str) -> str:
    """Remove absolute local filesystem paths from GitHub URLs.

    LLMs occasionally produce URLs like
    ``https://github.com/org/repo/blob/main//Users/me/proj/src/...``
    which should be ``https://github.com/org/repo/blob/main/src/...``.
    """
    return re.sub(r'/Users/[^"]*?/automated-doc-poc-repo/', '', content)
