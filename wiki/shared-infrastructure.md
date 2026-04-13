# Shared Infrastructure

This document covers the cross-cutting libraries and shared components that support all services in the eShop platform.

## EventBus (Abstractions)

**Location**: `src/EventBus/`

The EventBus library defines transport-agnostic contracts for integration events. No broker code exists here.

### Core Interfaces

| Interface | Purpose |
|-----------|---------|
| `IEventBus` | Single method: `PublishAsync(IntegrationEvent)` |
| `IIntegrationEventHandler<T>` | Generic handler: `Handle(T)` where T is an `IntegrationEvent` |
| `IEventBusBuilder` | DI builder (wraps `IServiceCollection`) for broker configuration |

### IntegrationEvent Base

Every event gets a unique `Id` (GUID) and `CreationDate` (UTC) on construction. JSON serialization includes both fields.

### Subscription Model

`EventBusBuilderExtensions.AddSubscription<T, TH>()`:
1. Registers handler as a **keyed transient** service (key = `typeof(T)`)
2. Updates `EventBusSubscriptionInfo` to map event type name -> CLR type

This enables multiple handlers per event type and type-safe deserialization without `Type.GetType()` (important for AOT/trimming).

## EventBusRabbitMQ

**Location**: `src/EventBusRabbitMQ/`

RabbitMQ implementation of `IEventBus`, registered as both a singleton and `IHostedService`.

### Exchange and Queue Topology

| Component | Configuration |
|-----------|--------------|
| Exchange | `eshop_event_bus`, type: **direct** |
| Queue | Named by `EventBusOptions.SubscriptionClientName` (per service), **durable** |
| Bindings | One binding per subscribed event type (routing key = type name) |
| Delivery | Persistent (`DeliveryMode = 2`), mandatory |

### Publishing

1. Creates a channel and declares the exchange
2. Serializes event using `EventBusSubscriptionInfo.JsonSerializerOptions`
3. Injects OpenTelemetry trace context into message headers
4. Publishes with Polly retry (exponential backoff, retries on `BrokerUnreachableException` / `SocketException`)

### Consuming

On `StartAsync`, creates a long-running consumer task:
1. Declares exchange + durable queue
2. Binds queue for each registered event type
3. Uses `AsyncEventingBasicConsumer` with `autoAck: false`
4. On message: extracts trace context, deserializes by routing key, resolves all keyed handlers from DI scope, invokes sequentially
5. Always acknowledges (no dead-letter exchange in this sample)

### Configuration

```json
{
  "EventBus": {
    "SubscriptionClientName": "ordering-api",
    "RetryCount": 10
  }
}
```

## IntegrationEventLogEF (Transactional Outbox)

**Location**: `src/IntegrationEventLogEF/`

Provides a relational outbox for EF Core contexts. Events are persisted atomically with domain changes, then published separately.

### IntegrationEventLogEntry

| Column | Type | Purpose |
|--------|------|---------|
| `EventId` | GUID | Primary key |
| `EventTypeName` | string | Full CLR type name |
| `Content` | string | JSON-serialized event |
| `State` | enum | `NotPublished` / `InProgress` / `Published` / `PublishedFailed` |
| `TimesSent` | int | Publish attempt counter |
| `CreationTime` | DateTime | When the event was created |
| `TransactionId` | string | Links to the EF transaction |

### Service Interface

| Method | Purpose |
|--------|---------|
| `RetrieveEventLogsPendingToPublishAsync(transactionId)` | Get `NotPublished` events for a transaction |
| `SaveEventAsync(event, transaction)` | Persist event in the same transaction |
| `MarkEventAsPublishedAsync(eventId)` | Update state to `Published` |
| `MarkEventAsInProgressAsync(eventId)` | Update state to `InProgress` |
| `MarkEventAsFailedAsync(eventId)` | Update state to `PublishedFailed` |

### ResilientTransaction

Wraps EF's `IExecutionStrategy` with explicit `BeginTransactionAsync` for retry-safe transactions.

### Usage

Used by **Ordering.API** (via `OrderingIntegrationEventService`) and **Catalog.API** (via `CatalogIntegrationEventService`). Both call `UseIntegrationEventLogs()` on their DbContext to include the `IntegrationEventLog` table.

## eShop.ServiceDefaults

**Location**: `src/eShop.ServiceDefaults/`

Shared cross-cutting concerns applied to all services.

### AddServiceDefaults vs AddBasicServiceDefaults

| Method | Health Checks | OpenTelemetry | HTTP Client Resilience | Service Discovery |
|--------|:---:|:---:|:---:|:---:|
| `AddBasicServiceDefaults` | Yes | Yes | No | No |
| `AddServiceDefaults` | Yes | Yes | Yes | Yes |

**Basket.API** and **OrderProcessor** use `AddBasicServiceDefaults` (no outgoing HTTP calls needed). All other services use `AddServiceDefaults`.

### OpenTelemetry

Configured in `ConfigureOpenTelemetry`:

| Signal | Instrumentations |
|--------|-----------------|
| **Logging** | OpenTelemetry log provider |
| **Metrics** | ASP.NET Core, HttpClient, .NET runtime, AI experimental |
| **Tracing** | ASP.NET Core, gRPC client, HttpClient, AI source |
| **Sampling** | `AlwaysOnSampler` in development |
| **Export** | OTLP when `OTEL_EXPORTER_OTLP_ENDPOINT` is set |

### Health Checks

`MapDefaultEndpoints` (development only):
- `/health` -> all registered health checks
- `/alive` -> checks tagged with `live` only

### Authentication

`AddDefaultAuthentication`:
- JWT Bearer with authority from `Identity:Url`
- Audience from `Identity:Audience`
- No HTTPS metadata requirement
- Preserves `sub` claim (no default mapping override)

### OpenAPI

`AddDefaultOpenApi` / `UseDefaultOpenApi`:
- OpenAPI v3 documents for v1/v2
- OAuth2 security scheme from `Identity:Scopes`
- Scalar UI in development (root `/` redirects to `/scalar/v1`)
- Clears `document.Servers` for correct Aspire port display

### HTTP Client Defaults

`ConfigureHttpClientDefaults`:
- Standard resilience handler (circuit breaker, retry, timeout)
- Service discovery integration
- Auth token forwarding via `AddAuthToken()`

## Shared Code (`src/Shared/`)

Linked files shared across multiple projects:

| File | Purpose | Used By |
|------|---------|---------|
| `ActivityExtensions.cs` | OpenTelemetry activity/propagation helpers | EventBusRabbitMQ |
| `MigrateDbContextExtensions.cs` | EF Core migration + seed on startup | Ordering, Catalog, Identity |
