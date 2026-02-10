# Base Domain Definitions

This section covers the foundational domain types used throughout the Ordering.Domain project. These are essential for building aggregates, entities, and value objects.

---

## ValueObject

**Overview:**
Represents an immutable type whose equality is determined by its property values rather than identity. Used for modeling concepts that do not require a unique identity, such as addresses or card types.

[View on GitHub](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Domain/SeedWork/ValueObject.cs)

---

## Entity

**Overview:**
Defines a domain object with a unique identity and lifecycle. Entities are the building blocks for aggregates and are tracked for changes within the domain.

[View on GitHub](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Domain/SeedWork/Entity.cs)

---

## IAggregateRoot

**Overview:**
Marks an entity as the root of an aggregate, ensuring transactional consistency and encapsulation of related entities and value objects.

[View on GitHub](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Domain/SeedWork/IAggregateRoot.cs)
