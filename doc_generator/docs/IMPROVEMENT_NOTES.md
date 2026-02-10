# Improvement Notes - Documentation Generator v2.1

## Current State

The documentation generator is a codebase-agnostic, config-driven tool.
End-to-end generation for Ordering.API produces 19 documentation files
matching the v1 template format. v2.1 addressed 8 audit findings.

## Changes in v2.1

| # | Issue | Fix |
|---|-------|-----|
| 1 | Template files overwritten by generated output | Templates moved to `src/docs/templates/reference_docs/`; generated output writes to `src/docs/docs/` (gitignored) |
| 2 | Hardcoded `feature_subfolder: "OrdersApi"` | Auto-detected from endpoint class name (e.g., `OrdersApi`, `CatalogApi`) |
| 3 | Source URL paths missing project prefix | `build_class_metadata` now receives `project_source_prefix` for correct repo-relative URLs |
| 4 | Nav replacement destroying other APIs | `NavigationBuilder` now **merges** new nav entries into existing ones |
| 5 | `index.md` wiped by nav rebuild | Merge logic preserves `Home` entry; `.gitignore` keeps `index.md` tracked |
| 6 | No way to remove stale files | `--clean` flag + `make regenerate` remove old output before writing |
| 7 | Feature keywords hardcoded in Python | Moved to `feature_detection.feature_keywords` in `project_config.yml` |
| 8 | No warning for missing source paths | Config validation now warns if source/template paths don't exist on disk |

## Known Limitations

### Code Parser
1. **Regex-based parsing**: Cannot handle all C# syntax variations (e.g.,
   file-scoped namespaces, primary constructors, records with positional
   parameters). Complex call chains (LINQ, lambdas) are delegated to the LLM.
2. **False negatives**: Some classes with non-standard formatting (e.g.,
   generic type declarations spanning multiple lines) may not be captured.
3. **No semantic analysis**: The parser does not resolve types or understand
   inheritance chains beyond simple base class names.

### LLM Output
4. **Mermaid syntax**: Occasional LLM-generated Mermaid syntax errors despite
   few-shot examples. Common issues: unescaped special characters, missing
   closing tags.
5. **Line number accuracy**: Line numbers in source URLs depend on regex
   match accuracy, which may be off by 1-2 lines for some declarations.
6. **Hallucinated cross-references**: The LLM may reference classes or methods
   that don't exist or use incorrect anchor names.

## Potential Improvements

### Short-term
- Add a post-processing step to validate Mermaid diagram syntax
- Add a link validator to check cross-page references
- Add support for file-scoped namespaces (`namespace X;` syntax)

### Medium-term
- Replace keyword-based feature detection with endpoint-pattern analysis
- Add incremental generation (only regenerate changed files)
- Add output comparison tool (diff against v1 template)
- Support chunking of large source files for token-budget management

### Long-term
- Multi-language support (Java, Python, TypeScript parser extensions)
- AST-based parsing for deeper code analysis
- CI/CD integration for auto-generation on code changes
- Watch mode for real-time documentation updates
