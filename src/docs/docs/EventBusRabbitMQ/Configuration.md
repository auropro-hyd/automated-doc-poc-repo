# Configuration

## EventBusOptions ([source](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/EventBusRabbitMQ/EventBusOptions.cs#L3-L7))

### Overview
`EventBusOptions` provides configuration settings for the RabbitMQ event bus, including the subscription client name and retry count. It is used to control how the event bus connects and retries operations.

#### Properties

| Key                    | Default | Effect                                                      |
|------------------------|---------|-------------------------------------------------------------|
| SubscriptionClientName | (none)  | Identifies the client for RabbitMQ subscriptions.           |
| RetryCount             | 10      | Number of retry attempts for event bus operations.          |

---

## RabbitMqDependencyInjectionExtensions ([source](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/EventBusRabbitMQ/RabbitMqDependencyInjectionExtensions.cs#L6-L50))

### Overview
`RabbitMqDependencyInjectionExtensions` is a static class that registers RabbitMQ event bus services and telemetry into the application's dependency injection container. It configures options, OpenTelemetry tracing, and ensures the event bus is started as a hosted service.

#### Methods

### AddRabbitMqEventBus ([source](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/EventBusRabbitMQ/RabbitMqDependencyInjectionExtensions.cs#L15-L39))
- **Overview:** Registers all required RabbitMQ event bus services, telemetry, and configuration in the DI container. Ensures consumers are started and OpenTelemetry tracing is enabled.
- **Configuration:**

  | Key                    | Default | Effect                                                      |
  |------------------------|---------|-------------------------------------------------------------|
  | EventBus:SubscriptionClientName | (none)  | Used for event bus client identification.                   |
  | EventBus:RetryCount             | 10      | Used for retry policy in event bus operations.              |
 **Call Graph:**
 ```mermaid
 flowchart LR
   A[AddRabbitMqEventBus] --> B[AddRabbitMQClient]
   A --> C[AddOpenTelemetry]
   A --> D[Configure<EventBusOptions>]
   A --> E[AddSingleton<RabbitMQTelemetry>]
   A --> F[AddSingleton<IEventBus, RabbitMQEventBus>]
   A --> G[AddSingleton<IHostedService>]
   click A "#addrabbitmqeventbus" "Go to AddRabbitMqEventBus documentation section"
   click B "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/EventBusRabbitMQ/RabbitMqDependencyInjectionExtensions.cs#L15-L20" "View AddRabbitMQClient implementation"
   click C "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/EventBusRabbitMQ/RabbitMqDependencyInjectionExtensions.cs#L22-L27" "View AddOpenTelemetry implementation"
   click D "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/EventBusRabbitMQ/RabbitMqDependencyInjectionExtensions.cs#L29-L30" "View Configure<EventBusOptions> implementation"
   click E "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/EventBusRabbitMQ/RabbitMqDependencyInjectionExtensions.cs#L32" "View AddSingleton<RabbitMQTelemetry> implementation"
   click F "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/EventBusRabbitMQ/RabbitMqDependencyInjectionExtensions.cs#L33" "View AddSingleton<IEventBus, RabbitMQEventBus> implementation"
   click G "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/EventBusRabbitMQ/RabbitMqDependencyInjectionExtensions.cs#L35" "View AddSingleton<IHostedService> implementation"
 ```
 
 **Flow Diagram:**
 ```mermaid
 flowchart TD
   S[Start] --> N1[Check builder not null]
   N1 --> N2[AddRabbitMQClient]
   N2 --> N3[AddOpenTelemetry]
   N3 --> N4[Configure<EventBusOptions>]
   N4 --> N5[AddSingleton<RabbitMQTelemetry>]
   N5 --> N6[AddSingleton<IEventBus, RabbitMQEventBus>]
   N6 --> N7[AddSingleton<IHostedService>]
   N7 --> E[Return EventBusBuilder]
   click N1 "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/EventBusRabbitMQ/RabbitMqDependencyInjectionExtensions.cs#L16" "Check builder not null"
   click N2 "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/EventBusRabbitMQ/RabbitMqDependencyInjectionExtensions.cs#L18-L21" "AddRabbitMQClient"
   click N3 "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/EventBusRabbitMQ/RabbitMqDependencyInjectionExtensions.cs#L23-L28" "AddOpenTelemetry"
   click N4 "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/EventBusRabbitMQ/RabbitMqDependencyInjectionExtensions.cs#L30" "Configure<EventBusOptions>"
   click N5 "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/EventBusRabbitMQ/RabbitMqDependencyInjectionExtensions.cs#L32" "AddSingleton<RabbitMQTelemetry>"
   click N6 "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/EventBusRabbitMQ/RabbitMqDependencyInjectionExtensions.cs#L33" "AddSingleton<IEventBus, RabbitMQEventBus>"
   click N7 "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/EventBusRabbitMQ/RabbitMqDependencyInjectionExtensions.cs#L35" "AddSingleton<IHostedService>"
   click E "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/EventBusRabbitMQ/RabbitMqDependencyInjectionExtensions.cs#L37" "Return EventBusBuilder"
 ```
 
 **Flow Explanation:**
 
 1. Checks if the builder is null and throws if so ([L16](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/EventBusRabbitMQ/RabbitMqDependencyInjectionExtensions.cs#L16)).
 2. Registers the RabbitMQ client ([L18-L21](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/EventBusRabbitMQ/RabbitMqDependencyInjectionExtensions.cs#L18-L21)).
 3. Adds OpenTelemetry tracing ([L23-L28](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/EventBusRabbitMQ/RabbitMqDependencyInjectionExtensions.cs#L23-L28)).
 4. Configures event bus options ([L30](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/EventBusRabbitMQ/RabbitMqDependencyInjectionExtensions.cs#L30)).
 5. Registers telemetry and event bus services ([L32-L35](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/EventBusRabbitMQ/RabbitMqDependencyInjectionExtensions.cs#L32-L35)).
 6. Returns the `EventBusBuilder` ([L37](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/EventBusRabbitMQ/RabbitMqDependencyInjectionExtensions.cs#L37)).

- **Exceptions:** Throws `ArgumentNullException` if the builder is null.

---
## RabbitMQTelemetry ([source](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/EventBusRabbitMQ/RabbitMQTelemetry.cs#L6-L13))

### Overview
`RabbitMQTelemetry` provides OpenTelemetry integration for RabbitMQ operations. It exposes an activity source and propagator for distributed tracing, enabling observability of event bus activities.

#### Properties
- **ActivitySource**: Used to create tracing activities for RabbitMQ operations.
- **Propagator**: Used to propagate context for distributed tracing.

---