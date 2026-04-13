# Catalog Service

The Catalog.API manages the product catalog: items, brands, types, images, pricing, stock, and optional AI-powered semantic search. It uses a simpler architecture than Ordering (no DDD/CQRS), favoring direct EF Core operations with minimal API endpoints.

## Project Structure

```
src/Catalog.API/
├── Program.cs                    # Host pipeline
├── Apis/CatalogApi.cs           # All endpoint definitions
├── Infrastructure/               # EF context, seed data
├── Model/                        # Entity classes
├── IntegrationEvents/            # Outbox service, handlers, events
├── Extensions/                   # DI registration
└── appsettings*.json            # Configuration
```

## Technology

- **Framework**: ASP.NET Core minimal APIs with API versioning (v1 + v2)
- **Database**: PostgreSQL with pgvector extension for vector similarity search
- **ORM**: Entity Framework Core + Npgsql
- **Messaging**: RabbitMQ (pub/sub) with transactional outbox
- **AI** (optional): Ollama or OpenAI embeddings for semantic catalog search

## Data Model

### CatalogItem

The central entity representing a product:

| Property | Type | Purpose |
|----------|------|---------|
| `Id` | `int` | Primary key |
| `Name` | `string` | Product name |
| `Description` | `string` | Product description |
| `Price` | `decimal` | Current price |
| `PictureFileName` | `string` | Image file name (served from `Pics/` directory) |
| `CatalogTypeId` / `CatalogType` | `int` / `CatalogType` | Product category |
| `CatalogBrandId` / `CatalogBrand` | `int` / `CatalogBrand` | Product brand |
| `AvailableStock` | `int` | Current stock quantity |
| `RestockThreshold` | `int` | Level at which to reorder |
| `MaxStockThreshold` | `int` | Maximum stock capacity |
| `OnReorder` | `bool` | Whether reorder has been triggered |
| `Embedding` | `Vector` | 384-dimensional embedding for semantic search (JSON-ignored) |

**Domain methods**:
- `RemoveStock(quantity)`: Decrements `AvailableStock`, sets `OnReorder` if below threshold. Throws `CatalogDomainException` if insufficient stock.
- `AddStock(quantity)`: Increments stock, caps at `MaxStockThreshold`, clears `OnReorder` flag.

### Lookup Entities

- **CatalogBrand**: `Id`, `Brand` (name)
- **CatalogType**: `Id`, `Type` (name)

## API Endpoints

All routes under `/api/catalog`, versioned v1 and v2. No authentication is required.

### Item CRUD

| Method | Route (v1) | Route (v2) | Purpose |
|--------|-----------|-----------|---------|
| `GET` | `/items` | `/items?pageSize&pageIndex&brand&type` | Paginated list (v2 adds filters) |
| `GET` | `/items/{id}` | same | Single item by ID |
| `GET` | `/items/by?ids=` | same | Multiple items by IDs |
| `GET` | `/items/{id}/pic` | same | Product image file |
| `POST` | `/items` | same | Create item |
| `PUT` | `/items` (body has id) | `/items/{id}` (route param) | Update/upsert item |
| `DELETE` | `/items/{id}` | same | Delete item |

### Semantic Search

| Method | Route (v1) | Route (v2) | Purpose |
|--------|-----------|-----------|---------|
| `GET` | `/items/withsemanticrelevance/{text}` | `/items/withsemanticrelevance?text=` | AI-powered semantic search |

When AI is enabled, searches use cosine distance against the `Embedding` column. When disabled, v2 falls back to a name-prefix `LIKE` search.

### Metadata

| Method | Route | Purpose |
|--------|-------|---------|
| `GET` | `/catalogtypes` | List all product types |
| `GET` | `/catalogbrands` | List all product brands |

## Persistence

### CatalogContext

- **Database**: PostgreSQL with `HasPostgresExtension("vector")` for pgvector
- **Schema**: Default (no custom schema)
- **Outbox**: `UseIntegrationEventLogs()` for transactional event publishing
- **Seed**: `CatalogContextSeed` for initial data in development

### AI / Embeddings

`ICatalogAI` / `CatalogAI` computes embeddings using `IEmbeddingGenerator`:
- **Ollama**: When `OllamaEnabled` configuration is true
- **OpenAI**: When a `textEmbeddingModel` connection exists
- **Disabled**: When neither is configured; semantic search degrades to name search

Embeddings are generated on item create/update and stored in the `Embedding` column (384 dimensions).

## Integration Events

### Published Events

| Event | When | Outbox? |
|-------|------|---------|
| `ProductPriceChangedIntegrationEvent` | Price changes on item update | Yes (same transaction as price update) |
| `OrderStockConfirmedIntegrationEvent` | All order items have sufficient stock | Yes |
| `OrderStockRejectedIntegrationEvent` | One or more items have insufficient stock | Yes |

### Consumed Events

| Event | Handler | Action |
|-------|---------|--------|
| `OrderStatusChangedToAwaitingValidationIntegrationEvent` | Checks stock for each order item, publishes confirmed or rejected event |
| `OrderStatusChangedToPaidIntegrationEvent` | Calls `RemoveStock` on each order item to decrement inventory |

### Outbox Pattern

`CatalogIntegrationEventService` coordinates with `IntegrationEventLogService<CatalogContext>`:
1. `SaveEventAndCatalogContextChangesAsync`: Saves domain changes + event log entry in a resilient transaction
2. `PublishThroughEventBusAsync`: Marks event in-progress, publishes to RabbitMQ, marks published/failed

## DI Registration

Key registrations in `AddApplicationServices` (`Extensions.cs`):
- `CatalogContext` with PostgreSQL + Npgsql + pgvector
- Migration and seed in development
- `IIntegrationEventLogService` -> `IntegrationEventLogService<CatalogContext>`
- `ICatalogIntegrationEventService` -> `CatalogIntegrationEventService`
- RabbitMQ event bus with 2 subscriptions
- `CatalogOptions` from configuration
- Optional AI services (Ollama/OpenAI embedding generator)
