## [OrderQueries](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.API/Application/Queries/OrderQueries.cs)

### Overview
The `OrderQueries` class provides query operations for retrieving order-related data from the database in the Ordering API. It is responsible for fetching detailed order information, user-specific order summaries, and available card types. The class collaborates closely with the `OrderingContext` (Entity Framework database context) and implements the `IOrderQueries` interface, ensuring a consistent contract for query operations. The use of a primary constructor streamlines dependency injection and initialization. 

---

### Methods

#### GetOrderAsync
**Overview:**
Public async method. Retrieves a single order by its ID, including all associated order items. Parameters: `int id`. Returns: `Task<Order>`. Throws an exception if the order is not found.

**Call Graph:**
```mermaid
flowchart LR
    A([OrderQueries.GetOrderAsync](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.API/Application/Queries/OrderQueries.cs#L6)) -- "calls" --> B([OrderingContext.Orders.Include](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.entityframeworkqueryableextensions.include))
    B -- "calls" --> C([OrderingContext.Orders.FirstOrDefaultAsync](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.entityframeworkqueryableextensions.firstordefaultasync))
    C -- "calls" --> D([Order.GetTotal](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.API/Model/Order.cs))
    D -- "calls" --> E([LINQ.Select for OrderItems](https://learn.microsoft.com/en-us/dotnet/api/system.linq.enumerable.select))
```

??? Call Graph Legend
    - **GetOrderAsync** - [OrderQueries.GetOrderAsync](#getorderasync)
    - **Order.GetTotal** - [Order.GetTotal](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.API/Model/Order.cs)

**Implementation flow:**
```mermaid
flowchart LR
    S([Start](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.API/Application/Queries/OrderQueries.cs#L6)) --> P1([Query Orders table for order with matching ID](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.API/Application/Queries/OrderQueries.cs#L9))
    P1 --> D1{Order is null?}
    D1 -- Yes --> E1([Throw KeyNotFoundException](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.API/Application/Queries/OrderQueries.cs#L13))
    D1 -- No --> P2([Map order properties to new Order object](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.API/Application/Queries/OrderQueries.cs#L15))
    P2 --> P3([Map order items](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.API/Application/Queries/OrderQueries.cs#L27))
    P3 --> E2([Return mapped Order](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.API/Application/Queries/OrderQueries.cs#L32))
```

**Exceptions:**
- `KeyNotFoundException`: Thrown if no order is found for the given ID.

**Configuration:**
- No configuration values are used directly in this method.

---

#### GetOrdersFromUserAsync
**Overview:**
Public async method. Retrieves all orders for a specific user by their identity GUID. Parameters: `string userId`. Returns: `Task<IEnumerable<OrderSummary>>`.

**Call Graph:**
```mermaid
flowchart LR
    A([OrderQueries.GetOrdersFromUserAsync](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.API/Application/Queries/OrderQueries.cs#L34)) -- "calls" --> B([OrderingContext.Orders.Where](https://learn.microsoft.com/en-us/dotnet/api/system.linq.queryable.where))
    B -- "calls" --> C([LINQ.Select for OrderSummary](https://learn.microsoft.com/en-us/dotnet/api/system.linq.enumerable.select))
    C -- "calls" --> D([LINQ.Sum for calculating totals](https://learn.microsoft.com/en-us/dotnet/api/system.linq.enumerable.sum))
    D -- "calls" --> E([ToListAsync](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.entityframeworkqueryableextensions.tolistasync))
```

??? Call Graph Legend
    - **GetOrdersFromUserAsync** - [OrderQueries.GetOrdersFromUserAsync](#getordersfromuserasync)

**Implementation flow:**
```mermaid
flowchart LR
    S([Start](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.API/Application/Queries/OrderQueries.cs#L34)) --> P1([Query Orders table for orders matching userId](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.API/Application/Queries/OrderQueries.cs#L36))
    P1 --> P2([Map each order to OrderSummary](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.API/Application/Queries/OrderQueries.cs#L39))
    P2 --> E([Return list of OrderSummary](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.API/Application/Queries/OrderQueries.cs#L44))
```

**Exceptions:**
- No explicit exceptions are thrown in this method.

**Configuration:**
- No configuration values are used directly in this method.

---

#### GetCardTypesAsync
**Overview:**
Public async method. Retrieves all available card types from the database. No parameters. Returns: `Task<IEnumerable<CardType>>`.

**Call Graph:**
```mermaid
flowchart LR
    A([OrderQueries.GetCardTypesAsync](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.API/Application/Queries/OrderQueries.cs#L46)) -- "calls" --> B([OrderingContext.CardTypes.Select](https://learn.microsoft.com/en-us/dotnet/api/system.linq.enumerable.select))
    B -- "calls" --> C([ToListAsync](https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.entityframeworkqueryableextensions.tolistasync))
```

??? Call Graph Legend
    - **GetCardTypesAsync** - [OrderQueries.GetCardTypesAsync](#getcardtypesasync)

**Implementation flow:**
```mermaid
flowchart LR
    S([Start](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.API/Application/Queries/OrderQueries.cs#L46)) --> P1([Query CardTypes table](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.API/Application/Queries/OrderQueries.cs#L47))
    P1 --> P2([Map each card type to CardType object](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.API/Application/Queries/OrderQueries.cs#L47))
    P2 --> E([Return list of CardType](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.API/Application/Queries/OrderQueries.cs#L47))
```

**Exceptions:**
- No explicit exceptions are thrown in this method.

**Configuration:**
- No configuration values are used directly in this method.

---

??? Usage Example

```csharp
var queries = new OrderQueries(context);
var order = await queries.GetOrderAsync(orderId);
var userOrders = await queries.GetOrdersFromUserAsync(userId);
var cardTypes = await queries.GetCardTypesAsync();
```

??? Threading Considerations
All methods are asynchronous and should be awaited to avoid blocking threads. Ensure the `OrderingContext` is properly scoped per request to avoid concurrency issues.
