# alx_be_captsone_project
# Inventory & Sales Management System

## Project Overview
This project is a robust Inventory & Sales Management System built with Django and Django REST Framework (DRF). It manages products, categories, suppliers, purchases, sales, stock movements, and users with role-based access.

## Project Structure
```
inventory/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
users/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
stock/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
purchases/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
sales/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
```

## Core Components

### Inventory App
- **Models:**
  - `Category`: Groups products; `on_delete=models.PROTECT` prevents orphaned products.
  - `Product`: Tracks name, price, quantity, low_stock_threshold; includes `CheckConstraint` and `UniqueConstraint`.
- **Serializers:**
  - `CategorySerializer`, `ProductSerializer` with read/write flexibility and validation.
- **Views & Permissions:**
  - `CategoryViewSet`, `ProductViewSet` support CRUD, filtering, search, ordering.
  - `IsAdminOrReadOnly` enforces role-based permissions; product deletion restricted to superusers.

### Users App
- Custom User model extending `AbstractUser`.
- **Authentication Endpoints:**
  - `Register (/api/users/register/)`
  - `Login (/api/users/login/)`
  - `Logout (/api/users/logout/)`
- **User Management:**
  - Admin-only `UserViewSet` for full CRUD and role assignments.
- **Serializers:** `UserRegistrationSerializer`, `AuthTokenSerializer`, `UserSerializer`.

### Stock App
- Read-only log tracking all inventory changes.
- **StockMovement Model:** Links product to purchase/sale.
- **Serializer & ViewSet:** Read-only API with filtering and ordering.

### Purchases App
- **Models:** `Purchase`, `PurchaseItem`.
- **Serializer:** `PurchaseCreateSerializer` for nested creation, stock updates, and StockMovement logging in atomic transactions.
- **ViewSet:** Uses distinct serializers for GET and POST.

### Sales App
- **Models:** `Sale`, `SaleItem`.
- **Serializer:** `SaleCreateSerializer` validates stock, decrements inventory, logs 'OUT' StockMovement.
- **ViewSet:** Separate serializers for GET and POST.

## Features & API Functionality ⚙️
- RESTful endpoints with ModelViewSets.
- Proper HTTP status codes (200, 201, 400, 401, 403, 500).
- Filtering, search, and ordering supported.

## Error Handling & Logging ⚠️
- Custom error responses (stock validation, permissions).
- Handles DRF exceptions (`ValidationError`, `PermissionDenied`, `ObjectDoesNotExist`).
- Logging/monitoring (recommended: Django logging module or Sentry).

## Database Design & Performance 🗄️
- Proper relational structure with `ForeignKey` usage.
- `CheckConstraint` prevents negative stock.
- `UniqueConstraint` and indexes improve performance.
- Calculated fields like `total_amount` use `@property`.

## Authentication Endpoints
- `POST /api/register/` - Create user account.
- `POST /api/login/` - Authenticate and obtain token.

## Inventory & Supplier Endpoints
- `/api/inventory/products/` GET/POST
- `/api/inventory/products/{id}/` GET/PUT/DELETE
- `/api/inventory/categories/` GET/POST
- `/api/inventory/categories/{id}/` GET
- `/api/inventory/suppliers/` GET/POST
- `/api/inventory/suppliers/{id}/` GET/PUT/DELETE

## Purchases & Sales Endpoints
- `/api/purchases/` GET/POST
- `/api/purchases/{id}/` GET
- `/api/sales/` GET/POST
- `/api/sales/{id}/` GET

## Stock Movement & Analytics Endpoints
- `/api/stock/stock-movements/` GET (read-only)
- `/api/dashboard/low-stock/` GET (planned)
- `/api/dashboard/total-sales/` GET (planned)
- `/api/dashboard/top-products/` GET (planned)

## Development & Setup Instructions
1. Clone repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run migrations: `python manage.py migrate`
4. Create superuser: `python manage.py createsuperuser`
5. Start server: `python manage.py runserver`

## Testing & Linting
- Lint code with `flake8` or format with `black`
- Run tests: `python manage.py test`

## Real-World Adaptation 🌟
- Can integrate with accounting software or e-commerce platforms.
- Real-time stock movement logging and low-stock alerts.
- Role-based access ensures secure operations.
- Include Postman collection for testing endpoints.
