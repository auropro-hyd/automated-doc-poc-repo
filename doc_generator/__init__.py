"""Automated Documentation Generator.

A config-driven tool that parses source code, generates structured
documentation via LLM, and produces MkDocs-compatible markdown files
with Mermaid diagrams, cross-page navigation, and clickable source links.

Package structure::

    doc_generator/
    ├── cli.py              CLI entry point
    ├── config.py           Configuration loader (YAML + .env)
    ├── models.py           Shared data classes
    ├── parsing/            Source code parsing and classification
    ├── llm/                LLM adapters and prompt templates
    ├── generation/         Orchestration and context building
    ├── output/             File assembly and MkDocs navigation
    └── docs/               Package documentation
"""

__version__ = "2.2.0"
