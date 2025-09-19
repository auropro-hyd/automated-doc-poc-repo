---
mode: 'agent'
description: 'Generate detailed mermaid diagrams for the call graph & flow chart data in the draft documentation files.'
---
Name of the Project: ${input:projectName: name of the .NET project}

You are a coding agent tasked with generating developer documentation for a .NET project.

Iterate through the markdown files in the `docs/docs/<project-name>/` folder. For each method section in the markdown files, perform below steps:

1. check if call graph section is available
    - if available-
        - read the call graph data and convert it into a mermaid call graph diagram with flow chart mermaid diagram type LR notation with method calls as nodes and directed edges representing the call relationships with labels explaining the relationship. ensure the diagram is clear and easy to understand. Add github link references to each method node in the diagram and references only if the implementation is part of the workspace.
        - insert the diagram in the call graph section replacing any existing diagram or text.
        - Create a legend abomination section.
        - Check method & class name section in `docs/docs` folder, if found add it to abomination section, else remove the entry from the abomination list. Example abomination section -
          ??? Call Graph Legend
              - **MethodName** - [Link to method in markdown file](<link-to-method-in-markdown-file>)
              - **MethodName2** - [Link to method in markdown file](<link-to-method-in-markdown-file>)
        - if no sections are found, remove the abomination section.
    - if not available, skip to next step
2. check if flow diagram section is available
    - if available-
        - read the flow diagram data and generate a mermaid flowchart diagram LR notation with nodes representing decision, process, start, and end points. use directed edges to illustrate the flow of logic and decision paths. ensure the diagram is clear and easy to understand. Add github link references to each node in the diagram pointing to the line number in the github repo.
        - insert the diagram in the flow diagram section replacing any existing diagram or text.

Output - Perform the operations mentioned above and do not print your thinking process in the response chat.