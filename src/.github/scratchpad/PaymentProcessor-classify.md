# PaymentProcessor Class Classification

Below is the classification and dependency graph for the main classes in the PaymentProcessor project. Test, auto-generated, and obj files are excluded.

## Topological Order of Classes

1. PaymentOptions.cs - Configuration - No dependencies - 6 lines
2. OrderStatusChangedToStockConfirmedIntegrationEvent.cs - Messaging - Depends on IntegrationEvent - 3 lines
3. OrderPaymentSucceededIntegrationEvent.cs - Messaging - Depends on IntegrationEvent - 3 lines
4. OrderPaymentFailedIntegrationEvent.cs - Messaging - Depends on IntegrationEvent - 3 lines
5. OrderStatusChangedToStockConfirmedIntegrationEventHandler.cs - Messaging - Depends on PaymentOptions, OrderStatusChangedToStockConfirmedIntegrationEvent, OrderPaymentSucceededIntegrationEvent, OrderPaymentFailedIntegrationEvent - 38 lines
6. Program.cs - Configuration - Depends on PaymentOptions, OrderStatusChangedToStockConfirmedIntegrationEventHandler, OrderStatusChangedToStockConfirmedIntegrationEvent - 14 lines

## Dependency Graph

```mermaid
flowchart TD
    PaymentOptions["PaymentOptions\n(Configuration)"]
    OrderStatusChangedToStockConfirmedIntegrationEvent["OrderStatusChangedToStockConfirmedIntegrationEvent\n(Messaging)"]
    OrderPaymentSucceededIntegrationEvent["OrderPaymentSucceededIntegrationEvent\n(Messaging)"]
    OrderPaymentFailedIntegrationEvent["OrderPaymentFailedIntegrationEvent\n(Messaging)"]
    OrderStatusChangedToStockConfirmedIntegrationEventHandler["OrderStatusChangedToStockConfirmedIntegrationEventHandler\n(Messaging)"]
    Program["Program\n(Configuration)"]

    Program -->|uses| PaymentOptions
    Program -->|subscribes| OrderStatusChangedToStockConfirmedIntegrationEventHandler
    Program -->|subscribes| OrderStatusChangedToStockConfirmedIntegrationEvent
    OrderStatusChangedToStockConfirmedIntegrationEventHandler -->|depends| PaymentOptions
    OrderStatusChangedToStockConfirmedIntegrationEventHandler -->|publishes| OrderPaymentSucceededIntegrationEvent
    OrderStatusChangedToStockConfirmedIntegrationEventHandler -->|publishes| OrderPaymentFailedIntegrationEvent
    OrderStatusChangedToStockConfirmedIntegrationEventHandler -->|handles| OrderStatusChangedToStockConfirmedIntegrationEvent
    OrderPaymentSucceededIntegrationEvent -->|inherits| IntegrationEvent
    OrderPaymentFailedIntegrationEvent -->|inherits| IntegrationEvent
    OrderStatusChangedToStockConfirmedIntegrationEvent -->|inherits| IntegrationEvent

    click PaymentOptions "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/PaymentProcessor/PaymentOptions.cs#L1-L6"
    click OrderStatusChangedToStockConfirmedIntegrationEvent "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/PaymentProcessor/IntegrationEvents/Events/OrderStatusChangedToStockConfirmedIntegrationEvent.cs#L1-L3"
    click OrderPaymentSucceededIntegrationEvent "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/PaymentProcessor/IntegrationEvents/Events/OrderPaymentSucceededIntegrationEvent.cs#L1-L3"
    click OrderPaymentFailedIntegrationEvent "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/PaymentProcessor/IntegrationEvents/Events/OrderPaymentFailedIntegrationEvent.cs#L1-L3"
    click OrderStatusChangedToStockConfirmedIntegrationEventHandler "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/PaymentProcessor/IntegrationEvents/EventHandling/OrderStatusChangedToStockConfirmedIntegrationEventHandler.cs#L1-L38"
    click Program "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/PaymentProcessor/Program.cs#L1-L14"
```
