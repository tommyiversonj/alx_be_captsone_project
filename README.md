# alx_be_captsone_project
# Inventory & Sales Management System

## Project Overview
This project provides a comprehensive Inventory and Sales Management System designed for small to medium-sized businesses. It helps track products, manage stock levels, and monitor sales in real time, all through a secure, RESTful API.

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

### Development & Setup Instructions

To get the project up and running on your local machine, follow these steps:

1.  **Clone the Repository**
    ```bash
    git clone [https://github.com/tommyiversonj/alx_be_captsone_project.git](https://github.com/tommyiversonj/alx_be_captsone_project.git)
    cd alx_be_captsone_project
    ```
2.  **Create a Virtual Environment & Install Dependencies**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```
3.  **Configure Environment Variables**
    Create a file named `.env` in the root of the project with the following content. **Remember to replace the values with your actual database credentials.**

    ```ini
    SECRET_KEY=your-secret-key
    DEBUG=True

    DB_NAME=your-database-name
    DB_USER=your-database-user
    DB_PASSWORD=your-database-password
    DB_HOST=localhost
    DB_PORT=5432
    ```
4.  **Set Up the Database**
    Make sure your PostgreSQL server is running. Create a new database with the name you specified in the `.env` file. Then, apply migrations to set up the database schema.
    ```bash
    python3 manage.py migrate
    ```
5.  **Create a Superuser**
    This will allow you to access the Django admin and test all features.
    ```bash
    python3 manage.py createsuperuser
    ```
6.  **Start the Server**
    ```bash
    python3 manage.py runserver
    ```

    ### API Usage

To interact with the API, you must first authenticate to obtain an access token. All protected endpoints require this token to be included in the `Authorization` header.

**1. Log in to get a token:**

```bash
curl -X POST [http://127.0.0.1:8000/api/users/login/](http://127.0.0.1:8000/api/users/login/) \
-H "Content-Type: application/json" \
-d '{"username": "your-username", "password": "your-password"}'

## Testing & Linting
- Lint code with `flake8` or format with `black`
- Run tests: `python manage.py test`

## Real-World Adaptation 🌟
- Can integrate with accounting software or e-commerce platforms.
- Real-time stock movement logging and low-stock alerts.
- Role-based access ensures secure operations.
- Include Postman collection for testing endpoints.
