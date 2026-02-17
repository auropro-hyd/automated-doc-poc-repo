# doc_generator Package Architecture

## Overview

The `doc_generator` package is a config-driven documentation generation pipeline
for .NET applications. It parses source code, classifies files, generates
structured documentation via LLM, and assembles MkDocs-compatible output.

## Package Structure

```
doc_generator/
├── __init__.py              Package metadata and version
├── __main__.py              Enables `python -m doc_generator`
├── cli.py                   CLI entry point (argument parsing, main loop)
├── config.py                Config loader (project_config.yml + .env)
├── models.py                Shared data classes (FileInfo, ClassInfo, etc.)
├── parsing/
│   ├── parser.py            Regex-based C# source code extraction
│   └── classifier.py        Config-driven file classification + URL builder
├── llm/
│   ├── adapters.py          Multi-provider LLM abstraction (OpenAI/Claude/Azure)
│   └── prompts.py           Prompt template functions + category mapping
├── generation/
│   ├── orchestrator.py      Pipeline coordinator (parse → classify → generate)
│   └── context.py           Context builders, file grouping, feature detection
├── output/
│   ├── assembler.py         File writing, cross-reference resolution
│   ├── link_resolver.py     Post-generation link validation + GitHub URL fixing
│   ├── navigation.py        MkDocs nav tree builder
│   └── clean.py             Generated file cleanup utility
└── docs/
    ├── README.md             This file
    └── IMPROVEMENT_NOTES.md  Known limitations and roadmap
```

## Module Responsibilities

### `config.py`
Loads configuration from `project_config.yml` (settings) and `.env` (API keys).
Validates all required fields on startup and provides typed property accessors.

### `models.py`
Five shared dataclasses (`MethodInfo`, `PropertyInfo`, `ClassInfo`, `FileInfo`,
`ProjectInfo`) used across parsing, generation, and output sub-packages.

### `parsing/parser.py`
`CodeParser` -- regex-based extraction of namespaces, classes, properties,
methods (with signatures and line numbers), and simple call chains from C#
source files. Delegates classification to `FileClassifier`.

### `parsing/classifier.py`
`FileClassifier` -- config-driven file categorisation using regex patterns
from YAML. Also builds source URLs for GitHub/GitLab/Bitbucket.

### `llm/adapters.py`
`BaseLLMAdapter` interface + concrete adapters (OpenAI, Claude, Azure) +
`LLMFactory`. All parameters read from config.

### `llm/prompts.py`
Prompt template functions (handler, query, feature, aggregate, simple,
infrastructure, overview) plus the system prompt and `CATEGORY_TO_PROMPT`
mapping. Infrastructure categories (`entity_configuration`, `repository`,
`db_context`) are mapped to the `infrastructure_doc` prompt type.

### `generation/orchestrator.py`
`DocumentationGenerator` -- the main pipeline: parse source, group by category,
select prompt template, make targeted LLM calls, collect results.

### `generation/context.py`
`ContextBuilder` -- file grouping, class metadata formatting, handler context
building, feature detection, and template key mapping. Pure data transformation
with no LLM interaction.

### `output/assembler.py`
`DocumentAssembler` -- writes generated markdown to disk, resolves
`{ref:ClassName}` cross-reference placeholders, delegates nav to NavigationBuilder.

### `output/navigation.py`
`NavigationBuilder` -- generates hierarchical `nav:` in mkdocs.yml from flat
file paths. **Merges** new API entries into existing nav (so running for
Ordering then Catalog preserves both). Preserves all non-nav mkdocs settings.

### `output/link_resolver.py`
`LinkResolver` -- post-generation pass that validates and repairs links in
generated markdown files:
- Builds an inventory of all generated files and their headings.
- Resolves broken internal cross-page links to correct relative paths
  with MkDocs-compatible anchor slugs.
- Scans the repository `src/` directory to build a source file index.
- Validates GitHub source URLs (both markdown links and Mermaid `click`
  directives) against actual files on disk. Corrects wrong paths or removes
  links to non-existent files.
- Replaces placeholder `your-repo` URLs with the configured repository URL.
- Strips invalid `#L<n>` line-number-only anchors from markdown links.

### `output/clean.py`
Standalone utility module (runnable via `python -m doc_generator.output.clean`)
that reads API configuration from `project_config.yml` and removes the
corresponding generated directories and overview files from the docs output.
Supports `--dry-run` to preview what would be deleted.

## CLI Flags

| Flag | Purpose |
|------|---------|
| `--api <key>` | Which API to generate (from `project_config.yml`) |
| `--list` | List available APIs and exit |
| `--dry-run` | Parse/classify only, no LLM calls |
| `--clean` | Remove stale generated files for the target API before writing |
| `--config <path>` | Path to a custom `project_config.yml` |

## Extending

### Add a new classification rule
Edit `classification_rules` in `project_config.yml`:
```yaml
- pattern: ".*Service\\.cs$"
  category: "service"
  doc_file: "Services.md"
  doc_title: "Services"
```

### Add a new prompt template type
1. Add a function in `llm/prompts.py`
2. Map the new category to the prompt type in `CATEGORY_TO_PROMPT`
3. Add a template example path in `project_config.yml` under `template_examples`

### Add a new LLM provider
1. Create a new adapter class extending `BaseLLMAdapter` in `llm/adapters.py`
2. Add a branch in `LLMFactory.create()`
3. Add the API key property in `config.py`
