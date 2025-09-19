---
mode: 'agent'
description: 'Analyze the selected project and determine the documentation order of the classes and other aspects.'
---

Project Name: ${input:projectName: name of the library}

Check if the user provided the project name explicitly in the prompt. If not, ask user to provide the project name. DO NOT infer from the context.
Follow below steps to arrive at the classification order & dependency graph of classes in the projectName for developer documentation:
1. Create a file if not exists  in `.github/scratchpad/` named `<projectName>-classify.md` (e.g., `Ordering.Infrastructure-classify.md`)
2. Create classification list section & class dependency graph section in the file if not exists.
3. Iterate through the .cs files folder by folder covering all the folders in the projectName one by one and perform below steps for each file & remember the analysis for later steps:
    - Identify the primary responsibility of the class (e.g., Configuration, Data Interactions, Services, Migrations, etc.).
    - Note any dependencies on other classes within the project either as a property or through constructor injection or method parameters or any other way possible in C#.
    - Determine if the class fits into one of the predefined categories (Services, Mappers, Data Interactions, Configuration, Caching, Messaging, Serialization, Validation, Logging/Observability, Adapters (External Integrations)). If not, create a new category that accurately describes its role.
4. List all classes/interfaces in a dependency-aware sequence in classification list section as a numbered list: first those with no dependencies, then those whose dependencies are already listed, in order. each entry should be in one line containing .cs file name, category type, and dependencies (if any) & number of lines.
5. Create a dependency graph in dependency graph section using Mermaid syntax, placing classes with no dependencies at the top and those with the most dependencies at the bottom.
Note - Do not include test files or auto-generated files or files from obj folder or .csproj in this analysis.
DO NOT write the thinking process in the response. Only provide the confirmation or review text after performing all the steps mentioned above.
