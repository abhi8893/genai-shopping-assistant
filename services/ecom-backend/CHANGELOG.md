# [UNRELEASED]


# v0.1.0 (TBD)

## 1st Release

An auxiliary FastAPI service that provides e-commerce operations (products, carts, users) required for developing and demonstrating the GenAI Shopping Assistant. This first release establishes the foundation for managing e-commerce backend operations with a clean 3-tier architecture and SQLite persistence.

## Features

- **Three-domain REST API**: Products, Carts, and Users APIs for e-commerce operations
- **SQLite persistence**: File-based database with Alembic migrations for schema management
- **3-tier architecture**: Clean separation between API, Service, and Repository layers
- **Product hierarchy**: Category and subcategory support with semantic slug-based lookups
- **Cart management**: Basic CRUD operations for cart management
- **User management**: Basic CRUD operations for user management
- **FastAPI framework**: REST API based on FastAPI

## NOTE

- This service is auxiliary to the main `shopping-assistant` service which requires ecom backend operations (products, carts, users) for `ProductSearch` and `ShoppingActions` agents
- The current user authentication and authorization is a makeshift implementation utilizing `X-User-Id` HTTP header (Will be replaced with proper authentication and authorization in future)
- Currently, the service does not bundle a client library, and it is externally maintained in `shopping-assistant` package as `packages/shopping-assistant/src/shopping_assistant/external/ecom_api_client`

