# ICatalogIntegrationEventService

[Definition](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Catalog.API/IntegrationEvents/ICatalogIntegrationEventService.cs#L4)

## Purpose & Role

ICatalogIntegrationEventService defines the contract for publishing and saving integration events related to catalog changes. It is intended for use in event-driven workflows, ensuring atomicity between catalog updates and event log persistence.

---

## Members

- `Task SaveEventAndCatalogContextChangesAsync(IntegrationEvent evt)` — Saves the event and catalog context changes atomically. [Definition](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Catalog.API/IntegrationEvents/ICatalogIntegrationEventService.cs#L6)
- `Task PublishThroughEventBusAsync(IntegrationEvent evt)` — Publishes the event through the event bus. [Definition](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Catalog.API/IntegrationEvents/ICatalogIntegrationEventService.cs#L7)

---

## Implementation Discovery

- [CatalogIntegrationEventService](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Catalog.API/IntegrationEvents/CatalogIntegrationEventService.cs#L4) (primary implementation)

---

## Implementation Diagram

```mermaid
flowchart LR
  ICatalogIntegrationEventService -->|implemented by| CatalogIntegrationEventService
  click ICatalogIntegrationEventService "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Catalog.API/IntegrationEvents/ICatalogIntegrationEventService.cs#L4"
  click CatalogIntegrationEventService "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Catalog.API/IntegrationEvents/CatalogIntegrationEventService.cs#L4"
```

ICatalogIntegrationEventService is implemented by CatalogIntegrationEventService, which is registered in DI and used by CatalogServices and API handlers.

---

## Recommended Usage

Use ICatalogIntegrationEventService when you need to publish or persist integration events in catalog workflows. To extend, implement the interface in a new class, override all members, and register your implementation in DI. Reference implementation is CatalogIntegrationEventService. Ensure atomicity and error handling in your implementation.

