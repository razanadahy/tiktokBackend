# TikTokShop API - User CRUD Testing

## Base URL
```
http://localhost:5000
```

## User API Endpoints

### 1. Create User (POST)
**Endpoint:** `POST /api/users`

**Request Body:**
```json
{
    "nom": "John Doe",
    "email": "john@example.com",
    "mot_de_passe": "password123",
    "code_parrainage": "ABC123"
}
```

**cURL Command:**
```bash
curl -X POST http://localhost:5000/api/users \
  -H "Content-Type: application/json" \
  -d "{\"nom\":\"John Doe\",\"email\":\"john@example.com\",\"mot_de_passe\":\"password123\",\"code_parrainage\":\"ABC123\"}"
```

**Expected Response (201):**
```json
{
    "message": "User created successfully",
    "user": {
        "id": 2300,
        "nom": "John Doe",
        "email": "john@example.com",
        "code_parrainage": "ABC123",
        "created_at": "2026-01-02T12:00:00"
    }
}
```

---

### 2. Get All Users (GET)
**Endpoint:** `GET /api/users`

**cURL Command:**
```bash
curl -X GET http://localhost:5000/api/users
```

**Expected Response (200):**
```json
{
    "users": [
        {
            "id": 2300,
            "nom": "John Doe",
            "email": "john@example.com",
            "code_parrainage": "ABC123",
            "created_at": "2026-01-02T12:00:00"
        }
    ]
}
```

---

### 3. Get Single User (GET)
**Endpoint:** `GET /api/users/{user_id}`

**cURL Command:**
```bash
curl -X GET http://localhost:5000/api/users/2300
```

**Expected Response (200):**
```json
{
    "user": {
        "id": 2300,
        "nom": "John Doe",
        "email": "john@example.com",
        "code_parrainage": "ABC123",
        "created_at": "2026-01-02T12:00:00"
    }
}
```

---

### 4. Update User (PUT)
**Endpoint:** `PUT /api/users/{user_id}`

**Request Body (partial update allowed):**
```json
{
    "nom": "Jane Doe",
    "email": "jane@example.com",
    "code_parrainage": "XYZ789"
}
```

**cURL Command:**
```bash
curl -X PUT http://localhost:5000/api/users/2300 \
  -H "Content-Type: application/json" \
  -d "{\"nom\":\"Jane Doe\",\"email\":\"jane@example.com\"}"
```

**Expected Response (200):**
```json
{
    "message": "User updated successfully",
    "user": {
        "id": 2300,
        "nom": "Jane Doe",
        "email": "jane@example.com",
        "code_parrainage": "ABC123",
        "created_at": "2026-01-02T12:00:00"
    }
}
```

---

### 5. Delete User (DELETE)
**Endpoint:** `DELETE /api/users/{user_id}`

**cURL Command:**
```bash
curl -X DELETE http://localhost:5000/api/users/2300
```

**Expected Response (200):**
```json
{
    "message": "User deleted successfully"
}
```

---

## Admin Information
- **Email:** andrianiavo@gmail.com
- **Password:** 1234 (hashed in database)
- Password is encrypted using bcrypt

## Error Responses

### 400 Bad Request
```json
{
    "error": "Missing required field: email"
}
```

### 404 Not Found
```json
{
    "error": "User not found"
}
```

### 500 Internal Server Error
```json
{
    "error": "Error message details"
}
```

---

## Testing with Python Requests

```python
import requests
import json

BASE_URL = "http://localhost:5000/api/users"

# Create user
new_user = {
    "nom": "Test User",
    "email": "test@example.com",
    "mot_de_passe": "test123",
    "code_parrainage": "REF001"
}
response = requests.post(BASE_URL, json=new_user)
print(response.json())

# Get all users
response = requests.get(BASE_URL)
print(response.json())

# Get single user
user_id = 2300
response = requests.get(f"{BASE_URL}/{user_id}")
print(response.json())

# Update user
update_data = {"nom": "Updated Name"}
response = requests.put(f"{BASE_URL}/{user_id}", json=update_data)
print(response.json())

# Delete user
response = requests.delete(f"{BASE_URL}/{user_id}")
print(response.json())
```

---

## Database Structure

### Users Table
| Column | Type | Constraints |
|--------|------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO_INCREMENT (starts at 2300) |
| nom | VARCHAR(100) | NOT NULL |
| email | VARCHAR(120) | UNIQUE, NOT NULL |
| mot_de_passe | VARCHAR(255) | NOT NULL (encrypted) |
| code_parrainage | VARCHAR(50) | NULLABLE |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP |

### Admins Table
| Column | Type | Constraints |
|--------|------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO_INCREMENT |
| email | VARCHAR(120) | UNIQUE, NOT NULL |
| mot_de_passe | VARCHAR(255) | NOT NULL (encrypted) |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP |
