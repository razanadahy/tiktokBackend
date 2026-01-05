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
        "qualification": {
            "id": 1,
            "valeur": 0,
            "nom": "DEBUTANT"
        },
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

### 6. Change Password (PUT)
**Endpoint:** `PUT /api/users/{user_id}/password`

**Request Body:**
```json
{
    "precedent_mdp": "password123",
    "nouveau_mdp": "newpassword456"
}
```

**cURL Command:**
```bash
curl -X PUT http://localhost:5000/api/users/2300/password \
  -H "Content-Type: application/json" \
  -d "{\"precedent_mdp\":\"password123\",\"nouveau_mdp\":\"newpassword456\"}"
```

**Expected Response (200):**
```json
{
    "message": "Password changed successfully"
}
```

**Error Response (400):**
```json
{
    "error": "Missing required field: precedent_mdp"
}
```

**Error Response (401):**
```json
{
    "error": "Incorrect current password"
}
```

**Error Response (404):**
```json
{
    "error": "User not found"
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

---

## Auth API Endpoints

### 6. User Login (POST)
**Endpoint:** `POST /api/auth/login/user`

**Request Body:**
```json
{
    "email": "john@example.com",
    "mot_de_passe": "password123"
}
```

**cURL Command:**
```bash
curl -X POST http://localhost:5000/api/auth/login/user \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"john@example.com\",\"mot_de_passe\":\"password123\"}"
```

**Expected Response (200):**
```json
{
    "message": "Login successful",
    "user": {
        "id": 2300,
        "nom": "John Doe",
        "email": "john@example.com",
        "code_parrainage": "ABC123",
        "created_at": "2026-01-02T12:00:00"
    }
}
```

**Error Response (401):**
```json
{
    "error": "Invalid email or password"
}
```

---

### 7. Admin Login (POST)
**Endpoint:** `POST /api/auth/login/admin`

> **Protection anti-brute force activée :** Maximum 5 tentatives par IP toutes les 15 minutes.

**Request Body:**
```json
{
    "email": "andrianiavo@gmail.com",
    "mot_de_passe": "1234"
}
```

**cURL Command:**
```bash
curl -X POST http://localhost:5000/api/auth/login/admin \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"andrianiavo@gmail.com\",\"mot_de_passe\":\"1234\"}"
```

**Expected Response (200):**
```json
{
    "message": "Admin login successful",
    "admin": {
        "id": 1,
        "email": "andrianiavo@gmail.com",
        "created_at": "2026-01-02T12:00:00"
    }
}
```

**Error Response (401):**
```json
{
    "error": "Invalid email or password"
}
```

**Rate Limited Response (429):**
```json
{
    "error": "Rate limit exceeded. Try again in 15 minutes."
}
```

---

## Testing Auth Endpoints with Python

```python
import requests

BASE_URL = "http://localhost:5000/api/auth"

# User Login
user_login = {
    "email": "john@example.com",
    "mot_de_passe": "password123"
}
response = requests.post(f"{BASE_URL}/login/user", json=user_login)
print(response.json())

# Admin Login
admin_login = {
    "email": "andrianiavo@gmail.com",
    "mot_de_passe": "1234"
}
response = requests.post(f"{BASE_URL}/login/admin", json=admin_login)
print(response.json())
```

---

## Security Measures

### Admin Login Protection
The admin login endpoint includes the following security measures:

| Protection | Limit | Description |
|------------|-------|-------------|
| Rate Limiting | 5 requests / 15 min per IP | Prevents brute force attacks |
| Global Limits | 200/day, 50/hour | Overall API protection |
| Logging | All attempts recorded | Failed/success login attempts logged to `login_attempts.log` |

### Log File Format
Failed and successful login attempts are logged to `login_attempts.log`:
```
2026-01-05 10:30:00,123 - WARNING - Failed login attempt - Wrong password for: andrianiavo@gmail.com from IP: 192.168.1.100
2026-01-05 10:30:05,456 - INFO - Successful admin login: andrianiavo@gmail.com from IP: 192.168.1.100
```

### Error Response Codes
| Code | Meaning |
|------|---------|
| 400 | Missing required field |
| 401 | Invalid credentials |
| 429 | Rate limit exceeded |
| 500 | Server error |

---

## Qualification API Endpoints

### Available Qualifications
| valeur | nom |
|--------|-----|
| 0 | DEBUTANT |
| 1 | VALIDER |
| 2 | VIP_1 |
| 3 | VIP_2 |
| 4 | VIP_3 |
| 5 | VIP_4 |

---

### 8. Get User Qualification (GET)
**Endpoint:** `GET /api/qualifications/user/{user_id}`

**cURL Command:**
```bash
curl -X GET http://localhost:5000/api/qualifications/user/2300
```

**Expected Response (200):**
```json
{
    "user_id": 2300,
    "qualification": {
        "id": 1,
        "valeur": 1,
        "nom": "VALIDER"
    },
    "assigned_at": "2026-01-02T12:00:00"
}
```

**Response - No Qualification (200):**
```json
{
    "user_id": 2300,
    "qualification": null,
    "message": "User has no qualification assigned"
}
```

**Error Response (404):**
```json
{
    "error": "User not found"
}
```

---

### 9. Update User Qualification (PUT)
**Endpoint:** `PUT /api/qualifications/user/{user_id}`

**Request Body:**
```json
{
    "id_qualification": 3
}
```

**cURL Command:**
```bash
curl -X PUT http://localhost:5000/api/qualifications/user/2300 \
  -H "Content-Type: application/json" \
  -d "{\"id_qualification\":3}"
