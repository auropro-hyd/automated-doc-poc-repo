# Domain Events

Domain Events represent significant occurrences within the domain, raised by aggregates to signal state changes or important business facts. They are immutable and used for decoupling business logic and side effects.

---

## BuyerPaymentMethodVerifiedDomainEvent

**Overview:**
Raised when a buyer's payment method is successfully verified. Used to trigger downstream processes such as order validation or payment authorization.

[View on GitHub](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Domain/Events/BuyerPaymentMethodVerifiedDomainEvent.cs)

---

## OrderCancelledDomainEvent

**Overview:**
Signals that an order has been cancelled. Used to notify other subsystems and trigger compensating actions.

[View on GitHub](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Domain/Events/OrderCancelledDomainEvent.cs)

---

## OrderShippedDomainEvent

**Overview:**
Indicates that an order has been shipped. Used to update order status and notify customers or external systems.

[View on GitHub](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Domain/Events/OrderShippedDomainEvent.cs)

---

## OrderStartedDomainEvent

**Overview:**
Raised when an order process is initiated. Used to trigger validation, payment, and inventory checks.

[View on GitHub](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Domain/Events/OrderStartedDomainEvent.cs)

---

## OrderStatusChangedToAwaitingValidationDomainEvent

**Overview:**
Signals that an order's status has changed to "Awaiting Validation." Used to coordinate validation workflows and notify relevant parties.

[View on GitHub](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Domain/Events/OrderStatusChangedToAwaitingValidationDomainEvent.cs)

---

## OrderStatusChangedToPaidDomainEvent

**Overview:**
Indicates that an order has been paid. Used to trigger shipment and update order status.

[View on GitHub](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Domain/Events/OrderStatusChangedToPaidDomainEvent.cs)

---

## OrderStatusChangedToStockConfirmedDomainEvent

**Overview:**
Signals that an order's stock has been confirmed. Used to proceed with order fulfillment and notify inventory systems.

[View on GitHub](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Domain/Events/OrderStatusChangedToStockConfirmedDomainEvent.cs)
