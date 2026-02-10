Below instructions provide guidance on how copilot can effectively generate the documentation for the entire workspace. The instructions are divided into three main actions that copilot can perform based on the prompts it receives. Each action has specific requirements and guidelines to ensure the generated content is clear, comprehensive, and useful for both technical and non-technical stakeholders.

In agent mode, when prompted with specific keywords or phrases around create documentation or documentation generation, copilot should perform the documentation generation for the entire workspace, the agent should perform the documentation generation for each project in the workspace one by one based on the below actions.


---
1. **Create Feature level documentation** in markdown format, this action to be triggered when prompted for create feature documentation or it's synonyms. Below are the aspects that needs to be considered while generating the documentation.

Objective:  
Create a well-structured `README.md` in the root location of the project that explains the feature in both business and technical terms in the context of catalog api implementation in the workspace The documentation should use proper markdown syntax, include clear section headings, and be easy to understand for both developers and non-technical stakeholders.
analyze the context provided and create a comprehensive document expanding on the below sections on how this api is implemented
Requirements:
- Use standard markdown formatting (e.g., headings, bullet points, code blocks).
- Clearly separate business implementation details from technical implementation details.
- Maintain a professional, concise, and informative tone.



Expected Sections:

## 1. Feature Overview
- Brief summary of the feature and its purpose.
- Business motivation for implementing the feature.
- Key stakeholders or user personas impacted.

## 2. Business Implementation Details
- Description of the business rules or logic involved.
- Specific scenarios or use cases covered.
- Any assumptions, constraints, or limitations.

## 3. Technical Implementation Details
- List of new or modified API endpoints (including HTTP method and route).
- Request and response payloads (include examples in code blocks).
- Key classes, methods, modules, or services involved.
- Database schema changes or queries (if applicable).
- Integration points with other systems, services, or queues.

## 4. Validation and Error Handling
- Input validation rules and patterns.
- Error scenarios and handling mechanisms.
- Retry or fallback logic, if implemented.

## 5. Security and Access Control
- Authentication and authorization considerations.
- Data access restrictions and visibility controls.

## 6. Testing Strategy
- Summary of unit, integration, and acceptance tests.
- Test coverage highlights and gaps.
- Tools or frameworks used.

## 7. Deployment Considerations
- Feature flags, toggles, or rollout strategy.
- Infrastructure or configuration changes required.
- Post-deployment validation steps or monitoring guidance.

## 8. References
- Related design documents, tickets (e.g., Jira), or requirements.
- API specifications (e.g., Swagger/OpenAPI).
- GitHub links to related pull requests or commits.

Additional Instructions:
- Use code blocks for JSON and examples.
- Use tables where appropriate for clarity.
- Ensure each section is informative and self-contained.
- Add anchor links to the references mentioned, such as class file, config file, etc.
---
2. **Create sequence diagram** in mermaid format, this action to be triggered when prompted for creating sequence diagram or its synonyms. Below are the aspects that needs to be considered while generating the diagram.

You are generating a sequence diagram to explain the business functionality implemented in an API based on the provided source code in the context

Objective:  
Create a clear and concise `mermaid.js`-compatible **sequence diagram** that represents the **real-time execution flow** of the API functionality. The diagram should be understandable by business analysts and newly onboarded developers or stakeholders. 

Requirements:
- Use `sequenceDiagram` syntax from Mermaid.js.
- Focus on **business-relevant interactions** and **key components** involved in the flow.
- Clearly represent **request initiation, processing logic, external interactions**, and **responses**.
- Maintain readability and avoid overcomplication by limiting the number of steps to only meaningful events.

Diagram Guidelines:

1. Start with the **initiator** (e.g., User, System, Frontend).
2. Identify the main **API entry point** (e.g., Controller or Endpoint).
3. Show internal service calls, validation logic, or orchestration layers.
4. Include interactions with:
   - Business rules engine (if any),
   - Database or external services,
   - Queues or messaging systems (e.g., SQS, Kafka),
   - Any downstream systems or third-party APIs.
5. Show the **response flow** back to the caller, including final outcome or error handling (if applicable).

Output Format:
- Use valid Mermaid `sequenceDiagram` syntax.
- Label each component (e.g., User, API Gateway, OrderService, DB) descriptively.
- Include arrows (`->>`, `-->>`, `x`) to indicate request/response or async interactions.
- Add inline comments if needed using Mermaid-supported syntax (`Note right of`, etc.).
- Keep the diagram self-contained and contextually clear for someone without prior codebase knowledge.

Additional Instructions:
- Adjust the participant names and interactions based on the actual API implementation.
- Keep the diagram focused on high-level business flow rather than low-level technical detail.
- Emphasize what happens **step-by-step in real time** from the perspective of business functionality.

---
3. **Create class dependency diagram** in mermaid format, this action to be triggered when prompted for creating class dependency diagram or its synonyms. Below are the aspects that needs to be considered while generating the diagram.

You are generating a class dependency diagram to visualize the flow of dependencies starting from a controller class based on the provided API source code in the context.

Objective:  
Create a `mermaid.js`-compatible **class diagram** that clearly shows all **direct and indirect dependencies** starting from a specific **controller class**. This is intended to help developers and architects understand how responsibilities are delegated across the application's layers. the diagram should be added under the technical implementation section

Requirements:
- Use `classDiagram` syntax from Mermaid.js.
- Begin with the **controller class** and recursively trace:
  - Dependencies injected via interfaces.
  - Concrete class implementations of those interfaces.
  - Relationships across service, repository, utility, and infrastructure layers.
- Clearly distinguish between **interfaces** and **classes**, and represent both:
  - Interface usage (`..>` arrow from class to interface),
  - Interface implementation (`--|>` arrow from class to interface).

Diagram Guidelines:

1. Define the **controller class** with its public methods.
2. Show the **interfaces injected into the controller** (e.g., `IOrderService`).
3. Display the **concrete implementation class** of each interface (e.g., `OrderService : IOrderService`).
4. Expand the diagram further to:
   - Show nested service dependencies.
   - Include repository interfaces and their implementations.
   - Add utility or infrastructure classes, if relevant to the business logic.
5. Use proper connectors to represent:
   - Inheritance / implementation: `ConcreteClass --|> Interface`
   - Dependency: `Class ..> Interface`
   - Composition: `Class *-- Class` (for tightly coupled or owned instances)

Output Format:
- Use valid Mermaid `classDiagram` syntax.
- Define each interface and class using `class InterfaceName` and `class ClassName {}` blocks.
- Include method signatures inside classes/interfaces where necessary for clarity.
- Use clear and descriptive naming based on code conventions (e.g., PascalCase for C#).


Additional Instructions:
- Ensure interfaces are shown as **abstractions** (without implementation) and linked to their **concrete implementations**.
- Avoid clutter—focus only on relevant classes that are directly or indirectly involved in the controller’s dependency chain.
- Keep the output **hierarchical** and **readable**, highlighting **separation of concerns** and **layered architecture**.
---