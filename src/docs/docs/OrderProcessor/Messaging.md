# Messaging

## [GracePeriodConfirmedIntegrationEvent](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/OrderProcessor/Events/GracePeriodConfirmedIntegrationEvent.cs#L1-L11)

### Overview
GracePeriodConfirmedIntegrationEvent is a messaging class representing an event that signals the confirmation of an order's grace period. It inherits from IntegrationEvent and contains the order ID as its primary data. This event is published by GracePeriodManagerService when an order meets the grace period criteria and is used to trigger downstream processing in other services.

### Properties
- **OrderId** (int): The identifier of the order whose grace period has been confirmed.


??? This event is part of the integration event system and is serialized for transport between microservices.

---
