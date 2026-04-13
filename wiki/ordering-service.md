# Ordering Service

The Ordering bounded context is the most architecturally complex part of the system, implementing Domain-Driven Design, CQRS, and the transactional outbox pattern. It spans three projects: `Ordering.API`, `Ordering.Domain`, and `Ordering.Infrastructure`.

## Project Structure

```
src/Ordering.API/              # HTTP API, commands, queries, DI, integration events
src/Ordering.Domain/           # Domain model (aggregates, entities, value objects, events)
src/Ordering.Infrastructure/   # EF Core persistence, repositories, mediator extension
```

## Domain Model (Ordering.Domain)

### Order Aggregate

The `Order` entity is the aggregate root. It encapsulates the complete order lifecycle.

**State**: `OrderDate`, `Address` (owned value object), `BuyerId`, `PaymentId`, `OrderStatus`, `Description`, and a private `_orderItems` collection.

**Construction**: Creating an `Order` sets status to `Submitted`, stamps `OrderDate`, assigns the shipping address, and raises `OrderStartedDomainEvent`.

**Key behaviors**:

| Method | Purpose | Domain Event Raised |
|--------|---------|-------------------|
| `AddOrderItem` | Add/merge line items (by ProductId, validates discount < unit price) | -- |
| `SetAwaitingValidationStatus` | Submitted -> AwaitingValidation | `OrderStatusChangedToAwaitingValidationDomainEvent` |
| `SetStockConfirmedStatus` | AwaitingValidation -> StockConfirmed | `OrderStatusChangedToStockConfirmedDomainEvent` |
| `SetPaidStatus` | StockConfirmed -> Paid | `OrderStatusChangedToPaidDomainEvent` |
| `SetShippedStatus` | Paid -> Shipped | `OrderShippedDomainEvent` |
| `SetCancelledStatus` | Submitted -> Cancelled | `OrderCancelledDomainEvent` |
| `SetCancelledStatusWhenStockIsRejected` | AwaitingValidation -> Cancelled | `OrderCancelledDomainEvent` |
| `SetPaymentMethodVerified` | Sets buyer and payment references | -- |
| `NewDraft` (static) | Creates a draft order for preview (not persisted) | -- |

**OrderItem** is an entity within the Order aggregate. It validates that `units > 0` and `discount < totalPrice`.

**Address** is a value object (street, city, state, country, zip) using structural equality.

**OrderStatus**: `Submitted` -> `AwaitingValidation` -> `StockConfirmed` -> `Paid` -> `Shipped`, plus `Cancelled`.

### Buyer Aggregate

The `Buyer` entity is a separate aggregate root, linked to `Order` via `BuyerId`.

**State**: `IdentityGuid` (external user ID), `Name`, private `_paymentMethods` collection.

**Key behavior**: `VerifyOrAddPaymentMethod` finds a matching payment method or creates one, then raises `BuyerAndPaymentMethodVerifiedDomainEvent`.

**PaymentMethod** is an entity within the Buyer aggregate (card alias, card number, security number, holder name, expiration, card type).

### Seedwork

| Class/Interface | Purpose |
|----------------|---------|
| `Entity` | Base: identity, equality, `DomainEvents` list with `AddDomainEvent`/`ClearDomainEvents` |
| `IAggregateRoot` | Marker interface for aggregate roots |
| `ValueObject` | Structural equality via `GetEqualityComponents()` |
| `IRepository<T>` | Repository contract (requires `IUnitOfWork`) |
| `IUnitOfWork` | `SaveEntitiesAsync()` contract |
| `Enumeration` | Base for type-safe enumerations |

## API Endpoints (Ordering.API)

All endpoints are under `api/orders` with API version `1.0` and require authorization.

| Method | Route | Handler | Purpose |
|--------|-------|---------|---------|
| `POST /` | `/api/orders` | `IdentifiedCommand<CreateOrderCommand>` | Create a new order |
| `POST /draft` | `/api/orders/draft` | `CreateOrderDraftCommand` | Preview order totals |
| `PUT /cancel` | `/api/orders/cancel` | `IdentifiedCommand<CancelOrderCommand>` | Cancel an order |
| `PUT /ship` | `/api/orders/ship` | `IdentifiedCommand<ShipOrderCommand>` | Ship an order |
| `GET /{orderId}` | `/api/orders/{orderId:int}` | `IOrderQueries.GetOrderAsync` | Get order by ID |
| `GET /` | `/api/orders` | `IOrderQueries.GetOrdersFromUserAsync` | Get current user's orders |
| `GET /cardtypes` | `/api/orders/cardtypes` | `IOrderQueries.GetCardTypesAsync` | List card types |

**Endpoint infrastructure**: `OrderServices` is a parameter object injected into minimal API handlers containing `IMediator`, `IOrderQueries`, `IIdentityService`, and `ILogger`.

## Commands and Handlers

### Command Pipeline

Every state-changing request flows through the MediatR pipeline:

**LoggingBehavior -> ValidatorBehavior -> TransactionBehavior -> Handler**

### Command Inventory

| Command | Handler | Returns | Idempotent? |
|---------|---------|---------|-------------|
| `CreateOrderCommand` | `CreateOrderCommandHandler` | `bool` | Via `IdentifiedCommand` |
| `CancelOrderCommand` | `CancelOrderCommandHandler` | `bool` | Via `IdentifiedCommand` |
| `ShipOrderCommand` | `ShipOrderCommandHandler` | `bool` | Via `IdentifiedCommand` |
| `CreateOrderDraftCommand` | `CreateOrderDraftCommandHandler` | `OrderDraftDTO` | No (read-only) |
| `SetAwaitingValidationOrderStatusCommand` | Handler | `bool` | No |
| `SetStockConfirmedOrderStatusCommand` | Handler | `bool` | No |
| `SetStockRejectedOrderStatusCommand` | Handler | `bool` | No |
| `SetPaidOrderStatusCommand` | Handler | `bool` | No |

