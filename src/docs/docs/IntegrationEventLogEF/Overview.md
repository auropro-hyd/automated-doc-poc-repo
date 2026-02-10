# IntegrationEventLogEF Library Overview

The IntegrationEventLogEF library provides robust infrastructure for managing integration event logs in distributed .NET applications. It enables reliable event persistence, transactional integrity, and orchestration of event publishing workflows using Entity Framework Core. The library is designed to support event-driven architectures, ensuring that events are tracked, retried, and published with resilience and traceability.



## File Dependency Diagram

```mermaid
flowchart TD
    EventStateEnum[EventStateEnum]
    IntegrationEventLogEntry[IntegrationEventLogEntry]
    IntegrationLogExtensions[IntegrationLogExtensions]
    ResilientTransaction[ResilientTransaction]
    IIntegrationEventLogService[IIntegrationEventLogService]
    IntegrationEventLogService[IntegrationEventLogService]

    EventStateEnum -->|used by| IntegrationEventLogEntry
    IntegrationEventLogEntry -->|used by| IntegrationLogExtensions
    IntegrationEventLogEntry -->|used by| IntegrationEventLogService
    IntegrationLogExtensions -->|used by| IntegrationEventLogService
    IIntegrationEventLogService -->|implemented by| IntegrationEventLogService
    ResilientTransaction -->|used by| IntegrationEventLogService
    click EventStateEnum "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/IntegrationEventLogEF/EventStateEnum.cs#L1-L9" "View source" _blank
    click IntegrationEventLogEntry "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/IntegrationEventLogEF/IntegrationEventLogEntry.cs#L1-L49" "View source" _blank
    click IntegrationLogExtensions "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/IntegrationEventLogEF/IntegrationLogExtensions.cs#L1-L16" "View source" _blank
    click ResilientTransaction "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/IntegrationEventLogEF/Utilities/ResilientTransaction.cs#L1-L28" "View source" _blank
    click IIntegrationEventLogService "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/IntegrationEventLogEF/Services/IIntegrationEventLogService.cs#L1-L13" "View source" _blank
    click IntegrationEventLogService "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/IntegrationEventLogEF/Services/IntegrationEventLogService.cs#L1-L92" "View source" _blank
```

## Documentation Walkthrough

- [Data Interactions](./Data%20Interactions.md):
  - Explains event state management, event log entity structure, EF Core configuration, and resilient transaction handling.
- [Services](./Services.md):
  - Details the orchestration of event log operations, including interface and implementation for event publishing, state transitions, and transactional workflows.

Refer to each section for deep dives into the respective components and their usage in distributed event-driven systems.
