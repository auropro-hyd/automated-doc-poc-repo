# EventBusRabbitMQ Overview

EventBusRabbitMQ provides a robust event bus implementation using RabbitMQ for distributed messaging in .NET applications. It enables reliable event publishing, subscription management, and integrates with OpenTelemetry for observability. The library is designed for extensibility and seamless integration into modern microservice architectures, supporting configuration, dependency injection, and tracing out of the box.



## File Dependency Diagram

```mermaid
flowchart TD
    EventBusOptions["EventBusOptions\n(Configuration)"]
    RabbitMQTelemetry["RabbitMQTelemetry\n(Logging/Observability)"]
    RabbitMQEventBus["RabbitMQEventBus\n(Messaging)"]
    RabbitMqDependencyInjectionExtensions["RabbitMqDependencyInjectionExtensions\n(Configuration)"]

    EventBusOptions -->|used by| RabbitMQEventBus
    RabbitMQTelemetry -->|used by| RabbitMQEventBus
    RabbitMqDependencyInjectionExtensions -->|registers| RabbitMQEventBus
    RabbitMqDependencyInjectionExtensions -->|registers| RabbitMQTelemetry
  click EventBusOptions "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/EventBusRabbitMQ/EventBusOptions.cs#L3-L7" "EventBusOptions source code"
  click RabbitMQTelemetry "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/EventBusRabbitMQ/RabbitMQTelemetry.cs#L6-L13" "RabbitMQTelemetry source code"
  click RabbitMQEventBus "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/EventBusRabbitMQ/RabbitMQEventBus.cs#L13-L319" "RabbitMQEventBus source code"
  click RabbitMqDependencyInjectionExtensions "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/EventBusRabbitMQ/RabbitMqDependencyInjectionExtensions.cs#L6-L50" "RabbitMqDependencyInjectionExtensions source code"
```

## Documentation Contents

- [Configuration](./Configuration.md)
- [Messaging](./Messaging.md)
