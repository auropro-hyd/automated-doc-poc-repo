"""Prompt templates for LLM-driven documentation generation.

Design decision: Templates are plain Python format-strings keyed by
documentation category. Each template is generic (no repo-specific text)
and accepts a ``template_example`` parameter -- a concrete reference
document loaded from ``template_examples`` in project_config.yml. This
few-shot approach lets the LLM match the exact output format without
embedding format rules in code.

When switching repositories, the user simply updates the
``template_examples`` paths in the YAML (or sets them to null to let the
LLM generate from the structural instructions alone).
"""

from typing import Optional

# ---------------------------------------------------------------------------
# System prompt (shared across all template types)
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = (
    "You are an expert technical documentation writer. "
    "Your task is to analyse source code and generate structured documentation "
    "in Markdown format. Follow the provided template example EXACTLY in terms "
    "of heading hierarchy, Mermaid diagram syntax, expandable section format, "
    "table structure, and link conventions. Be precise with class names, method "
    "signatures, and line numbers from the source code."
)

# ---------------------------------------------------------------------------
# Category -> prompt-type mapping
# ---------------------------------------------------------------------------

# Maps classification categories to the prompt template key.
# Multiple categories can share a template.
CATEGORY_TO_PROMPT: dict = {
    "command_handler": "handler_doc",
    "domain_event_handler": "handler_doc",
    "integration_event_handler": "handler_doc",
    "query": "query_doc",
    "validator": "handler_doc",
    "extension": "infrastructure_doc",
    "entity_configuration": "infrastructure_doc",
    "repository": "infrastructure_doc",
    "db_context": "infrastructure_doc",
    "aggregate": "aggregate_doc",
    "api_endpoint": "feature_doc",
    "model": "simple_doc",
    "other": "simple_doc",
}

# ---------------------------------------------------------------------------
# Prompt templates
# ---------------------------------------------------------------------------


def _wrap_example(example: Optional[str]) -> str:
    """Wrap a template example with clear delimiters, or return empty."""
    if not example:
        return "(No reference template available -- generate from the structural instructions above.)"
    # Truncate very large examples to keep within token budget.
    max_chars = 6000
    if len(example) > max_chars:
        example = example[:max_chars] + "\n\n... (truncated for brevity)"
    return (
        "--- BEGIN REFERENCE TEMPLATE ---\n"
        f"{example}\n"
        "--- END REFERENCE TEMPLATE ---"
    )


def handler_doc_prompt(
    *,
    doc_title: str,
    source_code: str,
    class_metadata: str,
    template_example: Optional[str] = None,
) -> str:
    """Build a prompt for handler-style documentation.

    Used for command handlers, domain event handlers, integration event
    handlers, and validators. Produces per-class sections with Call Graph,
    Implementation Flow, and expandable legends.
    """
    example_block = _wrap_example(template_example)
    return f"""Generate documentation for the following source code.

## Output Structure (per class/handler found in the source)

For EACH class, produce a section like this:

## [ClassName]({{source_url}})

**Overview:**
A paragraph describing the class purpose, collaborators, and interfaces implemented.

### Handle  (or the primary method name)
**Overview:**
Method description with parameters and return type.

**Call Graph:**
```mermaid
flowchart LR
    A([ClassName.MethodName]) --> B([Dependency.Method])
    B --> C([Another.Method])
```

??? Call Graph Legend
    - **ClassName.MethodName** - [link to section]
    - **Dependency.Method** - [link to related doc page]

**Implementation flow:**
```mermaid
flowchart LR
    S([Start]) --> P1([Step 1])
    P1 --> D1{{Decision?}}
    D1 -- Yes --> E1([Outcome A])
    D1 -- No --> P2([Step 2])
    P2 --> E2([Return result])
```

??? Usage Example
    ```csharp
    // brief usage snippet
    ```

---

## CRITICAL FORMAT RULES:
- Use `flowchart LR` (not `graph LR`)
- Use rounded nodes: `([text])` for processes, `{{text}}` for decisions
- Use `???` (three question marks + space) for expandable sections
- Separate classes with `---`
- Link class headers to source URL
- Include ALL classes found in the source -- do not skip any

## Reference template (match this format exactly):

{example_block}

## Class Metadata:
{class_metadata}

## Source Code:

{source_code}

Generate the complete "{doc_title}" documentation now:"""


