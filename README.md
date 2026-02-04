# Automated Documentation Generator

An AI-powered tool that automatically generates comprehensive documentation for .NET APIs by analyzing source code.

## Overview

This tool reads .NET source code files, sends them to an LLM (Large Language Model) for analysis, and generates structured markdown documentation following a standardized template.

### Features

- **Model-Agnostic**: Supports OpenAI, Claude (Anthropic), and Azure OpenAI
- **Multi-API Support**: Document any API with a single command
- **Structured Output**: Generates documentation with 8 standardized sections
- **Mermaid Diagrams**: Auto-generates sequence and class dependency diagrams
- **MkDocs Integration**: Ready-to-view documentation in browser
- **Makefile**: Easy command execution

---

## Quick Start

### Option 1: Using Makefile (Recommended)

```bash
# First-time setup (creates venv + installs dependencies)
make setup

# Add your API key to .env file
# Then generate documentation
make generate                  # Default: Ordering API
make generate API=catalog      # Catalog API
make generate-all              # All APIs

# View in browser
make serve
# Open http://127.0.0.1:8000
```

### Option 2: Manual Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate       # On macOS/Linux
# OR: venv\Scripts\activate    # On Windows

# Install dependencies
pip install -r requirements.txt

# Configure API key (copy template)
cp config.env.template .env
# Edit .env and add your API key

# Generate documentation
python -m doc_generator.main --api ordering

# View in browser
mkdocs serve
```

---

## Makefile Commands

Run `make help` to see all available commands:

### Setup & Generation

| Command | Description |
|---------|-------------|
| `make setup` | Complete first-time setup (venv + dependencies) |
| `make generate` | Generate docs for default API (ordering) |
| `make generate API=catalog` | Generate docs for specific API |
| `make generate-ordering` | Generate docs for Ordering API |
| `make generate-catalog` | Generate docs for Catalog API |
| `make generate-basket` | Generate docs for Basket API |
| `make generate-all` | Generate docs for ALL APIs |

### Server Management

| Command | Description |
|---------|-------------|
| `make serve` | Start MkDocs server (http://127.0.0.1:8000) |
| `make kill` | Kill server running on port 8000 |
| `make restart` | Restart server (kill + serve) |

### Utilities

| Command | Description |
|---------|-------------|
| `make list` | List available APIs |
| `make dry-run` | Test without calling LLM |
| `make clean` | Clean generated files |
| `make test` | Run basic tests |
| `make help` | Show all commands |

---

## Typical Workflow

### Daily Usage

```bash
# 1. Start the documentation server (keep running in one terminal)
make serve
# Open http://127.0.0.1:8000 in browser

# 2. In another terminal, generate documentation
make generate                    # Ordering API (default)
make generate API=catalog        # Catalog API
make generate API=basket         # Basket API

# Browser auto-refreshes when docs are generated!
# Just click sidebar to switch between APIs

# 3. When done, stop the server
# Press Ctrl+C in the terminal running "make serve"
# OR run: make kill
```

### When to Use `make kill`

| Situation | What to do |
|-----------|------------|
| Error: "Address already in use" | Run `make kill` then `make serve` |
| Server not responding | Run `make restart` |
| Done viewing documentation | Press `Ctrl+C` or `make kill` |
| Generating new docs | **Don't kill!** Server auto-refreshes |

---

## Multi-API Support

The tool supports documenting multiple APIs:

```bash
# Using Makefile
make generate API=ordering     # Ordering API
make generate API=catalog      # Catalog API
make generate API=basket       # Basket API

# Using Python directly
python -m doc_generator.main --api ordering
python -m doc_generator.main --api catalog
python -m doc_generator.main --api basket

