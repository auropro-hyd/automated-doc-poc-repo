# Basket Service

The Basket.API is a gRPC-only service managing per-user shopping carts with Redis as the data store. It is architecturally the simplest backend service, following a straightforward CRUD approach.

## Project Structure

```
src/Basket.API/
├── Program.cs                                    # Host pipeline
├── Grpc/BasketService.cs                        # gRPC service implementation
├── Proto/basket.proto                           # gRPC contract definition
├── Repositories/
│   ├── IBasketRepository.cs                     # Repository interface
│   └── RedisBasketRepository.cs                 # Redis implementation
├── Model/
│   ├── CustomerBasket.cs                        # Basket model
│   └── BasketItem.cs                            # Line item model
├── IntegrationEvents/
│   ├── Events/OrderStartedIntegrationEvent.cs   # Inbound event
│   └── EventHandling/                           # Handler
├── Extensions/                                   # DI, identity helpers
└── appsettings*.json
```

## Technology

- **Protocol**: gRPC (HTTP/2)
- **Data store**: Redis (JSON document per user)
- **Messaging**: RabbitMQ (consumer only)
- **Serialization**: System.Text.Json source generators (AOT-friendly)

## gRPC Contract

Defined in `Proto/basket.proto`:

| RPC | Request | Response | Purpose |
|-----|---------|----------|---------|
| `GetBasket` | `GetBasketRequest` | `CustomerBasketResponse` | Retrieve user's basket |
| `UpdateBasket` | `UpdateBasketRequest` | `CustomerBasketResponse` | Create/update basket |
| `DeleteBasket` | `DeleteBasketRequest` | `DeleteBasketResponse` | Remove basket |

## Service Implementation

`BasketService` (`Grpc/BasketService.cs`) is registered as a gRPC service.

### GetBasket
- Annotated `[AllowAnonymous]`
- Resolves user identity from `ServerCallContext` -> `HttpContext.User` (`sub` claim)
- If no `sub` claim, returns empty response
- Otherwise loads basket from Redis and maps to proto response

### UpdateBasket
- Requires authenticated user (`sub` claim); returns `Unauthenticated` status if missing
- Maps proto items to `CustomerBasket` model
- Persists via `IBasketRepository.UpdateBasketAsync`
- Returns `NotFound` if the basket is missing after update

### DeleteBasket
- Requires authenticated user
- Calls `IBasketRepository.DeleteBasketAsync`

### Identity Resolution

User identity is extracted from the gRPC host's HTTP context:
```csharp
context.GetHttpContext().User.FindFirst("sub")?.Value
```

**Note**: `AddDefaultAuthentication` registers JWT bearer and authorization services, but `Program.cs` does not explicitly call `UseAuthentication()` / `UseAuthorization()` in the middleware pipeline.

## Data Model

### CustomerBasket

| Property | Type | Purpose |
|----------|------|---------|
| `BuyerId` | `string` | User identifier (from `sub` claim) |
| `Items` | `List<BasketItem>` | Line items in the cart |

### BasketItem

| Property | Type | Purpose |
|----------|------|---------|
| `Id` | `string` | Item identifier |
| `ProductId` | `int` | Catalog product reference |
| `ProductName` | `string` | Display name |
| `UnitPrice` | `decimal` | Current price |
| `OldUnitPrice` | `decimal` | Previous price (for UI strikethrough) |
| `Quantity` | `int` | Quantity in cart |
| `PictureUrl` | `string` | Product image URL |

`BasketItem` implements `IValidatableObject` for quantity validation.

## Persistence (Redis)

`RedisBasketRepository` stores each basket as a UTF-8 JSON string at key `/basket/{userId}`:

| Operation | Redis Command |
|-----------|--------------|
| `GetBasketAsync` | `StringGetLeaseAsync` -> deserialize JSON |
| `UpdateBasketAsync` | Serialize JSON -> `StringSetAsync` |
| `DeleteBasketAsync` | `KeyDeleteAsync` |

Serialization uses `BasketSerializationContext` (source-generated `JsonSerializerContext`) for AOT compatibility.

## Integration Events

### Consumed (Inbound)

| Event | Handler | Action |
|-------|---------|--------|
| `OrderStartedIntegrationEvent` | `OrderStartedIntegrationEventHandler` | Deletes the user's basket (clears cart after checkout) |

The basket does not publish any integration events.

## DI Registration

Key registrations in `AddApplicationServices` (`Extensions.cs`):
- `AddDefaultAuthentication` (JWT bearer with Identity URL)
- `AddRedisClient("redis")` (Aspire Redis integration)
- `IBasketRepository` -> `RedisBasketRepository` (singleton)
- `AddRabbitMqEventBus("eventbus")` with subscription to `OrderStartedIntegrationEvent`
- JSON serializer `TypeInfoResolverChain` entry for `OrderStartedIntegrationEvent`
