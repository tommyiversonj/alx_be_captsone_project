# API Documentation

## Authentication

- **Token Auth:**  
  Add header: `Authorization: Token <token>`
- **JWT Auth:**  
  Add header: `Authorization: Bearer <jwt>`

---

## Endpoints

### Products

- **GET /api/inventory/products/**  
  List all products.

- **POST /api/inventory/products/**  
  Create a new product.  
  **Body:**  
  ```json
  {
    "name": "Product Name",
    "category": 1,
    "price": 10.99,
    "quantity": 100
  }
  ```

- **GET /api/inventory/products/{id}/**  
  Retrieve a product.

- **PUT /api/inventory/products/{id}/**  
  Update a product.

- **DELETE /api/inventory/products/{id}/**  
  Delete a product.

---

### Categories

- **GET /api/inventory/categories/**  
  List all categories.

- **POST /api/inventory/categories/**  
  Create a new category.  
  **Body:**  
  ```json
  {
    "name": "Category Name"
  }
  ```

- **GET /api/inventory/categories/{id}/**  
  Retrieve a category.

---

### Suppliers

- **GET /api/inventory/suppliers/**  
  List all suppliers.

- **POST /api/inventory/suppliers/**  
  Create a new supplier.  
  **Body:**  
  ```json
  {
    "name": "Supplier Name",
    "contact": "Contact Info"
  }
  ```

- **GET /api/inventory/suppliers/{id}/**  
  Retrieve a supplier.

- **PUT /api/inventory/suppliers/{id}/**  
  Update a supplier.

- **DELETE /api/inventory/suppliers/{id}/**  
  Delete a supplier.

---

### Purchases

- **GET /api/purchases/**  
  List all purchases.

- **POST /api/purchases/**  
  Create a new purchase.  
  **Body:**  
  ```json
  {
    "product": 1,
    "supplier": 2,
    "quantity": 50,
    "purchase_date": "2025-09-05"
  }
  ```

- **GET /api/purchases/{id}/**  
  Retrieve a purchase.

---

### Sales

- **GET /api/sales/**  
  List all sales.

- **POST /api/sales/**  
  Create a new sale.  
  **Body:**  
  ```json
  {
    "product": 1,
    "customer": 3,
    "quantity": 5,
    "sale_date": "2025-09-05"
  }
  ```

- **GET /api/sales/{id}/**  
  Retrieve a sale.

---

### Stock Movements

- **GET /api/stock/stock-movements/**  
  List all stock movements (read-only).

---

### User Registration & Authentication

- **POST /api/register/**  
  Register a new user.  
  **Body:**  
  ```json
  {
    "username": "user",
    "password": "password",
    "email": "user@example.com"
  }
  ```

- **POST /api/login/**  
  Obtain authentication token.  
  **Body:**  
  ```json
  {
    "username": "user",
    "password": "password"
  }
  ```

---

## Error Responses

- **400 Bad Request:** Invalid input.
- **401 Unauthorized:** Authentication required.
- **403 Forbidden:** Permission denied.
- **404 Not Found:** Resource does not exist.

**Example error response:**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

---

## Swagger/OpenAPI

- Visit `/api/schema/swagger-ui/` for interactive API documentation.

---