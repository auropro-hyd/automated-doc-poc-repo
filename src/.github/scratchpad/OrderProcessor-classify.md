# OrderProcessor Class Classification

Below is the classification and dependency graph for the main classes in the OrderProcessor project.

## Class List (Topological Order)

1. **BackgroundTaskOptions.cs** (Configuration) - No dependencies, 9 lines
2. **GracePeriodConfirmedIntegrationEvent.cs** (Messaging) - Depends on IntegrationEvent (external), 11 lines
3. **IntegrationEventContext.cs** (Serialization) - Depends on GracePeriodConfirmedIntegrationEvent, 8 lines
4. **Extensions.cs** (Configuration/Adapters) - Depends on BackgroundTaskOptions, GracePeriodManagerService, IntegrationEventContext, 22 lines
5. **GracePeriodManagerService.cs** (Services) - Depends on BackgroundTaskOptions, GracePeriodConfirmedIntegrationEvent, IEventBus, ILogger, NpgsqlDataSource, 66 lines

## Mermaid Dependency Graph

```mermaid
flowchart TD
    BackgroundTaskOptions[BackgroundTaskOptions\nConfiguration] -->|used by| GracePeriodManagerService[GracePeriodManagerService\nServices]
    BackgroundTaskOptions -->|used by| Extensions[Extensions\nConfiguration/Adapters]
    GracePeriodConfirmedIntegrationEvent[GracePeriodConfirmedIntegrationEvent\nMessaging] -->|used by| GracePeriodManagerService
    GracePeriodConfirmedIntegrationEvent -->|used by| IntegrationEventContext[IntegrationEventContext\nSerialization]
    IntegrationEventContext -->|used by| Extensions
    GracePeriodManagerService -->|registered by| Extensions
    Extensions -->|called by| Program[Program\nEntry]
    click BackgroundTaskOptions "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/OrderProcessor/BackgroundTaskOptions.cs#L1-L9"
    click GracePeriodConfirmedIntegrationEvent "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/OrderProcessor/Events/GracePeriodConfirmedIntegrationEvent.cs#L1-L11"
    click IntegrationEventContext "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/OrderProcessor/Extensions/Extensions.cs#L17-L24"
    click Extensions "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/OrderProcessor/Extensions/Extensions.cs#L1-L22"
    click GracePeriodManagerService "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/OrderProcessor/Services/GracePeriodManagerService.cs#L1-L66"
    click Program "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/OrderProcessor/Program.cs#L1-L8"
```

---

This file documents the classification and dependencies of classes in the OrderProcessor project for developer documentation.
