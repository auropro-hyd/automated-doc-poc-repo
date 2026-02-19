"""Configuration loader for the documentation generator.

Design decision: Configuration is split into two sources:
  1. project_config.yml -- all project settings (paths, rules, LLM params).
     This is the single source of truth for non-secret configuration.
  2. .env -- API keys only (secrets that must never be committed).

This separation means project_config.yml can be freely shared as a template
while .env remains gitignored. The Python code contains zero hardcoded repo
names, paths, or magic strings -- everything is driven by the YAML.
"""

import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from dotenv import load_dotenv
import os

logger = logging.getLogger(__name__)


class ConfigLoader:
    """Loads and validates configuration from project_config.yml and .env.

    Design decision: A single class owns all config access so every other
    module receives a validated, typed config dict rather than reaching into
    environment variables or YAML files directly.
    """

    # Resolved project root (parent of this file's parent).
    PROJECT_ROOT = Path(__file__).resolve().parent.parent

    def __init__(
        self,
        config_path: Optional[Path] = None,
        env_path: Optional[Path] = None,
    ):
        """Load configuration from disk.

        Args:
            config_path: Path to project_config.yml. Defaults to PROJECT_ROOT.
            env_path: Path to .env file. Defaults to PROJECT_ROOT.
        """
        self._config_path = config_path or self.PROJECT_ROOT / "project_config.yml"
        self._env_path = env_path or self.PROJECT_ROOT / ".env"

        self._raw: Dict[str, Any] = {}
        self._load_env()
        self._load_yaml()
        self._validate()

    # ------------------------------------------------------------------
    # Public accessors
    # ------------------------------------------------------------------

    @property
    def raw(self) -> Dict[str, Any]:
        """Full raw configuration dictionary."""
        return self._raw

    @property
    def project_root(self) -> Path:
        """Absolute path to the repository root."""
        return self.PROJECT_ROOT

    # --- Repository ---

    @property
    def repo_url(self) -> str:
        return self._raw["repository"]["url"]

    @property
    def repo_branch(self) -> str:
        return self._raw["repository"]["branch"]

    @property
    def source_url_format(self) -> str:
        return self._raw["repository"]["source_url_format"]

    # --- Language / Scanning ---

    @property
    def language(self) -> str:
        return self._raw.get("language", "csharp")

    @property
    def file_extensions(self) -> List[str]:
        return self._raw.get("file_extensions", ["*.cs"])

    @property
    def exclude_folders(self) -> List[str]:
        return self._raw.get("exclude_folders", [])

    @property
    def exclude_files(self) -> List[str]:
        return self._raw.get("exclude_files", [])

    # --- APIs ---

    @property
    def apis(self) -> Dict[str, Dict]:
        return self._raw.get("apis", {})

    def api_config(self, api_key: str) -> Dict:
        """Return configuration for a specific API by its key.

        Args:
            api_key: Key in the ``apis`` section of the YAML.

        Returns:
            Dict with display_name, source_paths, dependent_libraries.

        Raises:
            KeyError: If the API key is not defined.
        """
        if api_key not in self.apis:
            available = ", ".join(self.apis.keys())
            raise KeyError(
                f"API '{api_key}' not found in config. Available: {available}"
            )
        return self.apis[api_key]

    def source_paths(self, api_key: str) -> List[Path]:
        """Resolve source paths for an API to absolute Path objects."""
        cfg = self.api_config(api_key)
        paths = cfg.get("source_paths", [])
        return [self.PROJECT_ROOT / p for p in paths]

    def dependent_library_paths(self, api_key: str) -> List[Path]:
        """Resolve dependent library paths for an API."""
        cfg = self.api_config(api_key)
        paths = cfg.get("dependent_libraries", [])
        return [self.PROJECT_ROOT / p for p in paths]

    # --- Classification ---

    @property
    def classification_rules(self) -> List[Dict]:
        return self._raw.get("classification_rules", [])

    # --- Feature detection ---

    @property
    def feature_detection(self) -> Dict:
        return self._raw.get("feature_detection", {})

    # --- Output ---

    @property
    def output_docs_dir(self) -> Path:
        return self.PROJECT_ROOT / self._raw.get("output", {}).get("docs_dir", "docs")

    @property
    def mkdocs_config_path(self) -> Path:
        return self.PROJECT_ROOT / self._raw.get("output", {}).get(
            "mkdocs_config", "mkdocs.yml"
        )

    @property
    def site_name(self) -> str:
        return self._raw.get("output", {}).get("site_name", "Documentation")

    @property
    def css_dir(self) -> Path:
        return self.PROJECT_ROOT / self._raw.get("output", {}).get("css_dir", "css")

    # --- Template examples ---

    @property
    def template_examples(self) -> Dict[str, Optional[str]]:
        return self._raw.get("template_examples", {})

    def template_example_content(self, key: str) -> Optional[str]:
        """Read and return the content of a template example file.

        Args:
            key: Template key (e.g. 'handler', 'feature', 'aggregate').

        Returns:
            File content as string, or None if the path is not set or the
            file does not exist.
        """
        path_str = self.template_examples.get(key)
        if not path_str:
            return None
        full = self.PROJECT_ROOT / path_str
        if not full.exists():
            logger.warning("Template example not found: %s", full)
            return None
        return full.read_text(encoding="utf-8")

    # --- LLM ---

    @property
    def llm_provider(self) -> str:
        return self._raw.get("llm", {}).get("provider", "openai")

    @property
    def llm_model(self) -> str:
        return self._raw.get("llm", {}).get("model", "gpt-4o")

    @property
    def llm_max_tokens(self) -> int:
        return int(self._raw.get("llm", {}).get("max_tokens", 8192))

    @property
    def llm_temperature(self) -> float:
        return float(self._raw.get("llm", {}).get("temperature", 0.3))

    @property
    def llm_retry_attempts(self) -> int:
        return int(self._raw.get("llm", {}).get("retry_attempts", 3))

    @property
    def llm_retry_delay(self) -> float:
        return float(self._raw.get("llm", {}).get("retry_delay_seconds", 2))

    @property
    def detail_level(self) -> str:
        """Detail level for generated docs: summary, standard, or detailed."""
        return self._raw.get("llm", {}).get("detail_level", "detailed")

    @property
    def max_classes_per_chunk(self) -> int:
        """Max classes per LLM call. Groups larger than this are split."""
        return int(self._raw.get("llm", {}).get("max_classes_per_chunk", 3))

    # --- Secrets (from .env) ---

    @property
    def openai_api_key(self) -> str:
        return os.getenv("OPENAI_API_KEY", "")

    @property
    def anthropic_api_key(self) -> str:
        return os.getenv("ANTHROPIC_API_KEY", "")

    @property
    def azure_openai_endpoint(self) -> str:
        return os.getenv("AZURE_OPENAI_ENDPOINT", "")

    @property
    def azure_openai_key(self) -> str:
        return os.getenv("AZURE_OPENAI_KEY", "")

    @property
    def azure_openai_deployment(self) -> str:
        return os.getenv("AZURE_OPENAI_DEPLOYMENT", "")

    @property
    def azure_openai_api_version(self) -> str:
        return os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")

    # --- Logging ---

    @property
    def log_level(self) -> str:
        return self._raw.get("logging", {}).get("level", "INFO")

    # ------------------------------------------------------------------
    # Internal loading / validation
    # ------------------------------------------------------------------

    def _load_env(self) -> None:
        """Load secrets from .env using python-dotenv."""
        if self._env_path.exists():
            load_dotenv(self._env_path)
            logger.debug("Loaded .env from %s", self._env_path)
        else:
            # Also try config.env for backward compatibility.
            alt = self.PROJECT_ROOT / "config.env"
            if alt.exists():
                load_dotenv(alt)
                logger.debug("Loaded config.env from %s", alt)

    def _load_yaml(self) -> None:
        """Load project_config.yml."""
        if not self._config_path.exists():
            logger.error("Config file not found: %s", self._config_path)
            sys.exit(1)
        with open(self._config_path, "r", encoding="utf-8") as fh:
            self._raw = yaml.safe_load(fh) or {}
        logger.debug("Loaded config from %s", self._config_path)

    def _validate(self) -> None:
        """Validate that required configuration fields are present."""
        errors: List[str] = []

        if "repository" not in self._raw:
            errors.append("Missing 'repository' section")
        else:
            repo = self._raw["repository"]
            if not repo.get("url"):
                errors.append("Missing 'repository.url'")
            if not repo.get("branch"):
                errors.append("Missing 'repository.branch'")

        if not self._raw.get("apis"):
            errors.append("Missing 'apis' section (at least one API required)")

        if not self._raw.get("classification_rules"):
            errors.append("Missing 'classification_rules' (at least one rule required)")

        # Validate LLM provider has matching API key.
        provider = self.llm_provider
        if provider == "openai" and not self.openai_api_key:
            errors.append("LLM provider is 'openai' but OPENAI_API_KEY is not set in .env")
        elif provider == "claude" and not self.anthropic_api_key:
            errors.append("LLM provider is 'claude' but ANTHROPIC_API_KEY is not set in .env")
        elif provider == "azure":
            if not self.azure_openai_key:
                errors.append("LLM provider is 'azure' but AZURE_OPENAI_KEY is not set")
            if not self.azure_openai_endpoint:
                errors.append("LLM provider is 'azure' but AZURE_OPENAI_ENDPOINT is not set")

        if errors:
            for e in errors:
                logger.error("Config validation: %s", e)
            sys.exit(1)

        # Non-fatal warnings: check source paths exist on disk.
        for api_key, api_cfg in self.apis.items():
            for p in api_cfg.get("source_paths", []):
                full = self.PROJECT_ROOT / p
                if not full.exists():
                    logger.warning(
                        "Source path for '%s' does not exist: %s "
                        "(check project_config.yml apis.%s.source_paths)",
                        api_key, full, api_key,
                    )
            for p in api_cfg.get("dependent_libraries", []):
                full = self.PROJECT_ROOT / p
                if not full.exists():
                    logger.warning(
                        "Dependent library path for '%s' does not exist: %s",
                        api_key, full,
                    )

        # Check template example files exist.
        for key, path_str in self.template_examples.items():
            if path_str:
                full = self.PROJECT_ROOT / path_str
                if not full.exists():
                    logger.warning(
                        "Template example '%s' not found: %s", key, full
                    )

        logger.info("Configuration validated successfully")
