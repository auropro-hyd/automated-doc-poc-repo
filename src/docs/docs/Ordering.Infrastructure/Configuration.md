# Configuration

This section documents all configuration-related classes in the Ordering.Infrastructure library. These classes define how domain entities are mapped to the database using Entity Framework Core.

---

## GlobalUsings.cs


**Overview:**
Provides project-wide using directives for the infrastructure layer, ensuring consistent access to common namespaces and types. This file is foundational and does not contain runtime logic or methods.

[View implementation](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Infrastructure/GlobalUsings.cs#L1)

---

## BuyerEntityTypeConfiguration.cs


**Overview:**
Configures the EF Core mapping for the [`Buyer`](../Ordering.Domain/Aggregate.md#buyer-aggregate) entity, specifying table schema, relationships, and constraints. Ensures correct persistence and retrieval of buyer data.

**Methods:**

### [`Configure(EntityTypeBuilder<Buyer> buyerConfiguration)`](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Infrastructure/EntityConfigurations/BuyerEntityTypeConfiguration.cs#L6)
- **Overview:** Sets up the entity mapping for [`Buyer`](../Ordering.Domain/Aggregate.md#buyer-aggregate), including keys, relationships, and property constraints.
- **Flow Diagram:**
	```mermaid
	flowchart LR
		A[Start] --> B[Set Table Name]
		B --> C[Ignore DomainEvents]
		C --> D[Configure Id]
		D --> E[Configure IdentityGuid]
		E --> F[Set Unique Index]
		F --> G[Configure PaymentMethods]
		G --> H[End]
		click A "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Infrastructure/EntityConfigurations/BuyerEntityTypeConfiguration.cs#L6" "Method Start"
		click B "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Infrastructure/EntityConfigurations/BuyerEntityTypeConfiguration.cs#L8" "Set Table Name"
		click C "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Infrastructure/EntityConfigurations/BuyerEntityTypeConfiguration.cs#L10" "Ignore DomainEvents"
		click D "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Infrastructure/EntityConfigurations/BuyerEntityTypeConfiguration.cs#L12" "Configure Id"
		click E "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Infrastructure/EntityConfigurations/BuyerEntityTypeConfiguration.cs#L14" "Configure IdentityGuid"
		click F "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Infrastructure/EntityConfigurations/BuyerEntityTypeConfiguration.cs#L16" "Set Unique Index"
		click G "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Infrastructure/EntityConfigurations/BuyerEntityTypeConfiguration.cs#L18" "Configure PaymentMethods"
		click H "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Infrastructure/EntityConfigurations/BuyerEntityTypeConfiguration.cs#L20" "Method End"
	```
	*The method configures table name, ignores domain events, sets up keys and relationships, and ensures uniqueness for identity.*
- **Exceptions:**
	- Throws if configuration is invalid or if required properties are missing during model building.

---

## OrderEntityTypeConfiguration.cs


**Overview:**
Configures the EF Core mapping for the [`Order`](../Ordering.Domain/Aggregate.md#order-aggregate) entity, defining table structure, relationships, and property rules.

**Methods:**

### [`Configure(EntityTypeBuilder<Order> orderConfiguration)`](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Infrastructure/EntityConfigurations/OrderEntityTypeConfiguration.cs#L5)
- **Overview:** Sets up the entity mapping for [`Order`](../Ordering.Domain/Aggregate.md#order-aggregate), including keys, navigation properties, and constraints.
- **Flow Diagram:**
	```mermaid
	flowchart LR
		A[Start] --> B[Set Table Name]
		B --> C[Ignore DomainEvents]
		C --> D[Configure Id]
		D --> E[Configure Address]
		E --> F[Configure OrderStatus]
		F --> G[Configure PaymentId]
		G --> H[Set PaymentMethod Relationship]
		H --> I[Set Buyer Relationship]
		I --> J[End]
		click A "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Infrastructure/EntityConfigurations/OrderEntityTypeConfiguration.cs#L5" "Method Start"
		click B "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Infrastructure/EntityConfigurations/OrderEntityTypeConfiguration.cs#L7" "Set Table Name"
		click C "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Infrastructure/EntityConfigurations/OrderEntityTypeConfiguration.cs#L9" "Ignore DomainEvents"
		click D "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Infrastructure/EntityConfigurations/OrderEntityTypeConfiguration.cs#L11" "Configure Id"
		click E "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Infrastructure/EntityConfigurations/OrderEntityTypeConfiguration.cs#L13" "Configure Address"
		click F "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Infrastructure/EntityConfigurations/OrderEntityTypeConfiguration.cs#L16" "Configure OrderStatus"
		click G "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Infrastructure/EntityConfigurations/OrderEntityTypeConfiguration.cs#L19" "Configure PaymentId"
		click H "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Infrastructure/EntityConfigurations/OrderEntityTypeConfiguration.cs#L21" "Set PaymentMethod Relationship"
		click I "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Infrastructure/EntityConfigurations/OrderEntityTypeConfiguration.cs#L24" "Set Buyer Relationship"
		click J "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Infrastructure/EntityConfigurations/OrderEntityTypeConfiguration.cs#L27" "Method End"
	```
	*The method configures table name, keys, value objects, and relationships for the Order entity.*
- **Exceptions:**
	- Throws if configuration is invalid or if required properties are missing during model building.

---

## CardTypeEntityTypeConfiguration.cs


**Overview:**
Configures the EF Core mapping for the [`CardType`](../Ordering.Domain/ValueObject.md#cardtype) entity, specifying schema and constraints for card type data.

**Methods:**

### [`Configure(EntityTypeBuilder<CardType> cardTypesConfiguration)`](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Infrastructure/EntityConfigurations/CardTypeEntityTypeConfiguration.cs#L6)
- **Overview:** Sets up the entity mapping for [`CardType`](../Ordering.Domain/ValueObject.md#cardtype).
- **Flow Diagram:**
	```mermaid
	flowchart LR
		A[Start] --> B[Set Table Name]
		B --> C[Configure Id]
		C --> D[Configure Name]
		D --> E[End]
		click A "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Infrastructure/EntityConfigurations/CardTypeEntityTypeConfiguration.cs#L6" "Method Start"
		click B "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Infrastructure/EntityConfigurations/CardTypeEntityTypeConfiguration.cs#L8" "Set Table Name"
		click C "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Infrastructure/EntityConfigurations/CardTypeEntityTypeConfiguration.cs#L10" "Configure Id"
		click D "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Infrastructure/EntityConfigurations/CardTypeEntityTypeConfiguration.cs#L12" "Configure Name"
		click E "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Infrastructure/EntityConfigurations/CardTypeEntityTypeConfiguration.cs#L14" "Method End"
	```
	*The method configures table name, sets up keys, and enforces constraints for card type names.*
- **Exceptions:**
	- Throws if configuration is invalid or if required properties are missing during model building.

---

## PaymentMethodEntityTypeConfiguration.cs


**Overview:**
Configures the EF Core mapping for the [`PaymentMethod`](../Ordering.Domain/ValueObject.md#paymentmethod) entity, ensuring correct schema and relationships for payment data.

**Methods:**

### [`Configure(EntityTypeBuilder<PaymentMethod> paymentConfiguration)`](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Infrastructure/EntityConfigurations/PaymentMethodEntityTypeConfiguration.cs#L6)
- **Overview:** Sets up the entity mapping for [`PaymentMethod`](../Ordering.Domain/ValueObject.md#paymentmethod), including table name, keys, and property constraints.
- **Flow Diagram:**
	```mermaid
	flowchart LR
		A[Start] --> B[Set Table Name]
		B --> C[Ignore DomainEvents]
		C --> D[Configure Id]
		D --> E[Configure BuyerId]
		E --> F[Configure CardHolderName]
		F --> G[Configure Alias]
		G --> H[Configure CardNumber]
		H --> I[Configure Expiration]
		I --> J[Configure CardTypeId]
		J --> K[End]
		click A "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Infrastructure/EntityConfigurations/PaymentMethodEntityTypeConfiguration.cs#L6" "Method Start"
		click B "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Infrastructure/EntityConfigurations/PaymentMethodEntityTypeConfiguration.cs#L8" "Set Table Name"
		click C "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Infrastructure/EntityConfigurations/PaymentMethodEntityTypeConfiguration.cs#L10" "Ignore DomainEvents"
		click D "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Infrastructure/EntityConfigurations/PaymentMethodEntityTypeConfiguration.cs#L12" "Configure Id"
		click E "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Infrastructure/EntityConfigurations/PaymentMethodEntityTypeConfiguration.cs#L14" "Configure BuyerId"
		click F "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Infrastructure/EntityConfigurations/PaymentMethodEntityTypeConfiguration.cs#L16" "Configure CardHolderName"
		click G "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Infrastructure/EntityConfigurations/PaymentMethodEntityTypeConfiguration.cs#L18" "Configure Alias"
		click H "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Infrastructure/EntityConfigurations/PaymentMethodEntityTypeConfiguration.cs#L20" "Configure CardNumber"
		click I "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Infrastructure/EntityConfigurations/PaymentMethodEntityTypeConfiguration.cs#L22" "Configure Expiration"
		click J "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Infrastructure/EntityConfigurations/PaymentMethodEntityTypeConfiguration.cs#L24" "Configure CardTypeId"
		click K "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Infrastructure/EntityConfigurations/PaymentMethodEntityTypeConfiguration.cs#L26" "Method End"
	```
	*The method configures table name, keys, and all relevant payment properties for persistence.*
- **Exceptions:**
	- Throws if configuration is invalid or if required properties are missing during model building.

---

## OrderItemEntityTypeConfiguration.cs

**Overview:**
Configures the EF Core mapping for the [`OrderItem`](../Ordering.Domain/ValueObject.md#orderitem) entity, specifying table schema and property rules.

**Methods:**

### Configure(EntityTypeBuilder<OrderItem> orderItemConfiguration)
- **Overview:** Sets up the entity mapping for [`OrderItem`](../Ordering.Domain/ValueObject.md#orderitem), including table name, keys, and foreign key.

- **Flow Diagram:**
	```mermaid
	flowchart LR
		A[Start] --> B[Set Table Name]
		B --> C[Ignore DomainEvents]
		C --> D[Configure Id]
		D --> E[Configure OrderId]
		E --> F[End]
	```
	*The method configures table name, keys, and sets up the foreign key for order items.*
- **Exceptions:**
	- Throws if configuration is invalid or if required properties are missing during model building.

---

## ClientRequestEntityTypeConfiguration.cs

**Overview:**
Configures the EF Core mapping for the [`ClientRequest`](./Data%20Interactions.md#clientrequestcs) entity, ensuring correct schema and constraints for client request tracking.

**Methods:**

### Configure(EntityTypeBuilder<ClientRequest> requestConfiguration)
- **Overview:** Sets up the entity mapping for [`ClientRequest`](./Data%20Interactions.md#clientrequestcs), including table name.
- **Call Graph:**
	```mermaid
	flowchart LR
		A[Configure] --> B[ToTable("requests")]
	```
- **Flow Diagram:**
	```mermaid
	flowchart LR
		A[Start] --> B[Set Table Name]
		B --> C[End]
	```
	*The method configures the table name for client requests.*
- **Exceptions:**
	- Throws if configuration is invalid or if required properties are missing during model building.
