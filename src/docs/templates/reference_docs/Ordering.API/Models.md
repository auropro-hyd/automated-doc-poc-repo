# Models

This file documents the models used in the Ordering.API service.

## Commands

### [CancelOrderCommand](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.API/Application/Commands/CancelOrderCommand.cs)
**Overview:**  
The `CancelOrderCommand` class represents a request to cancel an order by its order number. It is used to trigger the cancellation workflow for a specific order in the system.

### [CreateOrderCommand](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.API/Application/Commands/CreateOrderCommand.cs)
**Overview:**  
The `CreateOrderCommand` class encapsulates all the data required to create a new order, including user details, address, payment information, and a collection of order items. It uses the custom data model [OrderItemDTO](../Ordering.API/Models.md#orderitemdto) for representing individual items in the order.

### [CreateOrderDraftCommand](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.API/Application/Commands/CreateOrderDraftCommand.cs)
**Overview:**  
The `CreateOrderDraftCommand` class is used to create a draft order for a buyer, taking a buyer ID and a collection of [BasketItem](../Ordering.API/Models.md#basketitem) instances. It helps in preparing an order draft before final submission.

### [IdentifiedCommand](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.API/Application/Commands/IdentifiedCommand.cs)
**Overview:**  
The `IdentifiedCommand` class wraps another command with a unique identifier, enabling idempotency and tracking for command processing. It is generic and can be used with any command type in the system.

### [SetAwaitingValidationOrderStatusCommand](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.API/Application/Commands/SetAwaitingValidationOrderStatusCommand.cs)
**Overview:**  
The `SetAwaitingValidationOrderStatusCommand` class is used to update an order's status to 'Awaiting Validation' by specifying the order number. It is part of the order status management workflow.

### [SetPaidOrderStatusCommand](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.API/Application/Commands/SetPaidOrderStatusCommand.cs)
**Overview:**  
The `SetPaidOrderStatusCommand` class is used to mark an order as paid by providing the order number. It triggers the payment confirmation process for the order.

### [SetStockConfirmedOrderStatusCommand](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.API/Application/Commands/SetStockConfirmedOrderStatusCommand.cs)
**Overview:**  
The `SetStockConfirmedOrderStatusCommand` class is used to update an order's status to 'Stock Confirmed' for a given order number. It is part of the stock validation workflow.

### [SetStockRejectedOrderStatusCommand](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.API/Application/Commands/SetStockRejectedOrderStatusCommand.cs)
**Overview:**  
The `SetStockRejectedOrderStatusCommand` class is used to mark an order as 'Stock Rejected' and includes a list of rejected stock item IDs. The list is represented as a collection of integers.

### [ShipOrderCommand](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.API/Application/Commands/ShipOrderCommand.cs)
**Overview:**  
The `ShipOrderCommand` class is used to trigger the shipping process for an order by specifying the order number. It initiates the workflow for shipping the order to the customer.

## Models

### [BasketItem](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.API/Models/BasketItem.cs#L1)

**Overview:**  
The `BasketItem` class represents an individual item within a customer's shopping basket in the Ordering API. It encapsulates product details, quantity, and pricing information required for order creation and validation. This model is essential for transferring basket data between client and server during the checkout process.

---

### [CustomerBasket](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.API/Models/CustomerBasket.cs#L1)

**Overview:**  
The `CustomerBasket` class models the entire shopping basket for a specific user, aggregating multiple [BasketItem](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.API/Models/BasketItem.cs#L1) instances. It manages the basket's lifecycle, including item addition, removal, and total calculation, serving as the primary data structure for basket operations in the Ordering API.

---

## Integration Events

### GracePeriodConfirmedIntegrationEvent
**Overview:**  
The `GracePeriodConfirmedIntegrationEvent` class signals that the grace period for an order has been confirmed, carrying the order ID for which the grace period applies.

### OrderPaymentFailedIntegrationEvent
**Overview:**  
The `OrderPaymentFailedIntegrationEvent` class represents a failed payment event for a specific order, identified by its order ID. It is used to trigger compensation or notification workflows.

### OrderPaymentSucceededIntegrationEvent
**Overview:**  
The `OrderPaymentSucceededIntegrationEvent` class indicates that payment for an order has succeeded, providing the order ID for downstream processing.

### OrderStartedIntegrationEvent
**Overview:**  
The `OrderStartedIntegrationEvent` class is raised when a new order process is started, containing the user ID of the customer who initiated the order.

### OrderStatusChangedToAwaitingValidationIntegrationEvent
**Overview:**  
The `OrderStatusChangedToAwaitingValidationIntegrationEvent` class is used when an order's status changes to 'Awaiting Validation'. It includes the order ID, order status ([OrderStatus](../Ordering.Domain/Aggregate.md#order-aggregate)), buyer information, and a collection of [OrderStockItem](#orderstockitem) models representing stock items for validation.

### OrderStatusChangedToCancelledIntegrationEvent
**Overview:**  
The `OrderStatusChangedToCancelledIntegrationEvent` class is raised when an order is cancelled, containing the order ID, order status ([OrderStatus](../Ordering.Domain/Aggregate.md#order-aggregate)), and buyer information.

### OrderStatusChangedToPaidIntegrationEvent
**Overview:**  
The `OrderStatusChangedToPaidIntegrationEvent` class is used when an order's status changes to 'Paid'. It includes the order ID, order status ([OrderStatus](../Ordering.Domain/Aggregate.md#order-aggregate)), buyer information, and a collection of [OrderStockItem](#orderstockitem) models for stock tracking.

### OrderStatusChangedToShippedIntegrationEvent
**Overview:**  
The `OrderStatusChangedToShippedIntegrationEvent` class is raised when an order is shipped, containing the order ID, order status ([OrderStatus](../Ordering.Domain/Aggregate.md#order-aggregate)), and buyer information.

### OrderStatusChangedToStockConfirmedIntegrationEvent
**Overview:**  
The `OrderStatusChangedToStockConfirmedIntegrationEvent` class is used when an order's status changes to 'Stock Confirmed', including the order ID, order status ([OrderStatus](../Ordering.Domain/Aggregate.md#order-aggregate)), and buyer information.

### OrderStatusChangedToSubmittedIntegrationEvent
**Overview:**  
The `OrderStatusChangedToSubmittedIntegrationEvent` class is raised when an order is submitted, containing the order ID, order status ([OrderStatus](../Ordering.Domain/Aggregate.md#order-aggregate)), and buyer information.

### OrderStockConfirmedIntegrationEvent
**Overview:**  
The `OrderStockConfirmedIntegrationEvent` class signals that the stock for an order has been confirmed, carrying the order ID for which the stock was validated.

### OrderStockRejectedIntegrationEvent
**Overview:**  
The `OrderStockRejectedIntegrationEvent` class is used when an order's stock is rejected. It includes the order ID and a list of [ConfirmedOrderStockItem](#confirmedorderstockitem) models indicating which items were rejected.

---

### OrderStockItem
**Overview:**  
The `OrderStockItem` model represents an item in an order for stock validation, including product ID and quantity. Used in awaiting validation and paid integration events.

### ConfirmedOrderStockItem
**Overview:**  
The `ConfirmedOrderStockItem` model represents the stock confirmation status for a product in an order, including product ID and a boolean indicating stock availability. Used in stock rejection integration events.