# List all available APIs
python -m doc_generator.main --list
```

### Available APIs

| API | Source Paths | Output File |
|-----|--------------|-------------|
| `ordering` | Ordering.API + Domain + Infrastructure | `ordering-api.md` |
| `catalog` | Catalog.API | `catalog-api.md` |
| `basket` | Basket.API | `basket-api.md` |
| `custom` | (configurable in .env) | `custom.md` |

---

## Configuration

### Environment File

The tool looks for configuration in this order:
1. `.env` (preferred)
2. `config.env` (alternative)

Copy the template and add your API key:

```bash
cp config.env.template .env
```

### Configuration Options

| Variable | Description | Options |
|----------|-------------|---------|
| `LLM_PROVIDER` | AI provider to use | `openai`, `claude`, `azure` |
| `TARGET_API` | Default API to document | `ordering`, `catalog`, `basket`, `custom` |
| `OPENAI_API_KEY` | OpenAI API key | Your key from platform.openai.com |
| `OPENAI_MODEL` | OpenAI model | `gpt-4-turbo-preview` (default) |
| `CLAUDE_API_KEY` | Anthropic API key | Your key from console.anthropic.com |
| `AZURE_OPENAI_API_KEY` | Azure OpenAI key | Your key from Azure portal |
| `INCLUDE_DIAGRAMS` | Generate Mermaid diagrams | `true` or `false` |

### Adding a New API

1. Edit `doc_generator/config_loader.py` and add to `API_CONFIGS`:
   ```python
   API_CONFIGS = {
       ...
       "newapi": {
           "paths": "src/NewAPI,src/NewAPI.Domain",
           "name": "New API",
           "filename": "newapi.md"
       }
   }
   ```

2. Add navigation in `mkdocs.yml`:
   ```yaml
   nav:
     - Home: index.md
     - APIs:
       - New API: newapi.md
   ```

3. Generate documentation:
   ```bash
   make generate API=newapi
   ```

---

## Project Structure

```
automated-doc-poc-repo/
│
├── Makefile                     # Easy command execution
├── README.md                    # This file
├── .gitignore                   # Git ignore rules
├── .env                         # Your configuration (not in git)
├── config.env.template          # Configuration template
├── requirements.txt             # Python dependencies
├── mkdocs.yml                   # MkDocs configuration
│
├── doc_generator/               # Documentation generator tool
│   ├── __init__.py
│   ├── main.py                  # Entry point (CLI)
│   ├── config_loader.py         # Configuration management
│   ├── code_parser.py           # Source code parsing
│   ├── llm_adapter.py           # LLM provider abstraction
│   ├── doc_generator.py         # Documentation generation
│   └── README.md                # Technical documentation
│
├── docs/                        # MkDocs source (viewable docs)
│   ├── index.md                 # Homepage
│   ├── ordering-api.md          # Generated/placeholder
│   ├── catalog-api.md           # Generated/placeholder
│   └── basket-api.md            # Generated/placeholder
│
├── local_dev/                   # Development outputs (not in git)
│   └── generated_docs/          # Raw generated files
│
└── src/                         # .NET source code
    ├── Ordering.API/
    ├── Ordering.Domain/
    ├── Ordering.Infrastructure/
    ├── Catalog.API/
    └── Basket.API/
```

---

## Generated Documentation Structure

The tool generates documentation with 8 standardized sections:

1. **Feature Overview** - Purpose, business motivation, stakeholders
2. **Business Implementation** - Business rules, use cases, sequence diagrams
3. **Technical Implementation** - API endpoints, classes, architecture
4. **Validation & Error Handling** - Input validation, error scenarios
5. **Security & Access Control** - Authentication, authorization
6. **Testing Strategy** - Unit, integration, acceptance tests
7. **Deployment Considerations** - Infrastructure, feature flags
8. **References** - Links to source files

---

## Troubleshooting

### "Address already in use" error

```bash
# Kill the existing server and restart
make kill
make serve

# Or use restart (does both)
make restart
```

### "Configuration file not found" error

```bash
# Copy the template
cp config.env.template .env

# Or if you prefer config.env
cp config.env.template config.env
```

### "API key not configured" error

Edit your `.env` file and add your API key:
```
OPENAI_API_KEY=sk-your-actual-key-here
```

### "Module not found" error

```bash
# Make sure you're in the virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
# Or: make install
```

### MkDocs not showing content

```bash
# Make sure documentation was generated
make generate

# Check if files exist in docs/ folder
ls docs/
```

### Link warnings in MkDocs

Warnings like `link './Ordering.API/Apis/OrdersApi.cs' not found` are **harmless**. 
These are links to source code files which don't exist in the docs folder. 
The documentation will still work correctly.

---

## Development

### Running Tests

```bash
make test
```

### Dry Run Mode

Test without making API calls:

```bash
make dry-run API=catalog
# Or: python -m doc_generator.main --api catalog --dry-run
```

### Clean Generated Files

```bash
make clean       # Clean generated docs only
make clean-all   # Clean everything including venv
```

---

## License

This project is for internal use.

---

*Generated documentation is stored in `local_dev/generated_docs/` and copied to `docs/` for viewing.*
