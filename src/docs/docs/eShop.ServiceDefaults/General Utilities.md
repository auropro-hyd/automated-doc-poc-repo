# General Utilities

This section documents general utility extension classes in `eShop.ServiceDefaults`.


## Classes

### 1. [Extensions](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/eShop.ServiceDefaults/Extensions.cs)

#### Overview
Provides general-purpose extension methods and helpers used throughout the solution, improving code reuse and maintainability.

#### Methods

##### [`AddServiceDefaults`](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/eShop.ServiceDefaults/Extensions.cs#L16)

- **Overview:**
	Adds service defaults including service discovery, HTTP client resilience, and telemetry to the host builder.

- **Call Graph:**

```mermaid
flowchart LR
    AddServiceDefaults --> AddBasicServiceDefaults
    AddServiceDefaults --> AddServiceDiscovery
    AddServiceDefaults --> ConfigureHttpClientDefaults
```

- **Flow Diagram:**

```mermaid
flowchart LR
    A[Start] --> B[Add Basic Service Defaults]
    B --> C[Add Service Discovery]
    C --> D[Configure HTTP Client Defaults]
    D --> E[Return Builder]
    click B "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/eShop.ServiceDefaults/Extensions.cs#L18" "Basic Defaults"
    click C "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/eShop.ServiceDefaults/Extensions.cs#L21" "Service Discovery"
    click D "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/eShop.ServiceDefaults/Extensions.cs#L23" "HTTP Defaults"
```
1. Starts by adding basic service defaults to the host builder.
2. Adds service discovery capabilities.
3. Configures HTTP client defaults for resilience and discovery.
4. Returns the updated builder for further configuration.

##### [`AddBasicServiceDefaults`](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/eShop.ServiceDefaults/Extensions.cs#L40)

- **Overview:**
	Adds basic service defaults such as health checks and telemetry, without outgoing HTTP calls.

- **Call Graph:**

```mermaid
flowchart LR
    AddBasicServiceDefaults --> AddDefaultHealthChecks
    AddBasicServiceDefaults --> ConfigureOpenTelemetry
```

- **Flow Diagram:**

```mermaid
flowchart LR
    A[Start] --> B[Add Default Health Checks]
    B --> C[Configure OpenTelemetry]
    C --> D[Return Builder]
    click B "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/eShop.ServiceDefaults/Extensions.cs#L42" "Health Checks"
    click C "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/eShop.ServiceDefaults/Extensions.cs#L44" "Telemetry"
```
1. Adds default health checks to the application.
2. Configures OpenTelemetry for logging and metrics.
3. Returns the updated builder for further configuration.

##### [`ConfigureOpenTelemetry`](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/eShop.ServiceDefaults/Extensions.cs#L50)

- **Overview:**
	Configures OpenTelemetry logging and metrics for the host builder.

- **Call Graph:**

```mermaid
flowchart LR
    ConfigureOpenTelemetry --> AddOpenTelemetry
    ConfigureOpenTelemetry --> WithMetrics
    ConfigureOpenTelemetry --> AddOpenTelemetry
```

- **Flow Diagram:**

```mermaid
flowchart LR
    A[Start] --> B[Add OpenTelemetry Logging]
    B --> C[Add OpenTelemetry Metrics]
    C --> D[Return Builder]
    click B "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/eShop.ServiceDefaults/Extensions.cs#L52" "Logging"
    click C "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/eShop.ServiceDefaults/Extensions.cs#L57" "Metrics"
```
1. Adds OpenTelemetry logging to the host builder.
2. Adds OpenTelemetry metrics for observability.
3. Returns the updated builder for further configuration.

##### [`AddDefaultHealthChecks`](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/eShop.ServiceDefaults/Extensions.cs#L99)

- **Overview:**
	Adds default health checks for the application, including event bus and self health checks.

- **Call Graph:**

```mermaid
flowchart LR
    AddDefaultHealthChecks --> AddHealthChecks
```

- **Flow Diagram:**

```mermaid
flowchart LR
    A[Start] --> B[Add Health Checks]
    B --> C[Return Builder]
    click B "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/eShop.ServiceDefaults/Extensions.cs#L100" "Health Checks"
```
1. Adds health checks to the application for monitoring.
2. Returns the updated builder for further configuration.


##### [`MapDefaultEndpoints`](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/eShop.ServiceDefaults/Extensions.cs#L108)

- **Overview:**
	Maps default endpoints for the web application, including health checks and other service endpoints.

- **Call Graph:**

```mermaid
flowchart LR
    MapDefaultEndpoints --> MapEndpoints
```

- **Flow Diagram:**

```mermaid
flowchart LR
    A[Start] --> B[Map Endpoints]
    B --> C[Return WebApplication]
    click B "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/eShop.ServiceDefaults/Extensions.cs#L109" "Map Endpoints"
```
1. Maps default endpoints for the web application.
2. Returns the updated web application instance.
