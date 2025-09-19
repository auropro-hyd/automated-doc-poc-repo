---
mode: 'agent'
description: 'Generate detailed documentation for the .cs files in a .NET project'
---
Name of the Project: ${input:projectName: name of the .NET project}
You are a coding agent tasked with generating developer documentation for a .NET project. 
1. retrieve and remember the documentation plan from the file `.github/scratchpad/<project-name>-doc-plan.md`.
2. For this prompt, focus on generating documentation for the first group of classes listed in the plan. In the next prompt iteration, you will handle the next group, and so on.
3. for each class in the current group, find the markdown file with the classification name in the `docs/docs/<project-name>/` folder. e.g. if the classification is "Services", look for `docs/docs/<project-name>/Services.md`. go to the section with the class name as the title and perform below steps
    - Read the class file from the project name folder in the workspace. e.g. if the project name is "OrderProcessor", read the class file from `<project-name>/` folder in the workspace. and analyze the class in detail to gather information for documentation described in below steps.
    - if the section name in the markdown file does not exist, create a section with the class name as the title and/or a github link reference pointing to the class in the repository. example - `## [ClassName](<link-to-class-in-repo>)`
    - Create overview section: Write a 2-3 sentence overview explaining the purpose and role of the class and include key responsibilities, collaboration points (important dependencies), and any notable constraints. if the class has a parent class, include that information in the overview and add link to the parent class documentation section if it exists else github repo link.
    - for each method, create a sub-section and include:
        - Overview: Write a 1-3 sentence overview explaining the purpose and usage of the method. include if it's private or public method, parameters, return type, or generic type details and any side effects in a cohesive explanation.
        - Call Graph: Read the method implementation line by line and identify all the method calls made within the method which includes direct, static, async & framework/external library method calls, do not include log statements & lambdas. Create a call data ensuring the order is followed as per the code execution. limit the call depth to 4 levels. the output should be list to ensure the call graph direction are preserved and each method entry should include the class name, method name, and a github link to the method in the repository. if the method calls another method within the same class, include that as well. if the method is an override or implements an interface method, include that as well.
        - Flow Diagram: If the implementation contains branching, workflows, or processing logic, map all the decision, processing & exception paths. record the information as a flow information with each node name, type (decision, process, start, end), decision paths and github link. In a separate paragraph describe the flow in a cohesive manner.
        - Exceptions: If there is an explicit exception throw statement or implicit exceptions interpreted then Create a subsection describing possible exceptions, why they occur, and when they are thrown.
        - Configuration: If the method or class uses configuration values, include a table describing the keys, defaults, and effects.
        - If Any other relevant sections that would help newly onboarded developers quickly understand and use the class (e.g., threading considerations, lifecycle rules, usage examples). add them as abomination sections.

Abomination example:
??? This is an example of abomination section.

NOTE - If it's interface, include the interface & method overviews only. Do not include call graph, flow diagram, exceptions, configuration, or other sections. 
documentation should be clear, concise, and easy to understand, avoiding unnecessary jargon.
Output - Perform the operations mentioned above and do not print your thinking process in the response chat.

