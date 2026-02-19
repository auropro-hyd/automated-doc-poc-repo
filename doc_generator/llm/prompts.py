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

_DETAIL_LEVEL_INSTRUCTIONS = {
    "detailed": (
        "Generate DETAILED and ELABORATIVE documentation -- never a summary. "
        "For every overview section, write at least 3-4 sentences explaining the "
        "class's purpose, the business problem it solves, how it collaborates with "
        "other components, and the interfaces or contracts it fulfils. "
        "For every method, describe its parameters, return values, side effects, "
        "and exception scenarios in full sentences. "
        "For every diagram legend entry, explain WHAT happens at that step and WHY, "
        "not just the method name. "
        "Match the reference template's LENGTH AND DEPTH, not just its format."
    ),
    "standard": (
        "Generate clear and informative documentation with moderate detail. "
        "Provide meaningful descriptions for each class and method."
    ),
    "summary": (
        "Generate concise summary documentation. Keep descriptions brief -- "
        "one to two sentences per section."
    ),
}


def get_system_prompt(detail_level: str = "detailed") -> str:
    """Build the system prompt, adapting verbosity to the configured detail level."""
    base = (
        "You are an expert technical documentation writer. "
        "Your task is to analyse source code and generate structured documentation "
        "in Markdown format. Follow the provided template example EXACTLY in terms "
        "of heading hierarchy, Mermaid diagram syntax, expandable section format, "
        "table structure, and link conventions. Be precise with class names, method "
        "signatures, and line numbers from the source code. "
    )
    detail = _DETAIL_LEVEL_INSTRUCTIONS.get(
        detail_level, _DETAIL_LEVEL_INSTRUCTIONS["detailed"]
    )
    return base + detail


SYSTEM_PROMPT = get_system_prompt("detailed")

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
    """Wrap a template example with clear delimiters, or return empty.

    The full reference template is always passed to the LLM so it can
    learn the expected level of detail from the complete example. The
    largest template (~22K chars / ~6K tokens) is trivial relative to
    modern context windows (128K+).
    """
    if not example:
        return "(No reference template available -- generate from the structural instructions above.)"
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
A detailed, multi-sentence description explaining the class's purpose, the business
problem it solves, all collaborators it depends on and how they interact, and the
interfaces or contracts it implements. Mention the command/request model used as input.

### Handle  (or the primary method name)
**Overview:**
Detailed method description including parameters with their types and purpose,
return type and what it represents, async behaviour, and any side effects
(e.g., domain events raised, integration events published).

**Call Graph:**
```mermaid
flowchart LR
    A([ClassName.MethodName]) --> B([Dependency.Method])
    B --> C([Another.Method])
```

??? Call Graph Legend
    - **ClassName.MethodName** - [link to section] -- explain what this step does and why
    - **Dependency.Method** - [link to related doc page] -- explain the purpose of this call

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
- Overview sections MUST be detailed (3-4 sentences minimum), never just one line

## Reference template (match this format AND level of detail exactly):

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
Detailed explanation of the query class's purpose, what data it retrieves, how it
relates to the command side of the CQRS pattern, which repositories or data sources
it depends on, and the return value semantics.

---

### Methods

#### MethodName
**Overview:** Detailed description including parameters with types and purpose,
return type and what it represents, data retrieval logic, and exception scenarios.

**Call Graph:**
```mermaid
flowchart LR
    A([ClassName.Method]) --> B([Dependency.Method])
```

??? Call Graph Legend
    - links to related docs -- explain what each call does and why

**Implementation flow:**
```mermaid
flowchart LR
    S([Start]) --> P1([Step]) --> E([Return])
```

**Exceptions:**
- bullet list of exception scenarios with causes and expected behavior

---

??? Usage Example
    ```csharp
    // usage
    ```

