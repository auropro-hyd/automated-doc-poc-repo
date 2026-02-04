"""
Configuration Loader

Loads configuration from config.env file and provides
access to settings throughout the application.
"""

import os
from pathlib import Path
from typing import Optional, List

# Try to import dotenv, but make it optional for testing
try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False
    def load_dotenv(path):
        """Fallback: manually load .env file."""
        if not path.exists():
            return
        with open(path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()


class ConfigLoader:
    """Loads and provides access to configuration settings."""
    
    def _load_config(self) -> None:
        """Load configuration from .env file."""
        if not self.config_path.exists():
            raise FileNotFoundError(
                f"Configuration file not found: {self.config_path}\n"
                f"Please copy config.env.template to .env (or config.env) and add your API keys.\n"
                f"Run: cp config.env.template .env"
            )
        
        load_dotenv(self.config_path)
    
    # --------------------------------------------
    # LLM Provider Settings
    # --------------------------------------------
    
    @property
    def llm_provider(self) -> str:
        """Get the configured LLM provider (openai, claude, azure)."""
        return os.getenv("LLM_PROVIDER", "openai").lower()
    
    @property
    def openai_api_key(self) -> Optional[str]:
        """Get OpenAI API key."""
        return os.getenv("OPENAI_API_KEY")
    
    @property
    def openai_model(self) -> str:
        """Get OpenAI model name."""
        return os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
    
    @property
    def claude_api_key(self) -> Optional[str]:
        """Get Claude (Anthropic) API key."""
        return os.getenv("CLAUDE_API_KEY")
    
    @property
    def claude_model(self) -> str:
        """Get Claude model name."""
        return os.getenv("CLAUDE_MODEL", "claude-3-sonnet-20240229")
    
    @property
    def azure_openai_api_key(self) -> Optional[str]:
        """Get Azure OpenAI API key."""
        return os.getenv("AZURE_OPENAI_API_KEY")
    
    @property
    def azure_openai_endpoint(self) -> Optional[str]:
        """Get Azure OpenAI endpoint."""
        return os.getenv("AZURE_OPENAI_ENDPOINT")
    
    @property
    def azure_openai_deployment(self) -> Optional[str]:
        """Get Azure OpenAI deployment name."""
        return os.getenv("AZURE_OPENAI_DEPLOYMENT")
    
    @property
    def azure_openai_api_version(self) -> str:
        """Get Azure OpenAI API version."""
        return os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
    
    # --------------------------------------------
    # Output Settings
    # --------------------------------------------
    
    @property
    def output_dir(self) -> Path:
        """Get the output directory for generated docs."""
        output = os.getenv("OUTPUT_DIR", "local_dev/generated_docs")
        return self.project_root / output
    
    @property
    def docs_dir(self) -> Path:
        """Get the MkDocs docs directory."""
        docs = os.getenv("DOCS_DIR", "docs")
        return self.project_root / docs
    
    # --------------------------------------------
    # API Configuration
    # --------------------------------------------
    
    # Predefined API configurations
    API_CONFIGS = {
        "ordering": {
            "paths": "src/Ordering.API,src/Ordering.Domain,src/Ordering.Infrastructure",
            "name": "Ordering API",
            "filename": "ordering-api.md"
        },
        "catalog": {
            "paths": "src/Catalog.API",
            "name": "Catalog API", 
            "filename": "catalog-api.md"
        },
        "basket": {
            "paths": "src/Basket.API",
            "name": "Basket API",
            "filename": "basket-api.md"
        }
    }
    
    def __init__(self, config_path: Optional[str] = None, target_api: Optional[str] = None):
        """
        Initialize the configuration loader.
        
        Args:
            config_path: Path to config file. If None, looks for .env or config.env in project root.
            target_api: Override the target API (ordering, catalog, basket, custom).
        """
        self.project_root = Path(__file__).parent.parent
        self._target_api_override = target_api
        
        if config_path:
            self.config_path = Path(config_path)
        else:
            # Check for .env first, then config.env
            env_path = self.project_root / ".env"
            config_env_path = self.project_root / "config.env"
            
            if env_path.exists():
                self.config_path = env_path
            elif config_env_path.exists():
                self.config_path = config_env_path
            else:
                # Default to .env for error message
                self.config_path = env_path
        
        self._load_config()
    
    @property
    def target_api(self) -> str:
        """Get the target API to document."""
        if self._target_api_override:
            return self._target_api_override.lower()
        return os.getenv("TARGET_API", "ordering").lower()
    
    @property
    def api_name(self) -> str:
        """Get the display name for the target API."""
        api = self.target_api
        if api in self.API_CONFIGS:
            return self.API_CONFIGS[api]["name"]
        return os.getenv("CUSTOM_API_NAME", "Custom API")
    
    @property
    def output_filename(self) -> str:
        """Get the output filename for the target API."""
        api = self.target_api
        if api in self.API_CONFIGS:
            return self.API_CONFIGS[api]["filename"]
        custom_name = os.getenv("CUSTOM_API_NAME", "custom-api")
        return f"{custom_name.lower().replace(' ', '-')}.md"
    
    @property
    def source_paths(self) -> List[Path]:
        """Get list of source code paths to document based on target API."""
        api = self.target_api
        
        if api == "ordering":
            paths_str = os.getenv("ORDERING_API_PATHS", self.API_CONFIGS["ordering"]["paths"])
        elif api == "catalog":
            paths_str = os.getenv("CATALOG_API_PATHS", self.API_CONFIGS["catalog"]["paths"])
        elif api == "basket":
            paths_str = os.getenv("BASKET_API_PATHS", self.API_CONFIGS["basket"]["paths"])
        elif api == "custom":
            paths_str = os.getenv("CUSTOM_API_PATHS", "src/YourAPI")
        else:
            # Check if it's a known API
            if api in self.API_CONFIGS:
                paths_str = self.API_CONFIGS[api]["paths"]
            else:
                raise ValueError(f"Unknown API: {api}. Use: ordering, catalog, basket, or custom")
        
        paths = [p.strip() for p in paths_str.split(",")]
        return [self.project_root / p for p in paths]
    
    @classmethod
    def get_available_apis(cls) -> List[str]:
        """Get list of available predefined APIs."""
        return list(cls.API_CONFIGS.keys()) + ["custom"]
    
    # --------------------------------------------
    # Generation Options
    # --------------------------------------------
    
    @property
    def include_diagrams(self) -> bool:
        """Whether to include Mermaid diagrams."""
        return os.getenv("INCLUDE_DIAGRAMS", "true").lower() == "true"
    
    @property
    def log_level(self) -> str:
        """Get logging level."""
        return os.getenv("LOG_LEVEL", "INFO")
    
    # --------------------------------------------
    # Validation
    # --------------------------------------------
    
    def validate(self) -> None:
        """Validate that required configuration is present."""
        provider = self.llm_provider
        
        if provider == "openai":
            if not self.openai_api_key or self.openai_api_key == "your-openai-api-key-here":
                raise ValueError(
                    "OpenAI API key not configured. "
                    "Please set OPENAI_API_KEY in config.env"
                )
        
        elif provider == "claude":
            if not self.claude_api_key or self.claude_api_key == "your-claude-api-key-here":
                raise ValueError(
                    "Claude API key not configured. "
                    "Please set CLAUDE_API_KEY in config.env"
                )
        
        elif provider == "azure":
            if not self.azure_openai_api_key or self.azure_openai_api_key == "your-azure-openai-key-here":
                raise ValueError(
                    "Azure OpenAI API key not configured. "
                    "Please set AZURE_OPENAI_API_KEY in config.env"
                )
            if not self.azure_openai_endpoint:
                raise ValueError(
                    "Azure OpenAI endpoint not configured. "
                    "Please set AZURE_OPENAI_ENDPOINT in config.env"
                )
        
        else:
            raise ValueError(
                f"Unknown LLM provider: {provider}. "
                "Supported providers: openai, claude, azure"
            )
        
        # Validate source paths exist
        for path in self.source_paths:
            if not path.exists():
                raise ValueError(f"Source path does not exist: {path}")
    
    def __str__(self) -> str:
        """String representation of configuration."""
        return (
            f"Configuration:\n"
            f"  LLM Provider: {self.llm_provider}\n"
            f"  Output Dir: {self.output_dir}\n"
            f"  Docs Dir: {self.docs_dir}\n"
            f"  Source Paths: {[str(p) for p in self.source_paths]}\n"
            f"  Include Diagrams: {self.include_diagrams}"
        )
