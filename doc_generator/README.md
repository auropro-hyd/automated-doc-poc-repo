# Documentation Generator - Technical Details

This document explains the internal architecture of the documentation generator tool.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    DOCUMENTATION GENERATOR                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  main.py ──► ConfigLoader ──► CodeParser ──► LLMAdapter         │
│                                    │              │              │
│                                    ▼              ▼              │
│                              Source Code    LLM Response         │
│                                    │              │              │
│                                    └──────┬───────┘              │
│                                           ▼                      │
│                                   DocGenerator                   │
│                                           │                      │
│                                           ▼                      │
│                                   Markdown Output                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Modules

### config_loader.py

Handles all configuration management:
- Loads settings from `config.env`
- Provides typed access to configuration values
- Validates required settings

**Key Class:** `ConfigLoader`

### code_parser.py

Parses .NET C# source code:
- Recursively finds all `.cs` files
- Extracts metadata (namespaces, classes, methods)
- Combines content for LLM processing

**Key Classes:** `CodeParser`, `FileInfo`, `ProjectInfo`

### llm_adapter.py

Provides model-agnostic LLM interface:
- Abstract base class for all providers
- Concrete implementations for OpenAI, Claude, Azure
- Factory pattern for adapter creation

**Key Classes:**
- `BaseLLMAdapter` (abstract)
- `OpenAIAdapter`
- `ClaudeAdapter`
- `AzureOpenAIAdapter`
- `LLMFactory`

### doc_generator.py

Main documentation generation logic:
- Orchestrates the generation pipeline
- Builds prompts for LLM
- Saves output to files

**Key Class:** `DocumentationGenerator`

### main.py

Entry point:
- Loads configuration
- Validates settings
- Runs generation pipeline

## Adding a New LLM Provider

To add support for a new LLM provider:

1. Create a new adapter class inheriting from `BaseLLMAdapter`:

```python
class NewProviderAdapter(BaseLLMAdapter):
    def __init__(self, api_key: str, model: str):
        # Initialize client
        pass
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        # Call the API
        pass
    
    def get_model_name(self) -> str:
        return f"NewProvider {self.model}"
```

2. Add configuration options in `config_loader.py`

3. Update `LLMFactory.create()` to handle the new provider

4. Update `config.env.template` with new configuration options

## Token/Character Limits

The code parser respects token limits:
- Default max characters: 100,000
- Files are processed in order of importance
- Large files may be truncated

## Error Handling

The tool handles common errors:
- Missing configuration file
- Invalid API keys
- Missing source paths
- LLM API errors

All errors include helpful messages for resolution.

## Testing

To test the tool without making API calls:

1. Set up mock responses in tests
2. Use the `CodeParser` independently to verify file parsing
3. Test configuration loading with test `.env` files

## Performance Considerations

- Source code is read once and cached
- LLM calls are the main bottleneck
- Consider using cheaper models for initial drafts
