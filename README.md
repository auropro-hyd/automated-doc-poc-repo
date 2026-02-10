# Automated Documentation Generator

A config-driven tool that automatically generates comprehensive, structured
documentation for .NET applications using LLM analysis. Produces
MkDocs-compatible markdown with Mermaid diagrams, clickable source links,
cross-page navigation, and hierarchical site structure.

## Architecture

```
project_config.yml          Central config (all settings)
.env                        API keys only (secrets)
        │
        ▼
config.py                   Loads YAML + .env, validates paths
        │
        ▼
parsing/
  parser.py                 Scans source files (config-driven)
  classifier.py             Classifies files using regex rules from YAML
        │
        ▼
generation/
  orchestrator.py           Groups files, makes targeted LLM calls
  context.py                Builds class metadata, detects features
        │
llm/
  adapters.py               Multi-provider LLM abstraction (OpenAI/Claude/Azure)
  prompts.py                Prompt templates per doc type
        │
        ▼
output/
  assembler.py              Writes markdown, resolves cross-references
  navigation.py             Merges into mkdocs.yml nav (preserves other APIs)
        │
        ▼
src/docs/docs/              Generated MkDocs-ready documentation
src/docs/templates/         Read-only reference templates (never overwritten)
```

## Quick Start

### 1. Setup

```bash
# Clone and enter the repo
git clone <repo-url>
cd automated-doc-poc-repo

# Create virtual environment and install dependencies
make setup
source venv/bin/activate
```

### 2. Configure

```bash
# Copy config templates
cp project_config.yml.template project_config.yml
cp .env.template .env

# Edit project_config.yml with your repository details:
#   - repository.url and branch
#   - apis section (source paths and dependencies)
#   - classification_rules (adjust for your architecture)
#   - template_examples (paths to reference docs, or null)

# Edit .env with your LLM API key
```

### 3. Generate

```bash
# List available APIs
make list

# Generate docs for a specific API
make generate API=ordering

# Clean + regenerate (removes stale files first)
make regenerate API=ordering

# Or generate for all configured APIs
make generate-all

# Dry-run (parse and classify without LLM calls)
make dry-run API=ordering
```

### 4. View

```bash
# Start MkDocs dev server
make serve

# Open http://127.0.0.1:8000

# Stop the server
make kill
```

## Configuration

All settings live in `project_config.yml`. API keys live in `.env`.

### Key Sections

| Section                                 | Purpose                                                           |
| --------------------------------------- | ----------------------------------------------------------------- |
| `repository`                          | Git repo URL, branch, source URL format (GitHub/GitLab/Bitbucket) |
| `language` / `file_extensions`      | What source files to scan                                         |
| `exclude_folders` / `exclude_files` | What to skip                                                      |
| `apis`                                | Each API with source paths and dependent libraries                |
| `classification_rules`                | Regex patterns mapping files to documentation categories          |
| `feature_detection`                   | How to identify API features for feature pages                    |
| `output`                              | Where to write docs, MkDocs config path, site name                |
| `template_examples`                   | Reference doc files for few-shot LLM prompts                      |
| `llm`                                 | Provider, model, max_tokens, temperature, retry settings          |
| `logging`                             | Log level                                                         |

### Adapting for Different Architectures

**CQRS/DDD** (default): Classification rules match `*CommandHandler.cs`,
`*Validator.cs`, `AggregatesModel/*`, etc.

**MVC**: Change rules to match `*Controller.cs`, `*Service.cs`,
`*Repository.cs`.

**Clean Architecture**: Change rules to match `*UseCase.cs`,
`*Gateway.cs`, `*Presenter.cs`.

No Python code changes are needed -- only YAML edits.

### Adapting for Different Git Platforms

Set `repository.source_url_format`:

- **GitHub**: `{repo_url}/blob/{branch}/{file_path}#L{line}`
- **GitLab**: `{repo_url}/-/blob/{branch}/{file_path}#L{line}`
- **Bitbucket**: `{repo_url}/src/{branch}/{file_path}#lines-{line}`

## Makefile Commands

| Command                       | Description                               |
| ----------------------------- | ----------------------------------------- |
| `make setup`                | Create venv and install dependencies      |
| `make generate API=<key>`   | Generate docs for one API                 |
| `make regenerate API=<key>` | Clean old output + regenerate for one API |
| `make generate-all`         | Generate docs for all APIs                |
| `make list`                 | List available APIs                       |
| `make dry-run API=<key>`    | Parse/classify without LLM calls          |
| `make serve`                | Start MkDocs dev server                   |
| `make build`                | Build static site                         |
| `make kill`                 | Stop MkDocs server                        |
| `make validate-config`      | Validate project_config.yml               |
| `make help`                 | Show all commands                         |

## Project Structure

```
automated-doc-poc-repo/
├── doc_generator/
│   ├── __init__.py              Package init
│   ├── __main__.py              python -m doc_generator entry point
│   ├── cli.py                   CLI argument parsing and main()
│   ├── config.py                Config loader (YAML + .env)
│   ├── models.py                Shared data classes
│   ├── parsing/
│   │   ├── __init__.py
│   │   ├── parser.py            Regex-based source code extraction
│   │   └── classifier.py        File classification + source URL builder
│   ├── llm/
okay thanks
│   │   ├── __init__.py
│   │   ├── adapters.py          Multi-provider LLM abstraction
│   │   └── prompts.py           Prompt templates per doc type
│   ├── generation/
│   │   ├── __init__.py
│   │   ├── orchestrator.py      Pipeline coordinator
│   │   └── context.py           Context building + feature detection
│   ├── output/
│   │   ├── __init__.py
│   │   ├── assembler.py         File writing + cross-ref resolution
│   │   └── navigation.py        MkDocs nav builder
│   └── docs/
│       ├── README.md            Module documentation
│       └── IMPROVEMENT_NOTES.md Known limitations + roadmap
├── project_config.yml           Central config (gitignored)
├── project_config.yml.template  Config template (committed)
├── .env                         API keys (gitignored)
├── .env.template                Secrets template (committed)
├── requirements.txt             Python dependencies
├── Makefile                     Command shortcuts
└── src/docs/                    MkDocs site
    ├── mkdocs.yml
    ├── css/extra_css.css
    ├── templates/               READ-ONLY reference templates (committed)
    │   └── reference_docs/      v1 template examples for LLM prompts
    └── docs/                    Generated output (gitignored except index.md)
```

### Template vs. Generated Output

| Folder                                 | Purpose                                                                   |       Git Tracked?       |
| -------------------------------------- | ------------------------------------------------------------------------- | :----------------------: |
| `src/docs/templates/reference_docs/` | Read-only v1 reference templates used as few-shot examples in LLM prompts |           Yes           |
| `src/docs/docs/`                     | Generated documentation output (recreated each run)                       | No (except `index.md`) |

This separation ensures that `make generate` never destroys the reference templates.

## Troubleshooting

| Issue                              | Solution                                                                           |
| ---------------------------------- | ---------------------------------------------------------------------------------- |
| `Config file not found`          | Run `cp project_config.yml.template project_config.yml`                          |
| `OPENAI_API_KEY is not set`      | Add your key to `.env`                                                           |
| `API 'xyz' not found`            | Check the `apis` section in `project_config.yml`                               |
| Mermaid diagrams show syntax error | Check MkDocs dev console; update `template_examples` with correct reference docs |
| Import errors                      | Run `make setup` and `source venv/bin/activate`                                |
