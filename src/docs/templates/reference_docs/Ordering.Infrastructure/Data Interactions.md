# Data Interactions

## [OrderingContext.cs](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Infrastructure/OrderingContext.cs#L1)

**Overview:**
Implements the EF Core [`DbContext`](../Ordering.Domain/BaseDomainDefinition.md#entity) and [`IUnitOfWork`](../Ordering.Domain/DataInteraction.md#iunitofwork) for the ordering domain. Manages entity sets, transactions, and persistence logic for [`Order`](../Ordering.Domain/Aggregate.md#order-aggregate), [`Buyer`](../Ordering.Domain/Aggregate.md#buyer-aggregate), [`PaymentMethod`](../Ordering.Domain/ValueObject.md#paymentmethod), and related entities.

**Methods:**
### [SaveEntitiesAsync(CancellationToken cancellationToken = default)](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Infrastructure/OrderingContext.cs#L47)
- **Overview:** Persists all changes and dispatches domain events. Ensures atomicity and consistency.
- **Exceptions:** Throws if database update fails or domain event dispatching fails.

### [BeginTransactionAsync()](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Infrastructure/OrderingContext.cs#L64)
- **Overview:** Starts a new database transaction.
- **Exceptions:** Throws if transaction cannot be started.

### [CommitTransactionAsync(IDbContextTransaction transaction)](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Infrastructure/OrderingContext.cs#L73)
- **Overview:** Commits the current transaction.
- **Exceptions:** Throws if commit fails or transaction is invalid.

### [RollbackTransaction()](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Infrastructure/OrderingContext.cs#L98)
- **Overview:** Rolls back the current transaction.
- **Exceptions:** Throws if rollback fails or transaction is invalid.

---

## [BuyerRepository.cs](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Infrastructure/Repositories/BuyerRepository.cs#L1)

**Overview:**
Repository for the [`Buyer`](../Ordering.Domain/Aggregate.md#buyer-aggregate) aggregate. Handles persistence, retrieval, and updates for [`Buyer`](../Ordering.Domain/Aggregate.md#buyer-aggregate) entities. 

**Methods:**
### [Add(Buyer buyer)](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Infrastructure/Repositories/BuyerRepository.cs#L14)
- **Overview:** Adds a new buyer to the context.
- **Exceptions:** Throws if buyer is invalid or context is disposed.

### [Update(Buyer buyer)](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Infrastructure/Repositories/BuyerRepository.cs#L26)
- **Overview:** Updates an existing buyer.
- **Exceptions:** Throws if buyer is invalid or context is disposed.

### [FindAsync(string identity)](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Infrastructure/Repositories/BuyerRepository.cs#L33)
- **Overview:** Finds a buyer by identity asynchronously.
- **Exceptions:** Throws if query fails or context is disposed.

### [FindByIdAsync(int id)](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Infrastructure/Repositories/BuyerRepository.cs#L43)
- **Overview:** Finds a buyer by ID asynchronously.
- **Exceptions:** Throws if query fails or context is disposed.

---

## [OrderRepository.cs](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Infrastructure/Repositories/OrderRepository.cs#L1)

**Overview:**
Repository for the [`Order`](../Ordering.Domain/Aggregate.md#order-aggregate) aggregate. Handles persistence, retrieval, and updates for [`Order`](../Ordering.Domain/Aggregate.md#order-aggregate) entities. 

**Methods:**
### [Add(Order order)](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Infrastructure/Repositories/OrderRepository.cs#L15)
- **Overview:** Adds a new order to the context.
- **Exceptions:** Throws if order is invalid or context is disposed.

### [Update(Order order)](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Infrastructure/Repositories/OrderRepository.cs#L34)
- **Overview:** Updates an existing order.
- **Exceptions:** Throws if order is invalid or context is disposed.

### [GetAsync(int orderId)](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Infrastructure/Repositories/OrderRepository.cs#L21)
- **Overview:** Retrieves an order by ID asynchronously.
- **Exceptions:** Throws if query fails or context is disposed.

---


## [RequestManager.cs](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Infrastructure/Idempotency/RequestManager.cs#L1)

**Overview:**
Implements idempotency tracking for requests. Ensures commands are processed only once, preventing duplicate operations. 

**Methods:**

### [ExistAsync(Guid id)](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Infrastructure/Idempotency/RequestManager.cs#L13)
- **Overview:** Checks if a request with the given ID exists.
- **Flow Diagram:**
```mermaid
flowchart LR
	A[Start] --> B[Query ClientRequest]
	B --> C[Return Exists]
	click A "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Infrastructure/Idempotency/RequestManager.cs#L13" "Method Start"
	click B "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Infrastructure/Idempotency/RequestManager.cs#L15" "Query ClientRequest"
	click C "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Infrastructure/Idempotency/RequestManager.cs#L17" "Return Exists"
```
**Exceptions:** Throws if query fails or context is disposed.


### [CreateRequestForCommandAsync<T>(Guid id)](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Infrastructure/Idempotency/RequestManager.cs#L21)
- **Overview:** Creates a new client request record for idempotency.
- **Flow Diagram:**
```mermaid
flowchart LR
	A[Start] --> B[Add ClientRequest]
	B --> C[Save Changes]
	C --> D[End]
	click A "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Infrastructure/Idempotency/RequestManager.cs#L21" "Method Start"
	click B "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Infrastructure/Idempotency/RequestManager.cs#L23" "Add ClientRequest"
	click C "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Infrastructure/Idempotency/RequestManager.cs#L25" "Save Changes"
	click D "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Infrastructure/Idempotency/RequestManager.cs#L27" "Method End"
```
**Exceptions:** Throws if creation fails or context is disposed.

---

## [IRequestManager.cs](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Infrastructure/Idempotency/IRequestManager.cs#L3)

**Overview:**
Interface for idempotency tracking. 

---

## [ClientRequest.cs](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Infrastructure/Idempotency/ClientRequest.cs#L5)

**Overview:**
Represents a client request record for idempotency. 

---

**Threading Considerations:**
- All repository and context methods are async and safe for concurrent use within the scope of a request.
- DbContext is not thread-safe; use per-request scope.

**Lifecycle Rules:**
- Repositories and context are registered as scoped dependencies in DI.
