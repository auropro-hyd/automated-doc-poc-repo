"""Config-driven file classification and source URL generation.

Design decision: Classification and URL building are separated from the
regex extraction engine because they are pure config-lookup functions
with no parsing logic. This makes them independently testable and
highlights that all classification behaviour comes from YAML, not code.
"""

import re
import logging
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class FileClassifier:
    """Classify source files into documentation categories and build source URLs.

    Design decision: Classification uses regex patterns from YAML config
    rather than hardcoded naming conventions, so the same code supports
    CQRS, MVC, Clean Architecture, etc. without modification.
    """

    def __init__(self, config: Dict[str, Any]):
        """Initialise with the full YAML configuration dictionary.

        Args:
            config: Parsed project_config.yml content.
        """
        self._config = config
        self._classification_rules: List[Dict] = config.get("classification_rules", [])

    def classify_file(self, relative_path: str) -> Tuple[str, Optional[str], Optional[str]]:
        """Classify a source file into a documentation category.

        Args:
            relative_path: Path relative to the project root (forward slashes).

        Returns:
            Tuple of (category, doc_file, doc_title).
            Falls back to ("other", None, None) if no rule matches.
        """
        normalised = relative_path.replace("\\", "/")
        for rule in self._classification_rules:
            if re.search(rule["pattern"], normalised):
                return (
                    rule["category"],
                    rule.get("doc_file"),
                    rule.get("doc_title"),
                )
        return ("other", None, None)

    def source_url(self, file_path: str, line: Optional[int] = None) -> str:
        """Build a clickable source URL for a file and optional line number.

        Design decision: The URL format string lives in project_config.yml
        so the same code works for GitHub, GitLab, and Bitbucket without
        any Python changes.

        Args:
            file_path: Path relative to the repository root.
            line: Optional line number.

        Returns:
            Fully-qualified URL string.
        """
        repo = self._config.get("repository", {})
        fmt = repo.get("source_url_format", "{repo_url}/blob/{branch}/{file_path}")
        url = fmt.format(
            repo_url=repo.get("url", ""),
            branch=repo.get("branch", "main"),
            file_path=file_path,
            line=line if line else "",
        )
        # Strip dangling anchor fragment when no line number is given.
        if url.endswith("#L"):
            url = url[:-2]
        return url
