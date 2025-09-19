# Migrations

This section documents the migration classes and model snapshot in the Ordering.Infrastructure library. These classes represent schema evolution and database changes over time.

---

## [20230925222426_Initial.cs](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Infrastructure/Migrations/20230925222426_Initial.cs#L1)

**Overview:**
Defines the initial schema for the ordering database, including tables, sequences, and relationships for buyers, orders, payment methods, and order items.

**Methods:**
### [Up(MigrationBuilder migrationBuilder)](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Infrastructure/Migrations/20230925222426_Initial.cs#L8)
- **Overview:** Creates all initial tables, sequences, and relationships.
- **Flow Diagram:**
    ```mermaid
    flowchart LR
      A[Start] --> B[Ensure Schema]
      B --> C[Create Sequences]
      C --> D[Create Tables]
      D --> E[End]
      click B "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Infrastructure/Migrations/20230925222426_Initial.cs#L10" "Ensure Schema"
      click C "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Infrastructure/Migrations/20230925222426_Initial.cs#L13" "Create Sequences"
      click D "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Infrastructure/Migrations/20230925222426_Initial.cs#L22" "Create Tables"
    ```
- **Exceptions:** Throws if schema creation fails or database is unreachable.

### [Down(MigrationBuilder migrationBuilder)](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Infrastructure/Migrations/20230925222426_Initial.cs#L270)
- **Overview:** Drops all tables and sequences created in the Up method.
- **Exceptions:** Throws if drop operations fail.

---

## [OrderingContextModelSnapshot.cs](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Infrastructure/Migrations/OrderingContextModelSnapshot.cs#L1)

**Overview:**
Represents the current state of the ordering database model. Used by EF Core to compare and generate future migrations.

**Methods:**
### [BuildModel(ModelBuilder modelBuilder)](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Infrastructure/Migrations/OrderingContextModelSnapshot.cs#L18)
- **Overview:** Configures the model snapshot for all entities, sequences, and relationships.
- **Exceptions:** Throws if model building fails.

---

## [20231021004633_FixOrderitemseqSchema.cs](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Infrastructure/Migrations/20231021004633_FixOrderitemseqSchema.cs#L1)

**Overview:**
Updates the schema for the order item sequence and alters columns in orderstatus and cardtypes tables.

**Methods:**
### [Up(MigrationBuilder migrationBuilder)](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Infrastructure/Migrations/20231021004633_FixOrderitemseqSchema.cs#L8)
- **Overview:** Renames sequence and alters columns.
- **Flow Diagram:**
    ```mermaid
    flowchart LR
      A[Start] --> B[Rename Sequence]
      B --> C[Alter Columns]
      C --> D[End]
      click B "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Infrastructure/Migrations/20231021004633_FixOrderitemseqSchema.cs#L10" "Rename Sequence"
      click C "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Infrastructure/Migrations/20231021004633_FixOrderitemseqSchema.cs#L13" "Alter Columns"
    ```
- **Exceptions:** Throws if schema update fails.

### [Down(MigrationBuilder migrationBuilder)](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Infrastructure/Migrations/20231021004633_FixOrderitemseqSchema.cs#L36)
- **Overview:** Reverts changes made in Up method.
- **Exceptions:** Throws if revert operations fail.

---

## [20231026091055_Outbox.cs](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Infrastructure/Migrations/20231026091055_Outbox.cs#L1)

**Overview:**
Adds the IntegrationEventLog table for outbox pattern support in the ordering database.

**Methods:**
### [Up(MigrationBuilder migrationBuilder)](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Infrastructure/Migrations/20231026091055_Outbox.cs#L8)
- **Overview:** Creates the IntegrationEventLog table.
- **Flow Diagram:**
    ```mermaid
    flowchart LR
      A[Start] --> B[Create Table]
      B --> C[End]
      click B "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Infrastructure/Migrations/20231026091055_Outbox.cs#L10" "Create Table"
    ```
- **Exceptions:** Throws if table creation fails.

### [Down(MigrationBuilder migrationBuilder)](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Infrastructure/Migrations/20231026091055_Outbox.cs#L35)
- **Overview:** Drops the IntegrationEventLog table.
- **Exceptions:** Throws if drop operation fails.

---

## [20240106121712_UseEnumForOrderStatus.cs](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Infrastructure/Migrations/20240106121712_UseEnumForOrderStatus.cs#L1)

**Overview:**
Refactors the order status representation to use an enum and updates the orders table accordingly.

**Methods:**
### [Up(MigrationBuilder migrationBuilder)](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Infrastructure/Migrations/20240106121712_UseEnumForOrderStatus.cs#L8)
- **Overview:** Adds OrderStatus column, migrates data, and drops old table.
- **Flow Diagram:**
    ```mermaid
    flowchart LR
      A[Start] --> B[Add Column]
      B --> C[Migrate Data]
      C --> D[Drop Table]
      D --> E[Drop Foreign Key]
      E --> F[Drop Index]
      F --> G[End]
      click B "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Infrastructure/Migrations/20240106121712_UseEnumForOrderStatus.cs#L10" "Add Column"
      click C "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Infrastructure/Migrations/20240106121712_UseEnumForOrderStatus.cs#L17" "Migrate Data"
      click D "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Infrastructure/Migrations/20240106121712_UseEnumForOrderStatus.cs#L25" "Drop Table"
      click E "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Infrastructure/Migrations/20240106121712_UseEnumForOrderStatus.cs#L32" "Drop Foreign Key"
      click F "https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Infrastructure/Migrations/20240106121712_UseEnumForOrderStatus.cs#L39" "Drop Index"
    ```
- **Exceptions:** Throws if migration or data update fails.

### [Down(MigrationBuilder migrationBuilder)](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Ordering.Infrastructure/Migrations/20240106121712_UseEnumForOrderStatus.cs#L90)
- **Overview:** Reverts changes made in Up method.
- **Exceptions:** Throws if revert operations fail.
