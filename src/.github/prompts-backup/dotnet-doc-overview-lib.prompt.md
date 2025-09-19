---
mode: 'agent'
description: 'Generate a overview documentation for a library file as part of developer documentation.'
---
library documentation folder path: ${input:doc-folder:provide for the folder name of the library documentation}
In `./docs/docs/doc-folder`, create an Overview page. Scan the markdown files in the `./docs/docs/doc-folder` directory and summarize their content. Begin with 3–4 sentences explaining the overall purpose of the domain & the capabilities. If the project structure include one or more folders then Include a short overview of how the project is organized, followed by a fenced code block showing the project structure and provide a one-sentence explanation of what each directory in the fence block.
Add the file dependency diagram from library specific classify file & add click directives to each node pointing to the respective github blob link for each node.
After this, add subsequent sections that walk through the content covered in the doc-folder documentation, including references (links) to the respective markdown files for each area.