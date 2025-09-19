### Project Summaries

**Project:** Basket.API, Basket.API/  
**Meta:** TargetFramework net9.0, Sdk Microsoft.NET.Sdk.Web, OutputType Web, Nullable not set, LangVersion not set, Version not set  
**Type:** gRPC service  
**Depends on:** eShop.ServiceDefaults, EventBusRabbitMQ  
**Depended by:** eShop.AppHost  
**Packages:** Aspire (Aspire.StackExchange.Redis), gRPC (Grpc.AspNetCore)  

**Project:** Catalog.API, Catalog.API/  
**Meta:** TargetFramework net9.0, Sdk Microsoft.NET.Sdk.Web, OutputType Web, Nullable not set, LangVersion not set, Version not set  
**Type:** REST API  
**Depends on:** EventBusRabbitMQ, IntegrationEventLogEF, eShop.ServiceDefaults  
**Depended by:** eShop.AppHost  
**Packages:** AspNetCore (Asp.Versioning.Http), EF Core (Aspire.Npgsql.EntityFrameworkCore.PostgreSQL, Microsoft.EntityFrameworkCore.Tools), Azure (Aspire.Azure.AI.OpenAI), Ollama (CommunityToolkit.Aspire.OllamaSharp), AI (Microsoft.Extensions.AI, Microsoft.Extensions.AI.OpenAI, Pgvector, Pgvector.EntityFrameworkCore)  

**Project:** ClientApp, ClientApp/  
**Meta:** TargetFrameworks net9.0-android;net9.0-ios;net9.0-maccatalyst;net9.0-windows10.0.19041.0, Sdk Microsoft.NET.Sdk, OutputType Exe, Nullable not set, LangVersion not set, Version not set  
**Type:** UI app  
**Depends on:** none  
**Depended by:** none  
**Packages:** gRPC (Google.Protobuf, Grpc.Net.Client, Grpc.Tools), MAUI (Microsoft.Maui.Controls, Microsoft.Maui.Controls.Compatibility, Microsoft.Maui.Controls.Maps, CommunityToolkit.Maui), Auth (IdentityModel.OidcClient, IdentityModel), MVVM (CommunityToolkit.Mvvm)  

**Project:** eShop.AppHost, eShop.AppHost/  
**Meta:** TargetFramework net9.0, Sdk Microsoft.NET.Sdk with Aspire.AppHost.Sdk, OutputType Exe, Nullable enable, LangVersion not set, Version not set  
**Type:** Tool  
**Depends on:** Mobile.Bff.Shopping, Basket.API, Catalog.API, Identity.API, Ordering.API, OrderProcessor, PaymentProcessor, Webhooks.API, WebApp, WebhookClient  
**Depended by:** none  
**Packages:** Aspire (Aspire.Hosting.AppHost, Aspire.Hosting.RabbitMQ, Aspire.Hosting.Redis, Aspire.Hosting.PostgreSQL, Aspire.Hosting.Azure.CognitiveServices, CommunityToolkit.Aspire.Hosting.Ollama)  

**Project:** eShop.ServiceDefaults, eShop.ServiceDefaults/  
**Meta:** TargetFramework net9.0, Sdk Microsoft.NET.Sdk, OutputType Library, Nullable enable, LangVersion not set, Version not set  
**Type:** Library  
**Depends on:** none  
**Depended by:** Basket.API, Catalog.API, Identity.API, Mobile.Bff.Shopping, Ordering.API, OrderProcessor, PaymentProcessor, WebApp, WebhookClient, Webhooks.API  
**Packages:** AspNetCore (Asp.Versioning.Mvc.ApiExplorer, Microsoft.AspNetCore.OpenApi, Scalar.AspNetCore, Microsoft.AspNetCore.Authentication.JwtBearer), Resilience (Microsoft.Extensions.Http.Resilience), ServiceDiscovery (Microsoft.Extensions.ServiceDiscovery), OpenTelemetry (OpenTelemetry.Exporter.OpenTelemetryProtocol, OpenTelemetry.Extensions.Hosting, OpenTelemetry.Instrumentation.AspNetCore, OpenTelemetry.Instrumentation.GrpcNetClient, OpenTelemetry.Instrumentation.Http, OpenTelemetry.Instrumentation.Runtime)  

