# Ordering API Documentation

## Sequence Diagram
```mermaid
sequenceDiagram
    participant Client
    participant OrdersApi
    participant OrderService
    participant BuyerRepo
    participant OrderRepo
    participant EventBus
    participant PaymentProcessor

    Client->>+OrdersApi: POST /api/orders
    Note right of OrdersApi: CreateOrderAsync

    OrdersApi->>OrderService: Send CreateOrderCommand
    activate OrderService
    OrderService->>BuyerRepo: Find or Create Buyer
    BuyerRepo-->>OrderService: Buyer Details

    OrderService->>OrderRepo: Create New Order
    OrderRepo-->>OrderService: Order Created

    OrderService->>PaymentProcessor: Process Payment
    activate PaymentProcessor
    PaymentProcessor-->>OrderService: Payment Processed
    deactivate PaymentProcessor

    OrderService->>OrderRepo: Update Order Status
    OrderRepo-->>OrderService: Status Updated

    OrderService->>EventBus: Publish OrderCreatedEvent
    deactivate OrderService

    OrdersApi-->>-Client: Order Created Response

    rect rgb(200, 150, 255)
    Note over Client,EventBus: Order Status Updates
    
    Client->>OrdersApi: GET /api/orders/{orderId}
    activate OrdersApi
    OrdersApi->>OrderService: GetOrderAsync
    OrderService->>OrderRepo: GetAsync
    OrderRepo-->>OrderService: Order Details
    OrderService-->>OrdersApi: Order Data
    OrdersApi-->>Client: Order Status
    deactivate OrdersApi
    end

    rect rgb(191, 223, 255)
    Note over Client,EventBus: Order Cancellation Flow
    
    Client->>+OrdersApi: PUT /api/orders/cancel
    OrdersApi->>OrderService: Send CancelOrderCommand
    OrderService->>OrderRepo: Update Order Status
    OrderRepo-->>OrderService: Status Updated
    OrderService->>EventBus: Publish OrderCancelledEvent
    OrdersApi-->>-Client: Order Cancelled Response
    end
```

## Class Diagram
```mermaid
classDiagram
    class OrdersApi {
        +MapOrdersApiV1() RouteGroupBuilder
        +CreateOrderAsync(requestId, request) Results
        +CancelOrderAsync(requestId, command) Results
        +GetOrderAsync(orderId) Results
        +GetOrdersByUserAsync() Results
    }

    class OrderServices {
        +IMediator Mediator
        +ILogger Logger
        +IOrderQueries Queries
        +IIdentityService IdentityService
    }

    class IOrderRepository {
        <<interface>>
        +IUnitOfWork UnitOfWork
        +Add(order) Order
        +Update(order) void
        +GetAsync(orderId) Task~Order~
    }

    class Order {
        +int Id
        +DateTime OrderDate
        +Address Address
        +int? BuyerId
        +OrderStatus OrderStatus
        +string Description
        +bool IsDraft
        +AddOrderItem()
        +SetPaymentMethodVerified()
        +SetAwaitingValidationStatus()
        +SetStockConfirmedStatus()
        +SetPaidStatus()
        +SetShippedStatus()
        +SetCancelledStatus()
    }

    class OrderRepository {
        -OrderingContext _context
        +IUnitOfWork UnitOfWork
        +Add(order) Order
        +Update(order) void
        +GetAsync(orderId) Task~Order~
    }

    class IBuyerRepository {
        <<interface>>
        +Add(buyer) Buyer
        +Update(buyer) Buyer
        +FindAsync(identity) Task~Buyer~
        +FindByIdAsync(id) Task~Buyer~
    }

    class CreateOrderCommand {
        +List~BasketItem~ Items
        +string UserId
        +string UserName
        +string City
        +string Street
        +string State
        +string Country
        +string ZipCode
        +string CardNumber
        +string CardHolderName
        +DateTime CardExpiration
        +string CardSecurityNumber
        +int CardTypeId
    }

    OrdersApi --> OrderServices : uses
    OrderServices --> IOrderRepository : depends
    OrderRepository ..|> IOrderRepository : implements
    OrderRepository --> Order : manages
    OrderServices --> IBuyerRepository : depends
    OrdersApi --> CreateOrderCommand : creates
    Order --> OrderStatus : has
    OrderServices --> CreateOrderCommand : handles

    click OrdersApi href "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.API/Apis/OrdersApi.cs" "View OrdersApi.cs on GitHub"
    click OrderServices href "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.API/Apis/OrderServices.cs" "View OrderServices.cs on GitHub"
    click OrderRepository href "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Infrastructure/Repositories/OrderRepository.cs" "View OrderRepository.cs on GitHub"
    click IOrderRepository href "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Domain/AggregatesModel/OrderAggregate/IOrderRepository.cs" "View IOrderRepository.cs on GitHub"
    click Order href "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Domain/AggregatesModel/OrderAggregate/Order.cs" "View Order.cs on GitHub"
    click CreateOrderCommand href "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.API/Application/Commands/CreateOrderCommand.cs" "View CreateOrderCommand.cs on GitHub"
```

