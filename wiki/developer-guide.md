# Developer Guide

This guide provides everything needed to set up, understand, and contribute to the eShop codebase and its documentation generator.

## Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| .NET SDK | 8.0+ | Build and run .NET services |
| .NET Aspire workload | Latest | `dotnet workload install aspire` |
| Python | 3.10+ | Documentation generator |
| Docker | Latest | PostgreSQL, Redis, RabbitMQ containers (via Aspire) |
| Git | Latest | Version control |

## Repository Setup

### 1. Clone and Install

```bash
git clone <repo-url>
cd automated-doc-poc-repo

# .NET: Aspire handles infrastructure via Docker
dotnet workload install aspire

# Python: Doc generator setup
make setup    # Creates venv, installs requirements.txt
```

### 2. Configure the Doc Generator

```bash
cp project_config.yml.template project_config.yml
cp .env.template .env
# Edit both files with your settings (LLM API keys, repo URL, etc.)
```

### 3. Run the System

```bash
# Start all services via Aspire
cd src/eShop.AppHost
dotnet run

# The Aspire dashboard opens at https://localhost:15888
# Services are accessible at their Aspire-assigned ports
```

## Project Structure Quick Reference

```
automated-doc-poc-repo/
├── src/
│   ├── eShop.AppHost/          # START HERE: Aspire orchestrator
│   ├── Ordering.API/           # Complex: DDD/CQRS (start reading here for patterns)
│   ├── Catalog.API/            # Simpler: CRUD + minimal APIs
│   ├── Basket.API/             # Simplest: gRPC + Redis
│   ├── Identity.API/           # Auth: Duende IdentityServer
│   ├── Ordering.Domain/        # Pure domain model (no framework deps)
│   ├── Ordering.Infrastructure/# EF Core persistence
│   ├── OrderProcessor/         # Background worker
│   ├── PaymentProcessor/       # Event-driven processor
│   ├── WebApp/                 # Blazor Server storefront
│   ├── EventBus/               # Event abstractions
│   ├── EventBusRabbitMQ/       # RabbitMQ implementation
│   ├── IntegrationEventLogEF/  # Transactional outbox
│   └── eShop.ServiceDefaults/  # Shared cross-cutting concerns
├── doc_generator/              # Python doc generation pipeline
├── wiki/                       # This wiki
└── Makefile                    # Useful commands
```

## Key Architectural Concepts

Before diving into the code, understand these patterns:

1. **Read [Design Patterns](design-patterns.md)** for DDD, CQRS, and outbox pattern explanations
2. **Read [Data Flow](data-flow.md)** for the complete order lifecycle and integration events
3. **Read [System Overview](system-overview.md)** for the high-level architecture

## Common Development Tasks

### Adding a New API Endpoint (Ordering)

1. Define the command in `Application/Commands/` (implement `IRequest<T>`)
2. Create the handler (implement `IRequestHandler<TCommand, TResult>`)
3. Add a validator in `Application/Validations/` (implement `AbstractValidator<T>`)
4. Map the endpoint in `Apis/OrdersApi.cs`
5. If the endpoint needs idempotency, wrap in `IdentifiedCommand<T, R>` and use `x-requestid` header

### Adding a New Integration Event

1. Define the event class in the publishing service's `IntegrationEvents/Events/` (extend `IntegrationEvent`)
2. In the publishing service: use `IOrderingIntegrationEventService.AddAndSaveEventAsync` (ordering) or `ICatalogIntegrationEventService.SaveEventAndCatalogContextChangesAsync` (catalog)
3. In the consuming service:
   - Define the handler (implement `IIntegrationEventHandler<TEvent>`)
   - Register: `eventBus.AddSubscription<TEvent, THandler>()` in `Extensions.cs`
   - Add JSON serialization context if using source generators

### Adding a New Domain Event (Ordering)

1. Define the event in `Ordering.Domain/Events/` (implement `INotification`)
2. Raise it from the aggregate method: `AddDomainEvent(new MyDomainEvent(...))`
3. Create the handler in `Application/DomainEventHandlers/` (implement `INotificationHandler<T>`)
4. The handler runs within the same transaction as the originating command

### Adding a New Catalog Endpoint

1. Add the route mapping in `Apis/CatalogApi.cs`
2. Use `CatalogServices` parameter object for dependencies
3. Work with `CatalogContext` directly (no CQRS layer)
4. If the change involves integration events, use `ICatalogIntegrationEventService`

### Generating Documentation

```bash
# Generate for one API
make generate API=ordering

# Generate for all configured APIs
make generate-all

# Preview the docs site
make serve
# Open http://127.0.0.1:8000
```

### Adding a New API to the Doc Generator

1. Add an entry in `project_config.yml` under `apis`:
```yaml
apis:
  newservice:
    display_name: "New Service"
    source_paths: ["src/NewService.API"]
    dependent_libraries: ["src/NewService.Domain"]
```

2. Add classification rules if new file patterns exist:
```yaml
classification_rules:
  - pattern: "NewPattern/.*\\.cs$"
    category: "handler"
    doc_file: "Handlers.md"
    doc_title: "Handlers"
```

3. Run: `make generate API=newservice`

## Coding Conventions

### .NET Services

- **Minimal APIs**: Use `MapXxxApi()` extension methods for endpoint groups
- **DI registration**: Centralize in `Extensions/Extensions.cs` with `AddApplicationServices()`
- **Shared defaults**: Always call `AddServiceDefaults()` or `AddBasicServiceDefaults()` in `Program.cs`
- **Global usings**: Use `GlobalUsings.cs` for common imports
- **Health checks**: Available at `/health` and `/alive` in development

### Domain Layer (Ordering.Domain)

- No framework dependencies (pure C#)
- Aggregates enforce invariants in methods (not constructors)
- Domain events are raised from aggregate methods, not handlers
- Repository interfaces live in the domain; implementations in infrastructure

### Documentation Generator (Python)

- Configuration-driven: all paths, rules, and LLM settings in `project_config.yml`
- Prompts are template functions in `llm/prompts.py`
- Post-processing fixes LLM output (link resolution, mermaid sanitization, table formatting)
- Navigation merges non-destructively with existing `mkdocs.yml` entries

## Troubleshooting

### Aspire AppHost fails to build

The AppHost references `Webhooks.API` which is not in this repository. Comment out or remove the `Webhooks_API` project reference in `eShop.AppHost.csproj` and the related lines in `Program.cs`.

### Services can't connect to each other

Ensure Docker Desktop is running (Aspire uses Docker for PostgreSQL, Redis, RabbitMQ). Check the Aspire dashboard for service health and connection errors.

### JWT authentication fails

Verify that `Identity:Url` in each service's `appsettings.json` matches the Identity.API's actual endpoint. In Aspire, this is injected automatically.

### Doc generator LLM errors

Check `.env` for valid API keys. Use `make dry-run API=ordering` to verify parsing works without LLM calls. Check `project_config.yml` for correct `llm.provider` and `llm.model` settings.

## Useful Makefile Commands

| Command | Purpose |
|---------|---------|
| `make setup` | Create Python venv and install dependencies |
| `make generate API=<key>` | Generate docs for one API |
| `make generate-all` | Generate docs for all APIs |
| `make regenerate API=<key>` | Clean + regenerate for one API |
| `make dry-run API=<key>` | Parse and classify without LLM calls |
| `make serve` | Start MkDocs dev server |
| `make build` | Build static MkDocs site |
| `make list` | List configured APIs |
| `make validate-config` | Validate project_config.yml |
| `make clean` | Preview files to delete |
| `make clean-confirm` | Actually delete generated docs |