**Project:** EventBus, EventBus/  
**Meta:** TargetFramework net9.0, Sdk Microsoft.NET.Sdk, OutputType Library, Nullable not set, LangVersion not set, Version not set  
**Type:** Library  
**Depends on:** none  
**Depended by:** EventBusRabbitMQ, IntegrationEventLogEF  
**Packages:** DI (Microsoft.Extensions.DependencyInjection.Abstractions, Microsoft.Extensions.Options)  

**Project:** EventBusRabbitMQ, EventBusRabbitMQ/  
**Meta:** TargetFramework net9.0, Sdk Microsoft.NET.Sdk, OutputType Library, Nullable not set, LangVersion not set, Version not set  
**Type:** Library  
**Depends on:** EventBus  
**Depended by:** Basket.API, Catalog.API, Ordering.API, OrderProcessor, PaymentProcessor, WebApp, Webhooks.API  
**Packages:** Aspire (Aspire.RabbitMQ.Client), Config (Microsoft.Extensions.Options.ConfigurationExtensions), Polly (Polly.Core)  

**Project:** HybridApp, HybridApp/  
**Meta:** TargetFrameworks net9.0-android;net9.0-ios;net9.0-maccatalyst;net9.0-windows10.0.19041.0, Sdk Microsoft.NET.Sdk.Razor, OutputType Exe, Nullable enable, LangVersion not set, Version not set  
**Type:** UI app  
**Depends on:** WebAppComponents  
**Depended by:** none  
**Packages:** MAUI (Microsoft.AspNetCore.Components.WebView.Maui, Microsoft.Maui.Controls, Microsoft.Maui.Controls.Compatibility), Http (Microsoft.Extensions.Http)  

**Project:** Identity.API, Identity.API/  
**Meta:** TargetFramework net9.0, Sdk Microsoft.NET.Sdk.Web, OutputType Web, Nullable not set, LangVersion not set, Version not set  
**Type:** REST API  
**Depends on:** eShop.ServiceDefaults  
**Depended by:** eShop.AppHost  
**Packages:** IdentityServer (Duende.IdentityServer.AspNetIdentity, Duende.IdentityServer.EntityFramework, Duende.IdentityServer.Storage, Duende.IdentityServer), AspNetCore Identity (Microsoft.AspNetCore.Identity.EntityFrameworkCore, Microsoft.AspNetCore.Identity.UI), EF Core (Microsoft.EntityFrameworkCore.Tools, Aspire.Npgsql.EntityFrameworkCore.PostgreSQL), AutoMapper (Automapper)  

**Project:** IntegrationEventLogEF, IntegrationEventLogEF/  
**Meta:** TargetFramework net9.0, Sdk Microsoft.NET.Sdk, OutputType Library, Nullable not set, LangVersion not set, Version not set  
**Type:** Library  
**Depends on:** EventBus  
**Depended by:** Catalog.API, Ordering.API, Webhooks.API  
**Packages:** EF Core (Npgsql.EntityFrameworkCore.PostgreSQL)  

**Project:** Mobile.Bff.Shopping, Mobile.Bff.Shopping/  
**Meta:** TargetFramework net9.0, Sdk Microsoft.NET.Sdk.Web, OutputType Web, Nullable not set, LangVersion not set, Version not set  
**Type:** REST API  
**Depends on:** eShop.ServiceDefaults  
**Depended by:** eShop.AppHost  
**Packages:** Yarp (Yarp.ReverseProxy, Microsoft.Extensions.ServiceDiscovery.Yarp), HealthChecks (AspNetCore.HealthChecks.Uris)  

**Project:** Ordering.API, Ordering.API/  
**Meta:** TargetFramework net9.0, Sdk Microsoft.NET.Sdk.Web, OutputType Web, Nullable not set, LangVersion not set, Version not set  
**Type:** REST API  
**Depends on:** EventBusRabbitMQ, IntegrationEventLogEF, eShop.ServiceDefaults, Ordering.Domain, Ordering.Infrastructure  
**Depended by:** eShop.AppHost  
**Packages:** AspNetCore (Asp.Versioning.Http), EF Core (Aspire.Npgsql.EntityFrameworkCore.PostgreSQL, Microsoft.EntityFrameworkCore.Tools), Validation (FluentValidation.AspNetCore)  