def query_doc_prompt(
    *,
    doc_title: str,
    source_code: str,
    class_metadata: str,
    template_example: Optional[str] = None,
) -> str:
    """Build a prompt for query-style documentation."""
    example_block = _wrap_example(template_example)
    return f"""Generate documentation for query classes.

## Output Structure (per class):

## [ClassName]({{source_url}})

### Overview
Class description.

---

### Methods

#### MethodName
**Overview:** Description with parameters, return type, exceptions.

**Call Graph:**
```mermaid
flowchart LR
    A([ClassName.Method]) --> B([Dependency.Method])
```

??? Call Graph Legend
    - links to related docs

**Implementation flow:**
```mermaid
flowchart LR
    S([Start]) --> P1([Step]) --> E([Return])
```

**Exceptions:**
- bullet list of exception scenarios

---

??? Usage Example
    ```csharp
    // usage
    ```

## CRITICAL FORMAT RULES:
- Use `flowchart LR` with rounded nodes `([text])`
- Use `???` for expandable sections
- Document ALL public methods

## Reference template:

{example_block}

## Class Metadata:
{class_metadata}

## Source Code:

{source_code}

Generate the complete "{doc_title}" documentation now:"""


def feature_doc_prompt(
    *,
    feature_name: str,
    source_code: str,
    handler_info: str,
    template_example: Optional[str] = None,
) -> str:
    """Build a prompt for API feature page documentation.

    Produces a page with a sequence diagram, legend, dependencies, notes,
    exception handling, and security considerations.
    """
    example_block = _wrap_example(template_example)
    return f"""Generate documentation for the API feature: {feature_name}

## Output Structure:

# {feature_name}

## Overview
Feature description paragraph.

## Sequence Diagram
```mermaid
sequenceDiagram
    participant Client
    participant ApiEndpoint
    participant MediatR
    participant Handler
    participant Repository
    participant Database

    Client->>ApiEndpoint: 1. HTTP request
    ApiEndpoint->>MediatR: 2. Send command
    MediatR->>Handler: 3. Handle
    Handler->>Repository: 4. Persist
    Repository->>Database: 5. Save
    Database-->>Repository: 6. Result
    Repository-->>Handler: 7. Result
    Handler-->>MediatR: 8. Result
    MediatR-->>ApiEndpoint: 9. Result
    ApiEndpoint-->>Client: 10. HTTP response
```

??? Sequence Diagram Legend
    - **1. HTTP request** - [link to source with line number]
    - **2. Send command** - [link to command model]
    (numbered list matching diagram steps)

## Dependencies
- bullet list of dependent components with cross-page links

??? Notes
    - business context notes

## Exception Handling
- bullet list of error scenarios

## Security Considerations
- bullet list of security measures

## CRITICAL FORMAT RULES:
- Use `sequenceDiagram` syntax (not flowchart)
- Number the steps in the diagram
- Legend entries match step numbers with links
- Use `???` for expandable sections

## Reference template:

{example_block}

## Related Handlers and Models:
{handler_info}

## Source Code:

{source_code}

Generate the complete documentation for "{feature_name}" now:"""


def aggregate_doc_prompt(
    *,
    doc_title: str,
    source_code: str,
    class_metadata: str,
    template_example: Optional[str] = None,
) -> str:
    """Build a prompt for domain aggregate documentation.

    Produces property tables, class diagrams with link directives, legends,
    and domain operation lists.
    """
    example_block = _wrap_example(template_example)
    return f"""Generate documentation for domain aggregates.

## Output Structure (per aggregate/entity):

## EntityName (Aggregate)

**Overview:**
Description paragraph.

**Properties:**

| Property | Description | Mandatory |
|:---------|:------------|:---------:|
| Id       | Description | Yes       |

**Class Diagram:**
```mermaid
classDiagram
  class EntityName {{
    +Property1
    +Property2
  }}
  class RelatedEntity {{
    +Prop
  }}
  EntityName "1" --|> "*" RelatedEntity : relationship
  link EntityName "{{source_url}}" "EntityName source code"
  link RelatedEntity "{{source_url}}" "RelatedEntity source code"
```

**Legend:**
- **EntityName**: [Documentation link]

**Domain Operations:**
- Operation description (raises [EventName](link))

[View on GitHub]({{source_url}})

---

## CRITICAL FORMAT RULES:
- Use `classDiagram` syntax
- Use `link ClassName "url" "tooltip"` for clickable class nodes
- Property tables with three columns: Property, Description, Mandatory
- List domain operations with links to domain event docs
- Separate aggregates with `---`

## Reference template:

{example_block}

## Class Metadata:
{class_metadata}

## Source Code:

{source_code}

Generate the complete "{doc_title}" documentation now:"""


