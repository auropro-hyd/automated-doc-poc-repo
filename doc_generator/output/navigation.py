"""MkDocs navigation builder.

Design decision: Navigation generation is separated from the file-writing
assembler because it is a self-contained transformation (flat file list ->
hierarchical nav tree) with its own YAML I/O. Keeping it in its own module
makes the assembler shorter and lets the nav logic be tested or reused
independently.
"""

import re
import logging
from collections import defaultdict
from pathlib import Path
from typing import Dict, List

import yaml

from ..config import ConfigLoader

logger = logging.getLogger(__name__)


class NavigationBuilder:
    """Generates and updates the ``nav:`` section in mkdocs.yml.

    Design decision: Only the ``nav`` key is modified; all other mkdocs
    settings (site_name, plugins, theme, extensions, extra_css) are
    preserved. This means the user can customise non-nav settings
    without the generator overwriting them.
    """

    def __init__(self, config: ConfigLoader):
        """Initialise with validated configuration.

        Args:
            config: Loaded ConfigLoader instance.
        """
        self.config = config

    def update_mkdocs_nav(self, file_paths: List[str]) -> None:
        """Merge newly generated files into the existing mkdocs.yml nav.

        Design decision: We MERGE rather than REPLACE the nav section so that
        running ``generate API=ordering`` followed by ``generate API=catalog``
        results in BOTH APIs appearing in the sidebar. Existing top-level groups
        that overlap with new groups are replaced; non-overlapping groups
        (from previous runs or hand-crafted entries) are preserved.

        Args:
            file_paths: List of relative doc paths that were generated.
        """
        mkdocs_path = self.config.mkdocs_config_path
        if not mkdocs_path.exists():
            logger.warning("mkdocs.yml not found at %s, creating new", mkdocs_path)
            existing = {}
        else:
            with open(mkdocs_path, "r", encoding="utf-8") as f:
                existing = yaml.safe_load(f) or {}

        new_nav = self._build_nav_tree(file_paths)
        old_nav = existing.get("nav", [])

        merged = self._merge_nav(old_nav, new_nav)

        existing["nav"] = merged
        if "site_name" not in existing:
            existing["site_name"] = self.config.site_name

        with open(mkdocs_path, "w", encoding="utf-8") as f:
            yaml.dump(
                existing, f,
                default_flow_style=False, sort_keys=False, allow_unicode=True,
            )

        logger.info("Updated mkdocs.yml navigation at %s", mkdocs_path)

    @staticmethod
    def _merge_nav(old_nav: List, new_nav: List) -> List:
        """Merge new nav entries into old nav, preserving non-overlapping groups.

        Design decision: Uses the dict key (group name) as the identity.
        If a group exists in both old and new, the new version wins.
        Groups only in old are kept. ``Home`` entry is always first.
        """
        # Build key -> entry maps for O(1) lookup.
        def _key(entry) -> str:
            if isinstance(entry, dict):
                return next(iter(entry))
            return str(entry)

        old_map = {_key(e): e for e in old_nav}
        new_map = {_key(e): e for e in new_nav}

        # Start with new entries (they take priority).
        merged_map = {**old_map, **new_map}

        # Ensure Home is always first.
        result: List = []
        if "Home" in merged_map:
            result.append(merged_map.pop("Home"))

        # Add remaining entries in sorted order.
        for key in sorted(merged_map.keys()):
            result.append(merged_map[key])

        return result

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _build_nav_tree(self, file_paths: List[str]) -> List:
        """Build a hierarchical navigation list from flat file paths.

        Design decision: Files are grouped by their top-level directory.
        Within each group, files are organised into sub-groups based on
        their directory structure, matching the v1 template pattern.
        """
        nav: List = [{"Home": "index.md"}]
        groups: Dict[str, List[str]] = defaultdict(list)

        for path in sorted(file_paths):
            parts = Path(path).parts
            if len(parts) == 1:
                title = self._title_from_filename(path)
                nav.append({title: path})
            else:
                top = parts[0]
                groups[top].append(path)

        for group_name, paths in sorted(groups.items()):
            sub_nav = self._build_group_nav(group_name, paths)
            nav.append({group_name: sub_nav})

        return nav

    def _build_group_nav(self, group_name: str, paths: List[str]) -> List:
        """Build navigation entries for a directory group."""
        sub_groups: Dict[str, List[Dict]] = defaultdict(list)
        direct_items: List[Dict] = []

        for path in sorted(paths):
            parts = Path(path).parts
            filename = parts[-1]
            title = self._title_from_filename(filename)

            if len(parts) == 2:
                direct_items.append({title: path})
            elif len(parts) >= 3:
                sub_folder = parts[1]
                sub_title = self._title_from_filename(sub_folder)
                sub_groups[sub_title].append({title: path})

        result: List = []
        for sub_name, items in sorted(sub_groups.items()):
            result.append({sub_name: items})
        result.extend(direct_items)
        return result

    @staticmethod
    def _title_from_filename(filename: str) -> str:
        """Convert a filename or folder name to a readable navigation title."""
        name = filename.replace(".md", "").replace("-", " ").replace("_", " ")
        name = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', name)
        return name.strip()
