# eShop System Wiki

A comprehensive knowledge base for the eShop microservices platform and its automated documentation generator. This wiki provides everything a developer needs to understand, extend, and maintain the system independently.

## Table of Contents

### Architecture and Design

| Document | Description |
|----------|-------------|
| [System Overview](system-overview.md) | High-level architecture, technology stack, service map, and deployment topology |
| [Design Patterns and Architectural Decisions](design-patterns.md) | DDD, CQRS, Event-Driven Architecture, Outbox pattern, and key trade-offs |
| [Data Flow and Integration Events](data-flow.md) | End-to-end message flows, event catalog, and saga choreography |
| [API Design and Contracts](api-design.md) | Endpoint inventory, versioning strategy, authentication, and OpenAPI |

### Service Documentation

| Document | Description |
|----------|-------------|
| [Ordering Service](ordering-service.md) | DDD bounded context: aggregates, commands, queries, domain events, infrastructure |
| [Catalog Service](catalog-service.md) | Product catalog: CRUD, semantic search, stock management, EF + pgvector |
| [Basket Service](basket-service.md) | Shopping cart: gRPC, Redis persistence, integration events |
| [Identity Service](identity-service.md) | Authentication: Duende IdentityServer, OIDC/OAuth2, user management |
| [Shared Infrastructure](shared-infrastructure.md) | EventBus, RabbitMQ, ServiceDefaults, IntegrationEventLogEF, and cross-cutting concerns |

### Frontend and Clients

| Document | Description |
|----------|-------------|
| [Frontend Architecture](frontend-architecture.md) | WebApp (Blazor), WebAppComponents (RCL), ClientApp (MAUI), HybridApp (MAUI+Blazor) |

### Platform and Tooling

| Document | Description |
|----------|-------------|
| [Aspire Orchestration and Deployment](aspire-orchestration.md) | .NET Aspire AppHost, service wiring, local development, and infrastructure resources |
| [Documentation Generator](doc-generator.md) | Python pipeline: parse, classify, generate (LLM), assemble, and MkDocs integration |
| [Developer Guide](developer-guide.md) | Environment setup, project structure, coding conventions, and contribution workflow |

## Repository Structure

```
automated-doc-poc-repo/
├── src/                          # .NET source code (18 projects)
│   ├── Ordering.API/             # Order management API (CQRS/DDD)
│   ├── Ordering.Domain/          # Domain model (aggregates, events)
│   ├── Ordering.Infrastructure/  # EF Core persistence
│   ├── Catalog.API/              # Product catalog API
│   ├── Basket.API/               # Shopping cart gRPC service
│   ├── Identity.API/             # IdentityServer (auth)
│   ├── OrderProcessor/           # Background grace-period worker
│   ├── PaymentProcessor/         # Fake payment event handler
│   ├── WebApp/                   # Blazor Server storefront
│   ├── WebAppComponents/         # Shared Razor class library
│   ├── ClientApp/                # .NET MAUI mobile app
│   ├── HybridApp/                # MAUI + Blazor WebView
│   ├── Mobile.Bff.Shopping/      # YARP reverse proxy (BFF)
│   ├── WebhookClient/            # Webhooks demo client
│   ├── EventBus/                 # Event bus abstractions
│   ├── EventBusRabbitMQ/         # RabbitMQ implementation
│   ├── IntegrationEventLogEF/    # Transactional outbox (EF)
│   ├── eShop.ServiceDefaults/    # Shared defaults (OTel, auth, health)
│   ├── eShop.AppHost/            # .NET Aspire orchestrator
│   └── docs/                     # MkDocs documentation site
├── doc_generator/                # Python doc generation pipeline
├── wiki/                         # This wiki
├── Makefile                      # Build/serve/generate commands
├── project_config.yml            # Doc generator configuration
└── requirements.txt              # Python dependencies
```
