# Catalog.API Utilities

This document covers utility, DTO, and helper classes in the Catalog.API area. Each entry links to its definition and highlights non-trivial members.

---

## CatalogItem
[Definition](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Catalog.API/Model/CatalogItem.cs#L7)

Represents a product in the catalog, including name, description, price, stock, type, brand, and optional AI embedding. Used for CRUD operations and semantic search.

**Notable Members:**
- `public int Id { get; set; }` — Unique identifier for the item. [Definition](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Catalog.API/Model/CatalogItem.cs#L9)
- `public string Name { get; set; }` — Item name. [Definition](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Catalog.API/Model/CatalogItem.cs#L11)
- `public decimal Price { get; set; }` — Item price. [Definition](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Catalog.API/Model/CatalogItem.cs#L15)
- `public Vector Embedding { get; set; }` — AI embedding for semantic search. [Definition](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Catalog.API/Model/CatalogItem.cs#L37)

---

## PaginatedItems<TEntity>
[Definition](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Catalog.API/Model/PaginatedItems.cs#L6)

DTO for paginated results, including page index, size, total count, and data collection.

**Notable Members:**
- `public int PageIndex { get; }` — Current page index. [Definition](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Catalog.API/Model/PaginatedItems.cs#L7)
- `public int PageSize { get; }` — Page size. [Definition](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Catalog.API/Model/PaginatedItems.cs#L9)
- `public long Count { get; }` — Total item count. [Definition](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Catalog.API/Model/PaginatedItems.cs#L11)

---

## PaginationRequest
[Definition](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Catalog.API/Model/PaginationRequest.cs#L6)

DTO for pagination parameters, including page size and index.

**Notable Members:**
- `int PageSize` — Number of items per page. [Definition](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Catalog.API/Model/PaginationRequest.cs#L7)
- `int PageIndex` — Page index. [Definition](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Catalog.API/Model/PaginationRequest.cs#L11)

---

## CatalogBrand
[Definition](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Catalog.API/Model/CatalogBrand.cs#L6)

Represents a brand in the catalog.

**Notable Members:**
- `public int Id { get; set; }` — Brand identifier. [Definition](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Catalog.API/Model/CatalogBrand.cs#L7)
- `public string Brand { get; set; }` — Brand name. [Definition](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Catalog.API/Model/CatalogBrand.cs#L9)

---

## CatalogType
[Definition](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Catalog.API/Model/CatalogType.cs#L6)

Represents a type/category in the catalog.

**Notable Members:**
- `public int Id { get; set; }` — Type identifier. [Definition](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Catalog.API/Model/CatalogType.cs#L7)
- `public string Type { get; set; }` — Type name. [Definition](https://github.com/akhileshap9/automated-doc-poc-repo/blob/main/src/Catalog.API/Model/CatalogType.cs#L9)

---