## 1. Feature Overview
The Ordering API is a critical microservice in the eShop system that manages the complete order lifecycle, from creation to fulfillment. It implements a Domain-Driven Design (DDD) approach with CQRS (Command Query Responsibility Segregation) pattern to handle complex order processing workflows.

### Business Motivation
- Enable customers to place, track, and manage their orders
- Provide a robust order management system for the eShop platform
- Ensure order consistency and reliability through proper domain modeling
- Support various payment methods and order statuses

### Key Stakeholders
- End customers placing orders
- System administrators managing orders
- Payment processing system
- Shipping and logistics teams

## 2. Business Implementation Details

### Business Rules
1. Order Creation:
   - Orders must have valid user information
   - Orders require valid payment details
   - Each order must contain at least one order item
   - Items must have valid product information and quantities

2. Order Status Flow:
   - Submitted → Awaiting Validation
   - Awaiting Validation → Stock Confirmed
   - Stock Confirmed → Paid
   - Paid → Shipped
   - Any State → Cancelled (if applicable conditions are met)

3. Payment Processing:
   - Payment method must be verified before order confirmation
   - Supports multiple card types
   - Requires valid card holder information and expiration date

4. Order Cancellation:
   - Orders can be cancelled by users
   - Automatic cancellation if stock validation fails
   - Cancellation may trigger refund workflow

### Assumptions and Constraints
- Users must be authenticated to place orders
- Payment processing is done through a secure payment gateway
- Order modifications are not allowed once confirmed
- Order history is preserved indefinitely
- Shipping addresses must be validated

## 3. Technical Implementation Details

### API Endpoints

#### Order Management

**GET /api/orders/{orderId}**
- Purpose: Retrieves detailed information for a specific order
- Parameters: orderId (int): Order identifier
- Returns: Order details with items and status
- Success: 200 OK
- Error: 404 Not Found

```mermaid
flowchart TD
    Client[Client App] -->|View Order| API[Ordering API]
    API -->|Fetch Order| Services[Order Services]
    Services -->|Query Order| DB[(Database)]
    DB -->|Return Order| Services
    Services -->|Include Items| API
    API -->|Send Details| Client

    click API "https://github.com/your-repo/automated-doc-poc-repo/blob/main/src/Ordering.API/Apis/OrdersApi.cs"
    click Services "https://github.com/your-repo/automated-doc-poc-repo/blob/main/src/Ordering.API/Apis/OrderServices.cs"
```

