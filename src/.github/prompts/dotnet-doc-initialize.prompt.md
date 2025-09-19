---
mode: 'agent'
description: 'Analyze the selected project and initialize the documentation process of the classes and other aspects.'
---
Classification file : ${input:classification-file: classification file created in the previous step}

1. Read the classification file and extract the project name and the ordered list of class classifications.
2. create a folder in `docs/docs/` named `<project-name>` (create the folder if it does not already exist).
3. create one file named `<classification>.md` for each group in the folder. The order of documentation must follow the order of the classification list.
4. In each markdown file, for each class in a classification, create a section containing the name of the class as the title only. section name must have a github link reference pointing to the class in the repository.

DO NOT Output thinking process, only output the completion message after completing above steps.