```

**Expected Response (200):**
```json
{
    "message": "Qualification assigned successfully",
    "user_id": 2300,
    "qualification": {
        "id": 3,
        "valeur": 2,
        "nom": "VIP_1"
    }
}
```

**Update Existing Response (200):**
```json
{
    "message": "Qualification updated from 3 to 4",
    "user_id": 2300,
    "qualification": {
        "id": 4,
        "valeur": 3,
        "nom": "VIP_2"
    }
}
```

**Error Response (400):**
```json
{
    "error": "Missing required field: id_qualification"
}
```

**Error Response (404):**
```json
{
    "error": "User not found"
}
```
or
```json
{
    "error": "Qualification not found"
}
```

---

## Testing Qualification Endpoints with Python

```python
import requests

BASE_URL = "http://localhost:5000/api/qualifications"

# Get user qualification
user_id = 2300
response = requests.get(f"{BASE_URL}/user/{user_id}")
print(response.json())

# Update user qualification
update_data = {"id_qualification": 3}  # VIP_1
response = requests.put(f"{BASE_URL}/user/{user_id}", json=update_data)
print(response.json())
```

---

## Database Structure (Updated)

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

### Qualifications Table
| Column | Type | Constraints |
|--------|------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO_INCREMENT |
| valeur | INTEGER | UNIQUE, NOT NULL |
| nom | VARCHAR(50) | NOT NULL |

### UtilisateurQualifications Table
| Column | Type | Constraints |
|--------|------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO_INCREMENT |
| id_utilisateur | INTEGER | FOREIGN KEY (users.id), NOT NULL |
| id_qualification | INTEGER | FOREIGN KEY (qualifications.id), NOT NULL |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP |

### Parametres Table
| Column | Type | Constraints |
|--------|------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO_INCREMENT |
| id_utilisateur | INTEGER | FOREIGN KEY (users.id), NOT NULL, UNIQUE |
| langue | VARCHAR(10) | NOT NULL, DEFAULT 'ANG' |
| devise | VARCHAR(10) | NOT NULL, DEFAULT 'DOLLAR' |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP |
| updated_at | DATETIME | DEFAULT CURRENT_TIMESTAMP |

---

## Parametre API Endpoints

### 10. Get User Parametre (GET)
**Endpoint:** `GET /api/parametres/user/{user_id}`

**cURL Command:**
```bash
curl -X GET http://localhost:5000/api/parametres/user/2300
```

**Expected Response (200):**
```json
{
    "user_id": 2300,
    "parametre": {
        "id": 1,
        "langue": "ANG",
        "devise": "DOLLAR"
    },
    "created_at": "2026-01-02T12:00:00",
    "updated_at": "2026-01-02T12:00:00"
}
```

**Response - No Parametre (200):**
```json
{
    "user_id": 2300,
    "parametre": null,
    "message": "User has no parameters assigned"
}
```

**Error Response (404):**
```json
{
    "error": "User not found"
}
```

---

### 11. Update User Parametre (PUT)
**Endpoint:** `PUT /api/parametres/user/{user_id}`

**Request Body (partial update allowed):**
```json
{
    "langue": "FR",
    "devise": "EURO"
}
```

**cURL Command:**
```bash
curl -X PUT http://localhost:5000/api/parametres/user/2300 \
  -H "Content-Type: application/json" \
  -d "{\"langue\":\"FR\",\"devise\":\"EURO\"}"
```

**Expected Response (200):**
```json
{
    "message": "Parametre updated successfully",
    "user_id": 2300,
    "parametre": {
        "id": 1,
        "langue": "FR",
        "devise": "EURO"
    }
}
```

**Error Response (400):**
```json
{
    "error": "Invalid langue. Must be FR or ANG"
}
```
or
```json
{
    "error": "Invalid devise. Must be EURO or DOLLAR"
}
```

**Error Response (404):**
```json
{
    "error": "User not found"
}
```

---

## Testing Parametre Endpoints with Python

```python
import requests

BASE_URL = "http://localhost:5000/api/parametres"

# Get user parametre
user_id = 2300
response = requests.get(f"{BASE_URL}/user/{user_id}")
print(response.json())

# Update user parametre
update_data = {
    "langue": "FR",
    "devise": "EURO"
}
response = requests.put(f"{BASE_URL}/user/{user_id}", json=update_data)
print(response.json())
```
