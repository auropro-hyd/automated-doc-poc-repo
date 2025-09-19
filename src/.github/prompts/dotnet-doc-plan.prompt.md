---
mode: 'agent'
description: 'Plan the documentation grouping of .cs files'
---
Classification file : ${input:classification-file: classification file created in the previous step}

1. Read the classification file and the ordered list of class classifications.
2. create a grouping plan for the classes to document them in batches. below is the grouping logic.
    - iterate through the ordered list of class classifications in the same order.
        - count the line numbers of a current class.
        - create a numbered group starting from 1.
        - count the line number of the current class. if the total line numbers(current+previous class) is less than or equal to 1000, add to the current group. else, create a new group and add the current class to the new group.
3. output the grouping plan in markdown format with the following structure.
    - # <project-name> Documentation Plan
    - ## Group <group-number>
        - 1. **<class-name>** (<classification>) - <github-link-reference>
        - 2. **<class-name>** (<classification>) - <github-link-reference>
        - ...
    - ## Group <group-number>
        - 1. **<class-name>** (<classification>) - <github-link-reference>
        - 2. **<class-name>** (<classification>) - <github-link-reference>
        - ...
    - ...
4. Save the output of step 3 to a markdown file named `<project-name>-doc-plan.md` in the `.github/scratchpad/` folder.