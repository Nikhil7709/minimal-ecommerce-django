# API Documentation

This document describes the available API endpoints for the Minimal E-commerce Django Project.

---

## Authentication

### Register
- **POST** `/api/store/register/`
- **Description:** Register a new user.
- **Request Body:**
  ```json
  { "email": "user@example.com", "name": "User", "password": "password123" }
  ```
- **Response:** 201 Created

### Login
- **POST** `/api/store/login/`
- **Description:** Login and receive JWT tokens.
- **Request Body:**
  ```json
  { "email": "user@example.com", "password": "password123" }
  ```
- **Response:** 200 OK, returns access and refresh tokens

### Logout
- **GET** `/api/store/logout/`
- **Description:** Logout user (redirects to login UI)

---

## Products

### Create Product
- **POST** `/api/store/create/`
- **Permissions:** Authenticated
- **Request Body:** multipart/form-data (name, price, stock, etc.)
- **Response:** 201 Created

### List Products
- **GET** `/api/store/product-list/`
- **Description:** List all products.
- **Response:** 200 OK

### Product Detail
- **GET** `/api/store/<pk>/`
- **Description:** Get details of a product.
- **Response:** 200 OK

### Update Product
- **PUT** `/api/store/product/<pk>/update/`
- **Permissions:** Authenticated, Admin or Creator
- **Request Body:** multipart/form-data (fields to update)
- **Response:** 200 OK

### Delete Product
- **DELETE** `/api/store/products/<pk>/delete/`
- **Permissions:** Authenticated, Admin or Creator
- **Response:** 204 No Content

---

## Cart

### Add to Cart
- **POST** `/api/store/cart/add/<product_id>/`
- **Permissions:** Authenticated
- **Request Body:**
  ```json
  { "quantity": 2 }
  ```
- **Response:** 201 Created

### View Cart
- **GET** `/api/store/cart/`
- **Permissions:** Authenticated
- **Response:** 200 OK

### Remove from Cart
- **DELETE** `/api/store/cart/remove/<product_id>/`
- **Permissions:** Authenticated
- **Response:** 200 OK

---

## Orders

### Place Order (All Cart)
- **POST** `/api/store/order/place/`
- **Permissions:** Authenticated
- **Response:** 201 Created

### Place Order (All Cart, Alternative)
- **POST** `/api/store/orders/checkout/`
- **Permissions:** Authenticated
- **Response:** 201 Created

### Place Order (Selected Cart Items)
- **POST** `/api/store/orders/checkout/selected/`
- **Permissions:** Authenticated
- **Request Body:**
  ```json
  { "product_ids": [1, 2, 3] }
  ```
- **Response:** 201 Created

### Order History
- **GET** `/api/store/orders/history/`
- **Permissions:** Authenticated
- **Response:** 200 OK

---

## Categories (Admin Only)

### Create Category
- **POST** `/api/store/admin/category/create/`
- **Permissions:** Authenticated, Admin
- **Request Body:**
  ```json
  { "name": "Category Name", "slug": "category-slug" }
  ```
- **Response:** 201 Created

### List Categories
- **GET** `/api/store/admin/category/list/`
- **Permissions:** Authenticated
- **Response:** 200 OK

### Update Category
- **PUT** `/api/store/admin/category/update/<pk>/`
- **Permissions:** Authenticated, Admin
- **Request Body:**
  ```json
  { "name": "New Name" }
  ```
- **Response:** 200 OK

### Delete Category
- **DELETE** `/api/store/admin/category/delete/<pk>/`
- **Permissions:** Authenticated, Admin
- **Response:** 204 No Content

---

## Response Format
All API responses are wrapped in a standard format:
```json
{
  "success": true,
  "message": "...",
  "data": { ... },
  "status_code": 200
}
```

---

## Notes
- All endpoints (except register/login/logout) require JWT authentication via `Authorization: Bearer <token>` header.
- Admin endpoints require the user to have admin privileges.
- For file uploads (product image), use `multipart/form-data`.
- UI endpoints (ending with `-ui/`) serve HTML templates and are not part of the API.