**GET /api/orders/**
- Purpose: Retrieves orders for the current user
- Returns: List of user's orders with summary
- Success: 200 OK
- Error: 401 Unauthorized

```mermaid
flowchart TD
    Client[Client App] -->|List Orders| API[Ordering API]
    API -->|Get User| Auth[(Auth Service)]
    Auth -->|Return UserId| API
    API -->|Fetch Orders| Services[Order Services]
    Services -->|Query User Orders| DB[(Database)]
    DB -->|Return Orders| Services
    Services -->|Format List| API
    API -->|Send Orders| Client

    click API "https://github.com/your-repo/automated-doc-poc-repo/blob/main/src/Ordering.API/Apis/OrdersApi.cs"
    click Services "https://github.com/your-repo/automated-doc-poc-repo/blob/main/src/Ordering.API/Apis/OrderServices.cs"
```

**POST /api/orders/draft**
- Purpose: Creates an order draft from basket contents
- Body: Draft order data
- Returns: Order draft with calculated totals
- Success: 200 OK
- Error: 400 Bad Request

```mermaid
flowchart TD
    Client[Client App] -->|Create Draft| API[Ordering API]
    API -->|Get Basket| BasketSvc[Basket Service]
    BasketSvc -->|Return Items| API
    API -->|Validate Items| CatalogSvc[Catalog Service]
    CatalogSvc -->|Confirm Prices| API
    API -->|Calculate Totals| Services[Order Services]
    Services -->|Create Draft| DB[(Database)]
    DB -->|Return Draft| Services
    Services -->|Format Response| API
    API -->|Send Draft| Client

    click API "https://github.com/your-repo/automated-doc-poc-repo/blob/main/src/Ordering.API/Apis/OrdersApi.cs"
    click BasketSvc "https://github.com/your-repo/automated-doc-poc-repo/blob/main/src/Basket.API/Grpc/BasketService.cs"
    click CatalogSvc "https://github.com/your-repo/automated-doc-poc-repo/blob/main/src/Catalog.API/Apis/CatalogApi.cs"
    click Services "https://github.com/your-repo/automated-doc-poc-repo/blob/main/src/Ordering.API/Apis/OrderServices.cs"
```

**POST /api/orders/**
- Purpose: Creates a new order from draft
- Body: Complete order information
- Returns: Created order details
- Success: 201 Created
- Error: 400 Bad Request, 409 Conflict

```mermaid
flowchart TD
    Client[Client App] -->|Place Order| API[Ordering API]
    API -->|Validate Order| Services[Order Services]
    Services -->|Check Inventory| CatalogSvc[Catalog Service]
    CatalogSvc -->|Confirm Stock| Services
    Services -->|Process Payment| PaymentSvc[Payment Service]
    PaymentSvc -->|Payment Success| Services
    Services -->|Create Order| DB[(Database)]
    DB -->|Return Order| Services
    Services -->|Clear Basket| BasketSvc[Basket Service]
    Services -->|Publish Events| EventBus[(Event Bus)]
    Services -->|Return Success| API
    API -->|Send Order| Client

    click API "https://github.com/your-repo/automated-doc-poc-repo/blob/main/src/Ordering.API/Apis/OrdersApi.cs"
    click Services "https://github.com/your-repo/automated-doc-poc-repo/blob/main/src/Ordering.API/Apis/OrderServices.cs"
    click CatalogSvc "https://github.com/your-repo/automated-doc-poc-repo/blob/main/src/Catalog.API/Apis/CatalogApi.cs"
    click BasketSvc "https://github.com/your-repo/automated-doc-poc-repo/blob/main/src/Basket.API/Grpc/BasketService.cs"
    click EventBus "https://github.com/your-repo/automated-doc-poc-repo/blob/main/src/EventBus/"
```

**PUT /api/orders/cancel**
- Purpose: Cancels an existing order
- Body: Cancellation reason and order ID
- Returns: Updated order status
- Success: 200 OK
- Error: 400 Bad Request, 404 Not Found

```mermaid
flowchart TD
    Client[Client App] -->|Cancel Order| API[Ordering API]
    API -->|Validate Request| Services[Order Services]
    Services -->|Check Status| DB[(Database)]
    DB -->|Return Order| Services
    Services -->|Update Status| DB
    DB -->|Confirm Update| Services
    Services -->|Refund Payment| PaymentSvc[Payment Service]
    Services -->|Publish Events| EventBus[(Event Bus)]
    Services -->|Return Updated| API
    API -->|Send Response| Client

    click API "https://github.com/your-repo/automated-doc-poc-repo/blob/main/src/Ordering.API/Apis/OrdersApi.cs"
    click Services "https://github.com/your-repo/automated-doc-poc-repo/blob/main/src/Ordering.API/Apis/OrderServices.cs"
    click EventBus "https://github.com/your-repo/automated-doc-poc-repo/blob/main/src/EventBus/"
```

**PUT /api/orders/ship**
- Purpose: Marks an order as shipped
- Body: Shipping details and order ID
- Returns: Updated order status
- Success: 200 OK
- Error: 400 Bad Request, 404 Not Found

```mermaid
flowchart TD
    Client[Client App] -->|Ship Order| API[Ordering API]
    API -->|Validate Request| Services[Order Services]
    Services -->|Check Status| DB[(Database)]
    DB -->|Return Order| Services
    Services -->|Update Status| DB
    DB -->|Confirm Update| Services
    Services -->|Publish Events| EventBus[(Event Bus)]
    Services -->|Return Updated| API
    API -->|Send Response| Client

    click API "https://github.com/your-repo/automated-doc-poc-repo/blob/main/src/Ordering.API/Apis/OrdersApi.cs"
    click Services "https://github.com/your-repo/automated-doc-poc-repo/blob/main/src/Ordering.API/Apis/OrderServices.cs"
    click EventBus "https://github.com/your-repo/automated-doc-poc-repo/blob/main/src/EventBus/"
```

**GET /api/orders/cardtypes**
- Purpose: Retrieves available payment card types
- Returns: List of supported card types
- Success: 200 OK

```mermaid
flowchart TD
    Client[Client App] -->|Get Card Types| API[Ordering API]
    API -->|Fetch Types| Services[Order Services]
    Services -->|Query Types| DB[(Database)]
    DB -->|Return Types| Services
    Services -->|Format List| API
    API -->|Send Types| Client

    click API "https://github.com/your-repo/automated-doc-poc-repo/blob/main/src/Ordering.API/Apis/OrdersApi.cs"
    click Services "https://github.com/your-repo/automated-doc-poc-repo/blob/main/src/Ordering.API/Apis/OrderServices.cs"
```

### Request/Response Examples

#### Create Order Request
```json
{
  "userId": "string",
  "userName": "string",
  "city": "string",
  "street": "string",
  "state": "string",
  "country": "string",
  "zipCode": "string",
  "cardNumber": "string",
  "cardHolderName": "string",
  "cardExpiration": "2025-09-05T00:00:00Z",
  "cardSecurityNumber": "string",
  "cardTypeId": 1,
  "buyer": "string",
  "items": [
    {
      "productId": "string",
      "productName": "string",
      "unitPrice": 0,
      "units": 0,
      "pictureUrl": "string"
    }
  ]
}
```

### Key Components

1. Domain Layer (`Ordering.Domain`):
   - Order Aggregate Root with Order and OrderItem entities
   - Buyer Aggregate Root for customer information
   - Domain events for order status changes
   - Repository interfaces

2. Infrastructure Layer (`Ordering.Infrastructure`):
   - EntityFramework implementation of repositories
   - Database context and migrations
   - Idempotency handling

3. Application Layer (`Ordering.API`):
   - Command handlers for order operations
   - Query handlers for order retrieval
   - Integration event handlers
   - Validators for commands

## 4. Validation and Error Handling

### Input Validation
- Command validation using FluentValidation
- Order items validation (quantity, price)
- Address information validation
- Payment information validation

### Error Scenarios
1. Invalid Order Creation:
   - Missing required fields
   - Invalid payment information
   - Non-existent products

2. Order Processing Failures:
   - Payment verification failure
   - Stock validation failure
   - Shipping address validation failure

### Retry Mechanisms
- Integration events use RabbitMQ for reliable messaging
- Idempotency handling for order creation
- Transactional consistency for order status updates

## 5. Security and Access Control

### Authentication
- JWT-based authentication
- Identity service integration
- Claims-based authorization

### Authorization
- User can only access their own orders
- Administrative endpoints require elevated privileges
- Payment information is encrypted

## 6. Testing Strategy

### Unit Tests
- Domain model behavior testing
- Command handler testing
- Validation rules testing

### Integration Tests
- API endpoint testing
- Database integration testing
- Event handling testing

### End-to-End Tests
- Order creation workflow
- Payment processing
- Status update scenarios

## 7. Deployment Considerations

### Dependencies
- SQL Server database
- RabbitMQ for event bus
- Identity Server for authentication

### Configuration
- Database connection strings
- RabbitMQ connection settings
- API versioning settings
- Authentication settings

### Monitoring
- Application Insights integration
- Order processing metrics
- Payment processing success rate
- API response times

## 8. References


### Source Code
- [Order Aggregate Root](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Domain/AggregatesModel/OrderAggregate/Order.cs)
- [Order Repository](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Infrastructure/Repositories/OrderRepository.cs)
- [Orders API](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.API/Apis/OrdersApi.cs)

### Related Components
- Identity.API - User authentication
- Basket.API - Shopping cart management
- Payment Processor - Payment handling
- Event Bus - Integration events

### Integration Events
- OrderStartedEvent
- OrderStatusChangedEvent
- OrderCancelledEvent
- OrderShippedEvent
