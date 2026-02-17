"""Document assembler for writing generated content to disk.

Design decision: The assembler is the final stage of the pipeline. It
receives a dict of ``{relative_path: markdown_content}`` from the
orchestrator and:
  1. Writes each file to the configured docs output directory.
  2. Resolves cross-reference placeholders to relative links.
  3. Delegates mkdocs.yml navigation updates to NavigationBuilder.

All output paths come from project_config.yml, so the assembler has
zero hardcoded paths.
"""

import logging
import re
from pathlib import Path
from typing import Dict, List, Tuple

from ..config import ConfigLoader
from .link_resolver import LinkResolver
from .navigation import NavigationBuilder

logger = logging.getLogger(__name__)


class DocumentAssembler:
    """Writes generated documentation to disk and updates mkdocs.yml.

    Design decision: Cross-reference resolution uses a simple dict lookup
    rather than a separate resolver class. The dict is built as files are
    processed -- each class heading becomes an entry mapping
    ``ClassName -> (doc_path, anchor)``. Placeholders in the form
    ``{ref:ClassName}`` are replaced with ``[ClassName](relative/path#anchor)``.
    """

    def __init__(self, config: ConfigLoader):
        """Initialise with validated configuration.

        Args:
            config: Loaded ConfigLoader instance.
        """
        self.config = config
        self._nav_builder = NavigationBuilder(config)
        self._ref_map: Dict[str, Tuple[str, str]] = {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def clean_api_output(self, api_key: str, generated: Dict[str, str]) -> None:
        """Remove previously generated files for an API before writing new ones.

        Design decision: Only removes directories that will be regenerated
        (based on the top-level folders in the generated dict). Does NOT
        remove ``index.md`` or other hand-crafted files.

        Args:
            api_key: API identifier (for logging).
            generated: The dict of files about to be written.
        """
        import shutil

        docs_dir = self.config.output_docs_dir
        # Collect top-level folders that will be regenerated.
        folders_to_clean: set = set()
        files_to_clean: List[Path] = []
        for rel_path in generated:
            parts = Path(rel_path).parts
            if len(parts) >= 2:
                folders_to_clean.add(parts[0])
            elif len(parts) == 1 and parts[0] != "index.md":
                files_to_clean.append(docs_dir / parts[0])

        for folder in folders_to_clean:
            target = docs_dir / folder
            if target.exists() and target.is_dir():
                shutil.rmtree(target)
                logger.info("Cleaned %s", target)

        for f in files_to_clean:
            if f.exists():
                f.unlink()
                logger.info("Cleaned %s", f)

        logger.info("Clean complete for API '%s'", api_key)

    def assemble(self, generated: Dict[str, str]) -> List[Path]:
        """Write all generated files and update mkdocs.yml.

        Args:
            generated: Dict mapping relative output paths (e.g.
                ``"Ordering.API/Commands.md"``) to markdown content.

        Returns:
            List of absolute paths to the written files.
        """
        docs_dir = self.config.output_docs_dir
        docs_dir.mkdir(parents=True, exist_ok=True)

        # First pass: build the cross-reference map.
        self._build_ref_map(generated)

        # Link resolution: repair broken internal links before writing.
        resolver = LinkResolver(
            generated,
            repo_root=self.config.project_root,
            repo_url=self.config.repo_url,
        )
        generated = resolver.resolve_all()

        # Second pass: resolve refs and write files.
        written: List[Path] = []
        for rel_path, content in generated.items():
            content = self._resolve_refs(content, rel_path)
            full_path = docs_dir / rel_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content, encoding="utf-8")
            written.append(full_path)
            logger.info("Wrote %s", full_path)

        # Update mkdocs navigation.
        self._nav_builder.update_mkdocs_nav(list(generated.keys()))

        logger.info("Assembly complete: %d files written", len(written))
        return written

    # ------------------------------------------------------------------
    # Cross-reference resolution
    # ------------------------------------------------------------------

    def _build_ref_map(self, generated: Dict[str, str]) -> None:
        """Scan generated content for class headings and build a ref map."""
        self._ref_map.clear()
        heading_re = re.compile(r'^##\s+\[?(\w+)\]?', re.MULTILINE)
        for rel_path, content in generated.items():
            for m in heading_re.finditer(content):
                name = m.group(1)
                anchor = self._to_anchor(name)
                if name not in self._ref_map:
                    self._ref_map[name] = (rel_path, anchor)

        logger.debug("Built ref map with %d entries", len(self._ref_map))

    def _resolve_refs(self, content: str, current_path: str) -> str:
        """Replace ``{ref:ClassName}`` placeholders with markdown links."""

        def _replacer(match: re.Match) -> str:
            name = match.group(1)
            if name in self._ref_map:
                target_path, anchor = self._ref_map[name]
                rel_link = self._relative_link(current_path, target_path, anchor)
                return f"[{name}]({rel_link})"
            logger.debug("Unresolved ref: %s", name)
            return name

        return re.sub(r'\{ref:(\w+(?:\.\w+)?)\}', _replacer, content)

    @staticmethod
    def _to_anchor(name: str) -> str:
        """Convert a class/section name to a markdown anchor slug."""
        return name.lower().replace(" ", "-").replace(".", "")

    @staticmethod
    def _relative_link(from_path: str, to_path: str, anchor: str) -> str:
        """Compute a relative link between two doc pages."""
        from_parts = Path(from_path).parent.parts

        try:
            rel = Path(to_path).relative_to(Path(from_path).parent)
            return f"{rel}#{anchor}"
        except ValueError:
            up_count = len(from_parts)
            rel = "../" * up_count + to_path
            return f"{rel}#{anchor}"
