---
mode: 'agent'
description: 'Evaluate and correct call graphs & flow diagrams in the provided markdown file for accuracy and completeness.'
---
markdown file name: ${input:markdown: name of the markdown file to validate}
Context files: ${input:contextFiles: comma-separated list of relevant files/folders}

For each mermaid call graph or flow diagram in the markdown file, perform these steps:

1. Ensure each click directive links to the correct GitHub blob URL; if a line number is present, increment it by 5.
2. Verify each GitHub blob URL points to the correct file in the workspace; fix any incorrect paths to prevent 404 errors.
3. Confirm diagram legends reference the correct markdown sections; update if needed.
4. Validate mermaid syntax and fix any errors without removing content.

CONTEXT - contextFiles  
If context is missing, scan the workspace to resolve links and references.

*If you cannot fully validate all diagrams in one pass, note your progress for the next iteration.*

Provide only a brief summary of your actions, not the full reasoning process.