# Data Interactions

Data Interaction types are responsible for abstracting persistence and transactional operations in the domain. They provide repository and unit-of-work patterns for managing aggregates and entities.

---

## IRepository

**Overview:**
Defines a generic contract for repository operations, such as adding, removing, and querying domain entities. Enables decoupling of domain logic from data access implementations.

[View on GitHub](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Domain/SeedWork/IRepository.cs)

---

## IUnitOfWork

**Overview:**
Specifies a contract for managing transactional consistency across multiple repository operations. Ensures atomicity and consistency in domain transactions.

[View on GitHub](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Domain/SeedWork/IUnitOfWork.cs)

---

## IBuyerRepository

**Overview:**
Defines repository operations specific to the Buyer aggregate, such as retrieving buyers and managing payment methods.

[View on GitHub](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Domain/AggregatesModel/BuyerAggregate/IBuyerRepository.cs)

---

## IOrderRepository

**Overview:**
Specifies repository operations for the Order aggregate, including order retrieval, creation, and status updates.

[View on GitHub](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Domain/AggregatesModel/OrderAggregate/IOrderRepository.cs)
