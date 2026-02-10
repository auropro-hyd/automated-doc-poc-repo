# EventBus Library Overview

The EventBus library provides a robust infrastructure for event-driven communication between microservices and application components. It enables reliable publishing, handling, and subscription of integration events, supporting extensibility and custom serialization. The library is designed for use in distributed systems, making it easy to decouple services and implement asynchronous workflows.

Key capabilities include:
- Interfaces for Publishing and subscribing to integration events.
- Customizable event serialization and handler registration.
- Utilities for type resolution and diagnostics.

## Project Organization

The EventBus project is organized into several key areas:

```
EventBus/
  Extensions/ #Contains extension methods for configuring and extending the event bus.
  Events/ #Defines integration event contracts.
  Abstractions/ #Contains core interfaces and types for event bus operations.

```

## Documentation Structure

The documentation is divided into the following areas:

- [Utilities](./Utilities.md): Extension methods and helpers for type resolution and diagnostics.
- [Messaging](./Messaging.md): Core messaging types, event contracts, handler interfaces, and configuration extensions.

Refer to each section for detailed documentation.