### Idempotency

HTTP-facing commands use `IdentifiedCommand<T, R>` with an `x-requestid` header. The `IdentifiedCommandHandler`:
1. Checks `IRequestManager` for duplicate request ID
2. Records the ID in the `requests` table
3. Delegates to the inner command handler
4. Returns a default result for duplicates

### Validators

| Validator | Validates |
|-----------|----------|
| `CreateOrderCommandValidator` | Order items not empty, city/street/state/country/zip not empty |
| `CancelOrderCommandValidator` | `OrderNumber > 0` |
| `ShipOrderCommandValidator` | `OrderNumber > 0` |
| `IdentifiedCommandValidator` | Always passes (structural validator for the wrapper) |

## Queries

`IOrderQueries` / `OrderQueries` project from EF entities to DTOs:

| Method | Returns |
|--------|---------|
| `GetOrderAsync(orderId)` | `Order` (detail DTO with items, status, address, totals) |
| `GetOrdersFromUserAsync(userId)` | `IEnumerable<OrderSummary>` |
| `GetCardTypesAsync()` | `IEnumerable<CardType>` |

## Domain Event Handlers

These run within the same transaction as the originating command (before `SaveChangesAsync`):

| Handler | Domain Event | Action |
|---------|-------------|--------|
| `ValidateOrAddBuyerAggregateWhenOrderStartedDomainEventHandler` | `OrderStartedDomainEvent` | Find/create buyer, verify payment method, enqueue `OrderStatusChangedToSubmittedIntegrationEvent` |
| `UpdateOrderWhenBuyerAndPaymentMethodVerifiedDomainEventHandler` | `BuyerAndPaymentMethodVerifiedDomainEvent` | Set payment method on order |
| `OrderStatusChangedToAwaitingValidationDomainEventHandler` | Status changed | Enqueue integration event |
| `OrderStatusChangedToStockConfirmedDomainEventHandler` | Status changed | Enqueue integration event |
| `OrderStatusChangedToPaidDomainEventHandler` | Status changed | Enqueue integration event |
| `OrderShippedDomainEventHandler` | Order shipped | Enqueue integration event |
| `OrderCancelledDomainEventHandler` | Order cancelled | Enqueue integration event |

## Integration Event Handlers

These consume events from RabbitMQ and dispatch MediatR commands:

| Handler | Consumes | Dispatches |
|---------|----------|-----------|
| `GracePeriodConfirmedIntegrationEventHandler` | `GracePeriodConfirmedIntegrationEvent` | `SetAwaitingValidationOrderStatusCommand` |
| `OrderStockConfirmedIntegrationEventHandler` | `OrderStockConfirmedIntegrationEvent` | `SetStockConfirmedOrderStatusCommand` |
| `OrderStockRejectedIntegrationEventHandler` | `OrderStockRejectedIntegrationEvent` | `SetStockRejectedOrderStatusCommand` |
| `OrderPaymentSucceededIntegrationEventHandler` | `OrderPaymentSucceededIntegrationEvent` | `SetPaidOrderStatusCommand` |
| `OrderPaymentFailedIntegrationEventHandler` | `OrderPaymentFailedIntegrationEvent` | `CancelOrderCommand` |

## Infrastructure (Ordering.Infrastructure)

### OrderingContext

- Schema: `ordering`
- Implements `IUnitOfWork` with `SaveEntitiesAsync` (dispatches domain events via `MediatorExtension`, then saves)
- Exposes explicit transaction management (`BeginTransactionAsync`, `CommitTransactionAsync`, `RollbackTransaction`) used by `TransactionBehavior`
- Calls `UseIntegrationEventLogs()` to include outbox tables

### Entity Configurations (HiLo Sequences)

| Entity | Sequence | Key Configuration |
|--------|----------|-------------------|
| `Order` | `orderseq` | HiLo, `OrderStatus` as string, `Address` as owned type |
| `OrderItem` | `orderitemseq` | Shadow `OrderId` FK |
| `Buyer` | `buyerseq` | Unique `IdentityGuid` index |
| `PaymentMethod` | `paymentseq` | Private field mappings, FK to `CardType` |
| `CardType` | -- | `ValueGeneratedNever` (seeded reference data) |
| `ClientRequest` | -- | `requests` table for idempotency |

### Repositories

| Repository | Methods |
|-----------|---------|
| `OrderRepository` | `Add`, `GetAsync` (includes `OrderItems`), `Update` |
| `BuyerRepository` | `Add`, `Update`, `FindAsync` (by identity GUID, includes PaymentMethods), `FindByIdAsync` |

### DI Registration (Extensions.cs)

Key registrations in `AddApplicationServices`:
- `OrderingContext` with PostgreSQL + Npgsql
- MediatR with assembly scanning + 3 pipeline behaviors
- FluentValidation validators (singleton)
- `IOrderQueries`, `IBuyerRepository`, `IOrderRepository`, `IRequestManager`
- `IOrderingIntegrationEventService` + `IIntegrationEventLogService`
- RabbitMQ event bus with 5 subscriptions
- `IIdentityService` (resolves user from `HttpContext`)
