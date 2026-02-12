# eShop Microservices Documentation

Welcome to the comprehensive documentation for the eShop microservices platform. This documentation provides detailed information about each microservice, their interactions, and the overall system architecture.

## System Overview

eShop is a modern e-commerce platform built using a microservices architecture. The system is designed to be scalable, maintainable, and resilient, implementing best practices in distributed systems design.

### Key Features

- Microservices-based architecture
- Event-driven communication
- Domain-Driven Design (DDD) implementation
- CQRS pattern usage
- OAuth2/JWT authentication
- Containerized deployment
- Monitoring and observability

## Core Microservices

### 1. Catalog API
The Catalog service manages the product catalog and inventory. It provides functionality for:
- Product management
- Category management
- Price management
- Inventory tracking
- Product search with AI capabilities

[View Catalog API Documentation](catalog-api.md)

### 2. Basket API
The Basket service handles shopping cart operations including:
- Cart creation and management
- Item addition and removal
- Price calculation
- Cart checkout process

[View Basket API Documentation](basket-api.md)

### 3. Ordering API
The Ordering service manages the complete order lifecycle:
- Order creation and processing
- Payment processing
- Order status management
- Order history tracking
- Shipping coordination

[View Ordering API Documentation](ordering-api.md)

### 4. Identity API
The Identity service handles:
- User authentication
- Authorization
- User profile management
- Security token management

[View Identity API Documentation](identity-api.md)

## Supporting Services

### Event Bus (RabbitMQ)
Handles asynchronous communication between services through:
- Event publishing
- Event subscription
- Message persistence
- Dead letter queues

### API Gateway
Provides:
- Request routing
- API composition
- Authentication
- Rate limiting

## Client Applications

### Web Application
- React-based SPA
- Responsive design
- Progressive Web App capabilities

### Mobile Application
- .NET MAUI implementation
- Cross-platform support
- Offline capabilities

## Technical Stack

### Backend
- .NET 8.0
- ASP.NET Core
- Entity Framework Core
- SQL Server
- Redis
- RabbitMQ
- gRPC

### Frontend
- React
- .NET MAUI
- TypeScript
- Material-UI

### Infrastructure
- Docker
- Kubernetes
- Azure Cloud Services
- Application Insights

## Getting Started

To start working with the eShop system:

1. Clone the repository
2. Install prerequisites:
   - .NET 8.0 SDK
   - Docker Desktop
   - Node.js
3. Run the development environment:
   ```powershell
   docker-compose up -d
   dotnet run --project src/eShop.AppHost
   ```

## Contributing

Please read our [Contributing Guidelines](contributing.md) for details on:
- Code standards
- Documentation requirements
- Pull request process
- Development workflow

## Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the FAQ section

## License

This project is licensed under the MIT License - see the [LICENSE](license.md) file for details.