**Project:** Ordering.Domain, Ordering.Domain/  
**Meta:** TargetFramework net9.0, Sdk Microsoft.NET.Sdk, OutputType Library, Nullable not set, LangVersion not set, Version not set  
**Type:** Library  
**Depends on:** none  
**Depended by:** Ordering.API, Ordering.Infrastructure  
**Packages:** MediatR (MediatR), Reflection (System.Reflection.TypeExtensions)  

**Project:** Ordering.Infrastructure, Ordering.Infrastructure/  
**Meta:** TargetFramework net9.0, Sdk Microsoft.NET.Sdk, OutputType Library, Nullable not set, LangVersion not set, Version not set  
**Type:** Library  
**Depends on:** IntegrationEventLogEF, Ordering.Domain  
**Depended by:** Ordering.API  
**Packages:** EF Core (Npgsql.EntityFrameworkCore.PostgreSQL)  

**Project:** OrderProcessor, OrderProcessor/  
**Meta:** TargetFramework net9.0, Sdk Microsoft.NET.Sdk.Worker, OutputType Worker, Nullable not set, LangVersion not set, Version not set  
**Type:** Worker  
**Depends on:** eShop.ServiceDefaults, EventBusRabbitMQ  
**Depended by:** eShop.AppHost  
**Packages:** Aspire (Aspire.Npgsql)  

**Project:** PaymentProcessor, PaymentProcessor/  
**Meta:** TargetFramework net9.0, Sdk Microsoft.NET.Sdk.Web, OutputType Web, Nullable not set, LangVersion not set, Version not set  
**Type:** REST API  
**Depends on:** eShop.ServiceDefaults, EventBusRabbitMQ  
**Depended by:** eShop.AppHost  
**Packages:** none  

**Project:** WebApp, WebApp/  
**Meta:** TargetFramework net9.0, Sdk Microsoft.NET.Sdk.Web, OutputType Web, Nullable enable, LangVersion not set, Version not set  
**Type:** UI app  
**Depends on:** eShop.ServiceDefaults, EventBusRabbitMQ, WebAppComponents  
**Depended by:** eShop.AppHost  
**Packages:** AspNetCore (Asp.Versioning.Http.Client), Azure (Aspire.Azure.AI.OpenAI), Ollama (CommunityToolkit.Aspire.OllamaSharp), ServiceDiscovery (Microsoft.Extensions.ServiceDiscovery.Yarp), AI (Microsoft.Extensions.AI, Microsoft.Extensions.AI.OpenAI), Auth (Microsoft.AspNetCore.Authentication.OpenIdConnect), gRPC (Google.Protobuf, Grpc.Net.ClientFactory, Grpc.Tools)  

**Project:** WebAppComponents, WebAppComponents/  
**Meta:** TargetFramework net9.0, Sdk Microsoft.NET.Sdk.Razor, OutputType Library, Nullable enable, LangVersion not set, Version not set  
**Type:** Library  
**Depends on:** none  
**Depended by:** HybridApp, WebApp  
**Packages:** Blazor (Microsoft.AspNetCore.Components.Web)  

**Project:** WebhookClient, WebhookClient/  
**Meta:** TargetFramework net9.0, Sdk Microsoft.NET.Sdk.Web, OutputType Web, Nullable enable, LangVersion not set, Version not set  
**Type:** UI app  
**Depends on:** eShop.ServiceDefaults  
**Depended by:** eShop.AppHost  
**Packages:** AspNetCore (Asp.Versioning.Http.Client), Auth (Microsoft.AspNetCore.Authentication.OpenIdConnect), Blazor (Microsoft.AspNetCore.Components.QuickGrid)  

**Project:** Webhooks.API, Webhooks.API/  
**Meta:** TargetFramework net9.0, Sdk Microsoft.NET.Sdk.Web, OutputType Web, Nullable not set, LangVersion not set, Version not set  
**Type:** REST API  
**Depends on:** EventBusRabbitMQ, IntegrationEventLogEF, eShop.ServiceDefaults  
**Depended by:** eShop.AppHost  
**Packages:** AspNetCore (Asp.Versioning.Http), EF Core (Aspire.Npgsql.EntityFrameworkCore.PostgreSQL, Microsoft.EntityFrameworkCore.Tools)

