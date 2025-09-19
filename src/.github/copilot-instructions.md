### Mermaid Diagram instructions
This instruction should applied for the tasks related to generating call graphs,dependency diagrams & flow diagrams - Always use mermaid tool in agent mode to make sure that the diagram generation aligns with mermaid syntax.Use mermaid validation tool to validate the generated diagram before giving the response. Always include labels for arrows with 2 words or less to indicate the relationship. for flow charts & dependency graphs, add click directive to each node to link to the relevant code definition as mentioned in the section below.

### Adding links to code definitions
As part of document generation - Use the repository prefix - https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/
Always link to definitions using blob URLs with #L<line> (or #L<start>-L<end> for multi-line signatures) using prefix https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src, and always point to definitions only

### Adding Links to other documentation files
Use relative links for internal documentation files. For example, if linking to a file named `utility.md` in the same directory, use `[Utilities](./utility.md)`.

### Markdown documentation practices

When writing or editing markdown documentation, please follow these best practices to ensure clarity, consistency, and maintainability:

1. **Headings**

   * Always leave a blank line before and after.
   * Start each file with a single `#` title.
   * Keep heading levels consistent (don’t skip levels).

2. **Paragraphs & Line Breaks**

   * One blank line between paragraphs.
   * No trailing double spaces for line breaks.

3. **Lists**

   * Blank line before and after a list.
   * Use `- ` for bullets, `1.` for ordered lists.
   * One item per line; indent wrapped text with two spaces.
   * Add a blank line before nested lists, indent nested items by two spaces.

4. **Code & Diagrams**

   * Blank line before and after fenced blocks.
   * Use triple backticks with a language tag (`csharp`, `json`, `mermaid`).
   * Ensure diagram syntax (e.g., Mermaid) is valid.

5. **Tables**

   * Blank line before and after.
   * Must have a header row and separator row.
   * Escape `|` inside cells with `\|`.

6. **Links**

   * Use relative links for internal docs (`[Utilities](./utility.md)`).
   * Use GitHub `blob` URLs with `#L<line>` for code definitions.

7. **Images**

   * Store in `docs/assets/` or similar.
   * Use relative paths with alt text: `![Flow](../assets/flow.png)`.

8. **File Hygiene**

   * End every file with a single newline.
   * Remove stray leading spaces and trailing whitespace.
   * Avoid mixing tabs and spaces.
