---
mode: 'agent'
description: 'Generate a class files classifations for a library file as part of developer documentation.'
---
Name of the Library: ${input:library-name: name of the library}
You are a coding agent tasked with generating developer documentation for a library-name project. Classify .cs files into Services, Mappers, Data Interactions, Configuration, Caching, Messaging, Serialization, Validation, Logging/Observability, or Adapters (External Integrations). For any type that does not fit these, dynamically create an appropriate group name (plural, human-readable, e.g., “Scheduling”, “Compression”, “CLI Tools”) and assign the file there; document the rule you applied for that new group in one sentence.
- Services: Orchestration or core logic (managers, handlers, background workers) registered in DI; removal breaks workflows.
- Mappers: Type conversions (DTO ↔ Domain ↔ Persistence). More than trivial mapping still maps here.
- Data Interactions: Persistence code (repositories, EF DbContext, UoW, event-log writers).
- Configuration: Options, settings binders, option validators, configuration loaders.
- Caching: Cache providers, decorators, policies.
- Messaging: Producers/consumers, bus clients, message contracts middleware (non-DDD).
- Serialization: JSON/XML/Binary serializers, converters, contract resolvers.
- Validation: Validators, rule sets (non-controller specific).
- Logging/Observability: Loggers, sinks, telemetry, metrics, tracing.
- Adapters (External Integrations): HTTP clients, SDK wrappers, filesystem/process adapters.
Ordering: Build a dependency graph and order topologically. Start with zero-dependency classes, then move upward. For ties, use this preference: Configuration → Serialization → Validation → Logging/Observability → Caching → Messaging → Data Interactions → Mappers → Adapters (External Integrations) → Services. When you create a dynamic group, place it in the order by its natural dependency role (foundations earlier, orchestrators later).
Output:
Create a file in `.github/scratchpad/<library-name>-classify.md`
create a mermaid dependency graph in TD with no dependent classes/interfaces on top and move downwards with increasind dependency order.
Add an ordered list for all the classes & their classification based on ordering criteria.
