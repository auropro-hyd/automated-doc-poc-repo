---
mode: 'agent'
description: 'Generate the overview section from the draft documentation files.'
---

Name of the Project: ${input:projectName: name of the .NET project}
You are a coding agent tasked with generating developer documentation for a .NET project.
Read all the markdown files in the `docs/docs/<project-name>/` folder & <project-name>-classify.md file in the `.github/scratchpad/` folder. Create an overview markdown file named `Overview.md` in the same folder with below sections:
 1. Overview - Write a 3-5 sentence overview explaining the purpose and role of the project and include key responsibilities, collaboration points (important dependencies), and any notable constraints.
 2. Analyze the <project-name>.csproj file and create Project dependency diagram showing the dependent libraries or projects using mermaid syntax with flow chart type TD notation. The diagram should illustrate the key dependencies and interactions between major components or modules within the project. The labels on the arrow should display the relationship with 1-2 words only. Ensure that each node in the diagram has a reference to the internal documentation.
 2. Check the project structure. If the project contains multiple folders, include fenced code block showing the project folder structure (exclude /obj folder) and provide a one-sentence explanation of what each directory in the fence block. 
 3. Class Relationship Diagram - Read the mermaid diagram in the classify file and include it in this section. Make sure the diagram has references to the respective github blob link for each node.
 4. Create a legend abomination section.
 5. Check method & class name section in `docs/docs` folder, if found add it to abomination section, else remove the entry from the abomination list. Example abomination section -
    ??? Legend
        - [MethodName](<link-to-method-in-markdown-file>)
        - [MethodName2](<link-to-method-in-markdown-file>)
- if no sections are found, remove the abomination section.
 6. Section that walk through the content covered in the doc-folder documentation, including references (links) to the respective markdown files for each area.

Output - Perform the operations mentioned above and do not print your thinking process in the response chat.