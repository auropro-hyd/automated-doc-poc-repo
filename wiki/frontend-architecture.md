# Frontend Architecture

The eShop platform has four client applications, each targeting a different form factor. There is no JavaScript/Node.js frontend; all UI is .NET-based (Blazor and MAUI).

## Application Overview

| App | Technology | Form Factor | Backend Access |
|-----|-----------|-------------|---------------|
| **WebApp** | Blazor Server | Web browser | Direct: gRPC (basket), HTTP (catalog, ordering), OIDC (identity) |
| **WebAppComponents** | Razor Class Library | Shared UI | Consumed by WebApp and HybridApp |
| **ClientApp** | .NET MAUI (XAML) | Mobile (iOS/Android) | HTTP via gateway endpoints |
| **HybridApp** | MAUI + Blazor WebView | Mobile + Web hybrid | HTTP via Mobile BFF |

## WebApp (Blazor Server)

### Architecture

The WebApp is a **Blazor Server** application. All component logic runs on the server with real-time UI updates over SignalR. It is the primary storefront.

### Component Hierarchy

```
App.razor
└── Routes.razor
    └── MainLayout.razor
        ├── HeaderBar.razor
        │   ├── UserMenu.razor
        │   └── CartMenu.razor
        ├── @Body (page content)
        │   ├── Catalog.razor (/)
        │   ├── ItemPage.razor (/item/{id})
        │   ├── CartPage.razor (/cart)
        │   ├── Checkout.razor (/checkout) [Authorize]
        │   ├── Orders.razor (/user/orders)
        │   │   └── OrdersRefreshOnStatusChange.razor
        │   ├── LogIn.razor (/user/login)
        │   └── LogOut.razor (/user/logout)
        ├── ShowChatbotButton.razor
        │   └── Chatbot.razor
        └── FooterBar.razor
```

### Page Routes

| Route | Component | Auth Required | Description |
|-------|-----------|:---:|-------------|
| `/` | `Catalog.razor` | No | Product browsing with search, brand/type filters |
| `/item/{itemId:int}` | `ItemPage.razor` | No | Product detail page |
| `/cart` | `CartPage.razor` | No | Shopping cart with quantity editing |
| `/checkout` | `Checkout.razor` | Yes | Order placement with address/payment |
| `/user/orders` | `Orders.razor` | Yes | Order history with real-time status updates |
| `/user/login` | `LogIn.razor` | No | OIDC login redirect |
| `/user/logout` | `LogOut.razor` | No | Sign out |

### Service Integrations

| Service | Protocol | Client Type | Registration |
|---------|----------|------------|--------------|
| Basket.API | gRPC | `Basket.BasketClient` | `AddGrpcClient` -> `http://basket-api` |
| Catalog.API | HTTP | `CatalogService` (from WebAppComponents) | `AddHttpClient` -> `http://catalog-api`, API v2 |
| Ordering.API | HTTP | `OrderingService` | `AddHttpClient` -> `http://ordering-api`, API v1 |
| Identity.API | OIDC | Cookie + OpenID Connect | `AddAuthentication` with Identity URL |

### Basket State Management

`BasketState` (scoped service) orchestrates the shopping cart UX:
- Combines gRPC basket quantities with catalog item details from `CatalogService`
- Publishes change notifications for UI reactivity
- Handles checkout: maps basket items to `CreateOrderRequest`, calls `OrderingService.CreateOrder`, then clears basket

### Real-Time Order Status

`OrderStatusNotificationService` (singleton) receives RabbitMQ integration events for order status changes. `OrdersRefreshOnStatusChange` (Interactive Server component) subscribes by buyer ID and calls `NavigationManager.Refresh()` when updates arrive.

### Product Image Proxy

Images are served via YARP forwarding in `Program.cs`:
```
/product-images/{id} -> http://catalog-api/api/catalog/items/{id}/pic
```

`ProductImageUrlProvider` generates relative URLs like `/product-images/{id}?api-version=2.0`.

### Authentication

Cookie + OpenID Connect to Identity.API. Scopes include `orders` and `basket`. Blazor uses `ServerAuthenticationStateProvider` with cascading `AuthenticationState`.

### AI Chatbot (Optional)

When configured, `AddAIServices` wires Ollama or OpenAI for an in-app chatbot (`Chatbot.razor`).

## WebAppComponents (Shared Razor Class Library)

**Location**: `src/WebAppComponents/`

A Razor Class Library consumed by both WebApp and HybridApp.

### Contents

| Component/Service | Purpose |
|------------------|---------|
| `CatalogSearch.razor` | Search input with brand/type filter dropdowns |
| `CatalogListItem.razor` | Product tile (image, name, price) |
| `ICatalogService` / `CatalogService` | HTTP JSON client for catalog endpoints |
| `IProductImageUrlProvider` | Abstraction for product image URLs |
| `CatalogItem`, `CatalogBrand`, `CatalogType` | Shared DTOs |
| `ItemHelper` | URL helper for product links |

**Key design decision**: The shared `ICatalogService` interface allows each host to provide its own implementation. WebApp registers `CatalogService` pointing to `http://catalog-api`. HybridApp registers its own `CatalogService` pointing to the Mobile BFF with `api-version` query parameters.

## ClientApp (.NET MAUI)

**Location**: `src/ClientApp/`

A native .NET MAUI application using XAML views and MVVM architecture.

### Shell Navigation

```
AppShell
├── Flyout: LoginView (route: "Login")
└── TabBar (route: "Main")
    ├── Tab: CatalogView ("Catalog")
    ├── Tab: MapView ("Map") [hidden on Windows]
    └── Tab: ProfileView ("ORDERS")
```

### Architecture Pattern

MVVM with dependency injection:
- **Views**: XAML pages (Catalog, Cart, Checkout, Profile, Settings)
- **ViewModels**: Business logic, service calls, property change notification
- **Services**: `IRequestProvider` (HTTP), `IIdentityService` (OIDC), `IAppEnvironmentService`

### Mock vs Real Mode

`AppEnvironmentService` supports a **mock mode** (default on first launch). When `UseMocks` is toggled in Settings, it swaps between mock and real service implementations for basket, catalog, ordering, and identity.

### Backend Access

Uses `IRequestProvider` (HTTP client) against configured gateway endpoints from `ISettingsService`. Does **not** use the WebAppComponents shared library for its main UI.

## HybridApp (MAUI + Blazor WebView)

**Location**: `src/HybridApp/`

A .NET MAUI app that hosts Blazor components inside a WebView.

### Architecture

```
App (MAUI)
└── MainPage (ContentPage)
    └── BlazorWebView
        └── Routes.razor (Blazor router)
            └── MainLayout
                ├── HeaderBar (simplified: no user/cart)
                ├── @Body (Catalog pages only)
                └── FooterBar
```

### Scope

Currently implements **catalog browsing only** (no cart, checkout, or auth). User menu and cart are commented out in `HeaderBar`. The chatbot is also disabled.

### Backend Access

Uses a local `CatalogService` that points to the Mobile BFF (`http://10.0.2.2:11632` on Android, `http://localhost:11632` elsewhere) and appends `api-version=2.0` query parameters.

### Shared vs Local Components

| Component | Source |
|-----------|--------|
| `CatalogListItem.razor` | WebAppComponents (shared) |
| `CatalogSearch.razor` | Local override in HybridApp |
| `CatalogService` | Local implementation (BFF-targeted) |
| `IProductImageUrlProvider` | Local implementation |