## CRITICAL FORMAT RULES:
- Use `flowchart LR` with rounded nodes `([text])`
- Use `???` for expandable sections
- Document ALL public methods
- Overview sections MUST be detailed (3-4 sentences minimum)

## Reference template (match this format AND level of detail):

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
Detailed feature description: explain the business purpose, the user story or workflow
it enables, the HTTP method and endpoint path, request/response models, and how the
feature fits into the broader system architecture. Write at least 3-4 sentences.

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
    - **1. HTTP request** - [link to source with line number] -- explain what data is sent and why
    - **2. Send command** - [link to command model] -- explain what the command carries
    (numbered list matching diagram steps -- each entry explains WHAT happens and WHY)

## Dependencies
- bullet list of dependent components with cross-page links and a sentence explaining each dependency's role

??? Notes
    - business context notes with detailed explanation

## Exception Handling
- bullet list of error scenarios with causes, HTTP status codes, and expected behavior

## Security Considerations
- bullet list of security measures with explanation of what each protects against

## CRITICAL FORMAT RULES:
- Use `sequenceDiagram` syntax (not flowchart)
- Number the steps in the diagram
- Legend entries match step numbers with links AND explanations
- Use `???` for expandable sections
- Overview MUST be detailed (3-4 sentences minimum)

## Reference template (match this format AND level of detail):

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
Detailed multi-sentence description explaining the aggregate's role in the domain model,
the business invariants it protects, its relationship to other aggregates and entities,
and the bounded context it belongs to.

**Properties:**

| Property | Description | Mandatory |
|:---------|:------------|:---------:|
| Id       | Detailed description of business meaning and validation rules | Yes       |

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
- Operation description explaining preconditions, postconditions, and domain events raised (raises [EventName](link))

[View on GitHub]({{source_url}})

---

## CRITICAL FORMAT RULES:
- Use `classDiagram` syntax
- Use `link ClassName "url" "tooltip"` for clickable class nodes
- Property tables with three columns: Property, Description, Mandatory
- Property descriptions MUST explain business meaning, not just type info
- List domain operations with preconditions, postconditions, and links to domain event docs
- Separate aggregates with `---`
- Overview sections MUST be detailed (3-4 sentences minimum)

## Reference template (match this format AND level of detail):

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
Thorough description including the class's role in the domain, its relationships
to other components, typical usage patterns, and any important constraints or
conventions. Write at least 2-3 sentences.

**Properties:** (if the class has public properties)

| Property | Description | Mandatory |
|:---------|:------------|:---------:|
| Prop     | Description explaining business meaning | Yes/No    |

[View on GitHub]({{source_url}})

---

## CRITICAL FORMAT RULES:
- Include property tables ONLY if the class has meaningful properties
- Group related classes under category headers if appropriate
- Separate classes with `---`
- Overview sections should be informative and explain purpose, not just repeat the class name

## Reference template (match this format AND level of detail):

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
Detailed description explaining what domain concepts this class supports, how it
integrates with the persistence layer, and its role in the infrastructure architecture.
Write at least 3-4 sentences.

**Methods:**

### [MethodName]({{source_url_with_line}})

- **Overview:** Detailed step-by-step description of what the method does, including
  parameters, return values, and side effects
- **Exceptions:** List of exception cases with causes and expected behavior
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
- Document ALL public methods with detailed descriptions
- Include exception scenarios with causes and resolutions
- Separate classes with `---`
- Overview sections MUST be detailed (3-4 sentences minimum)

## Reference template (match this format AND level of detail):

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
- Comprehensive description covering business motivation, user stories addressed, and architectural decisions
- Business motivation (3-4 detailed bullets explaining WHY each aspect matters)
- Key stakeholders and their concerns

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
- All sections MUST be elaborative and detailed, not summaries

## Reference template (match this format AND level of detail):

{example_block}

## Component Summary:
{component_summary}

## Source Code:

{source_code}

Generate the complete overview documentation for "{api_name}" now:"""
