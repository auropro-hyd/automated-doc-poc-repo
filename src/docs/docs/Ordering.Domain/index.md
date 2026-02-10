# Ordering.Domain Overview

The Ordering.Domain project provides the core domain logic for managing orders and buyers in the eShop application. It defines aggregates, entities, value objects, domain events, and repository contracts to ensure transactional consistency and enforce business rules. The domain is designed for extensibility, maintainability, and clear separation of concerns, supporting robust order processing and buyer management workflows.

The project is organized into logical folders that separate aggregates, events, exceptions, and seedwork (base domain types). This structure helps developers quickly locate and understand the responsibilities of each component.

```text
Ordering.Domain/
  AggregatesModel/         # Contains domain aggregates (Order, Buyer) and related value objects
    BuyerAggregate/        # Buyer aggregate and payment method value objects
    OrderAggregate/        # Order aggregate, order items, address, and status value objects
  Events/                  # Domain events raised by aggregates
  Exceptions/              # Domain-specific exception types
  SeedWork/                # Base domain definitions (Entity, ValueObject, IAggregateRoot, IRepository, IUnitOfWork)
  obj/                     # Build artifacts (ignored in domain logic)
  GlobalUsings.cs          # Global using directives
  Ordering.Domain.csproj   # Project file
  README.md                # Project documentation
```

## Documentation Structure

The Ordering.Domain documentation is organized into the following areas:

- [Base Domain Definitions](./BaseDomainDefinition.md): Foundational types such as Entity, ValueObject, and IAggregateRoot.
- [Value Objects](./ValueObject.md): Immutable types used for modeling concepts like addresses, order items, and payment methods.
- [Data Interactions](./DataInteraction.md): Repository and unit-of-work contracts for managing aggregates and entities.
- [Domain Events](./DomainEvent.md): Events raised by aggregates to signal important business facts and state changes.
- [Exception](./Exception.md): Domain-specific exception types for enforcing business rules.
- [Aggregates](./Aggregate.md): Main consistency boundaries, including Order and Buyer aggregates, with diagrams and domain operations.
