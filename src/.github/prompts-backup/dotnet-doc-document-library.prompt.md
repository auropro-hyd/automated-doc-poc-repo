---
mode: 'agent'
description: 'Generate a documentation for a library file as part of developer documentation.'
---
Name of the Library: ${input:library-name: name of the library}
ordered list of class classifications: ${input:ordered-list-of-class-classifications: ordered list of class classifications}

Follow the ordered structure ordered-list-of-class-classifications when generating documentation for library-name project. The documentation should be created in docs/docs/<library-name> (create the folder if it does not already exist).
Identify the classification types from the provided list and create one file named <classification>.md for each group in the folder. The order of documentation must follow the order of the classification list.
For every class or interface, create a section in its respective markdown file containing, gather the information & generate for each class covering below aspects step by step without missing any details before moving onto other class:
- Overview: 2–3 sentences explaining the purpose and role of the class.
- Methods: A subsection for each method. For each method:
    - Overview: 1–3 sentences explaining its purpose and usage.
    - Call Graph: if the method calls other functions or lambdas, generate a Mermaid flowchart (flowchart LR) showing all subsequent calls. Each node must link back to the relevant markdown documentation section. If it's lambda, point to the github link pointing to the lambda implementation. 
    - Flow Diagram: if the implementation contains branching, workflows, or processing logic, generate a flowchart describing the critical functionality for clarity. Each node must include a GitHub link to the relevant line number. Include a description after the diagram explaining the flow. 
    - Exceptions: a subsection describing possible exceptions, why they occur, and when they are thrown.
    - Configuration: if the method or class uses configuration values, include a table describing the keys, defaults, and effects.
In addition, include any other sections that would help newly onboarded developers quickly understand and use the library (e.g., threading considerations, lifecycle rules, usage examples). 
NOTE- include the sections only if they are relevant to the class or method. do not create empty sections.
The documentation must be clear, concise, and easy to understand, avoiding unnecessary jargon. 
Output - Perform the operations mentioned above and do not print your thinking process in the response chat.