def simple_doc_prompt(
    *,
    doc_title: str,
    source_code: str,
    class_metadata: str,
    template_example: Optional[str] = None,
) -> str:
    """Build a prompt for simple documentation (models, value objects, etc.).

    Produces lightweight docs: overview, optional property table, GitHub link.
    """
    example_block = _wrap_example(template_example)
    return f"""Generate documentation for the following classes.

## Output Structure (per class):

## ClassName

**Overview:**
Brief description paragraph.

**Properties:** (if the class has public properties)

| Property | Description | Mandatory |
|:---------|:------------|:---------:|
| Prop     | Description | Yes/No    |

[View on GitHub]({{source_url}})

---

## CRITICAL FORMAT RULES:
- Keep descriptions concise
- Include property tables ONLY if the class has meaningful properties
- Group related classes under category headers if appropriate
- Separate classes with `---`

## Reference template:

{example_block}

## Class Metadata:
{class_metadata}

## Source Code:

{source_code}

Generate the complete "{doc_title}" documentation now:"""


def infrastructure_doc_prompt(
    *,
    doc_title: str,
    source_code: str,
    class_metadata: str,
    template_example: Optional[str] = None,
) -> str:
    """Build a prompt for infrastructure documentation (repos, configs, services)."""
    example_block = _wrap_example(template_example)
    return f"""Generate documentation for infrastructure/service classes.

## Output Structure (per class):

## [ClassName.cs]({{source_url}})

**Overview:**
Description with links to domain concepts this class supports.

**Methods:**

### [MethodName]({{source_url_with_line}})

- **Overview:** Description
- **Exceptions:** List of exception cases
- **Flow Diagram:** (if method has meaningful logic)

```mermaid
flowchart LR
    S([Start]) --> P1([Step]) --> E([Return])
    click P1 "{{source_url}}" "Description"
```

---

## CRITICAL FORMAT RULES:
- Use `flowchart LR` or `flowchart TD` for flow diagrams
- Use `click` directives to link diagram nodes to source
- Document ALL public methods
- Include exception scenarios
- Separate classes with `---`

## Reference template:

{example_block}

## Class Metadata:
{class_metadata}

## Source Code:

{source_code}

Generate the complete "{doc_title}" documentation now:"""


def overview_doc_prompt(
    *,
    api_name: str,
    component_summary: str,
    source_code: str,
    template_example: Optional[str] = None,
) -> str:
    """Build a prompt for the API-level overview page."""
    example_block = _wrap_example(template_example)
    return f"""Generate an overview documentation page for: {api_name}

## Output Structure:

# {api_name} Documentation

## Sequence Diagram
(Full system-level flow showing Client -> API -> MediatR -> Handlers -> Domain -> Database)

## Class Diagram
(Key domain model relationships)

## 1. Feature Overview
- Brief summary
- Business motivation (3-4 bullets)
- Key stakeholders

## 2. Business Implementation Details
- Business rules (numbered)
- Assumptions and constraints

## 3. Technical Implementation Details
- API endpoints with HTTP methods and paths
- Key components (numbered list)
- Request/response examples

## 4. Validation and Error Handling
## 5. Security and Access Control
## 6. Testing Strategy
## 7. Deployment Considerations
## 8. References
- Links to key source files and related documentation

## CRITICAL FORMAT RULES:
- Use `sequenceDiagram` for the system flow
- Use `classDiagram` with `link` directives for the class diagram
- Number all sections
- Include realistic examples

## Reference template:

{example_block}

## Component Summary:
{component_summary}

## Source Code:

{source_code}

Generate the complete overview documentation for "{api_name}" now:"""
