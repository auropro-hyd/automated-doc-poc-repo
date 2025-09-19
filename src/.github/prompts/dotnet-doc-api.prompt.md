---
mode: 'agent'
description: 'Generate api feature documentation for the .NET project  using the existing docs/docs/<project-name>/*.md files as reference'
---

You are a coding agent tasked with generating developer documentation for a .NET project. You will use the existing documentation files located in `docs/docs/<project-name>/*.md` as references to create comprehensive API feature documentation. Your goal is to ensure that the generated documentation is consistent with the existing materials and provides clear, actionable information for developers working with the API.
1. Iterate through the controller files in the `<project-name>/Apis/` folder in the workspace.
2. For all the controller files, identify the unique features they belong to based on the route attributes and method names.
3. For each identified feature, check if any dependencies are used from other folders in the project like Services, Models, Commands, Queries, Events, Extensions etc. and gather information about those dependencies from the respective markdown files in the `docs/docs/<project-name>/` folder.
4. Create a new markdown file named `docs/docs/<project-name>/<ApiName>/<FeatureName>.md for each feature.
5. In the feature markdown file, include the following sections:
    - Overview: A brief description of the feature, its purpose, and its role within the API.
    - Sequence diagram: A mermaid sequence diagram visual representation of the sequence of operations involved in the feature, including interactions with other components or services. number each step in the sequence diagram.
    - Sequence Diagram Legend: A legend with each numbered step linking to relevant documentation sections for each component or service involved.
    Example:
    ??? Sequence Diagram Legend
        - **1. ComponentA.MethodX** - [ComponentA.MethodX](#componentamethodx)
        - **2. ComponentB.MethodY** - [ComponentB.MethodY](#componentbmethody)
    - Implementation Flow: A mermaid flowchart diagram illustrating the implementation flow of the feature, highlighting key decision points and processes.
    - Implementation Flow Legend: A legend with each step linking to relevant documentation sections for each component or service involved.
    Example:
    ??? Implementation Flow Legend
        - **1. ComponentA.MethodX** - [ComponentA.MethodX](#componentamethodx)
        - **2. ComponentB.MethodY** - [ComponentB.MethodY](#componentbmethody)
    - Pseudo Code - A simplified representation of the feature's logic and flow using pseudo code. Ensure that the pseudo code is clear and easy to understand, focusing on the main operations and decision points.
    - Dependencies: A list of key dependencies used by the feature, including services, models, commands, queries, and events. For each dependency, provide a brief description and a link to its documentation section if available.

NOTE: Ensure to consider the context provided in the existing documentation files to capture the specific details and nuances of each feature accurately. The generated documentation should be clear, concise, and useful for developers who will be using or maintaining the API.Ensure that all links in the documentation are correctly formatted and point to the appropriate sections within the