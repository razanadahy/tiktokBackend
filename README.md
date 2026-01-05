# TikTokShop - Application Flask avec MySQL

## Description
Application Flask avec base de données MySQL (via XAMPP) et authentification sécurisée avec cryptage des mots de passe.

## Technologies utilisées
- **Flask** 3.1.2 - Framework web Python
- **SQLAlchemy** 2.0.45 - ORM Python
- **Flask-SQLAlchemy** 3.1.1 - Intégration SQLAlchemy pour Flask
- **Flask-Bcrypt** 1.0.1 - Cryptage des mots de passe
- **PyMySQL** 1.1.2 - Driver MySQL pour Python
- **MySQL/MariaDB** (via XAMPP)

## Structure du projet
```
TikTokShop/
├── app.py                  # Application Flask principale
├── config.py               # Configuration de la base de données
├── models.py               # Modèles de données (User, Admin, Product)
├── init_db.py              # Script d'initialisation de la base de données
├── requirements.txt        # Dépendances Python
├── controllers/
│   ├── __init__.py
│   └── userController.py   # Contrôleur CRUD pour les utilisateurs
├── routes/
│   ├── __init__.py
│   └── userRoutes.py       # Routes API pour les utilisateurs
├── API_TESTING.md          # Documentation des endpoints API
└── README.md               # Ce fichier
```

## Installation

### 1. Prérequis
- Python 3.14+
- XAMPP avec MySQL/MariaDB en cours d'exécution

### 2. Installation des dépendances
```bash
py -m pip install -r requirements.txt
```

### 3. Initialiser la base de données
```bash
py init_db.py
```

Cela va:
- Créer la base de données `tiktokshop`
- Créer les tables `users`, `admins`, et `products`
- Configurer l'auto-increment de la table users à partir de 2300
- Créer un compte admin par défaut

## Configuration

### Base de données (config.py)
```python
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost:3306/tiktokshop'
```

### Compte Admin par défaut
- **Email:** andrianiavo@gmail.com
- **Mot de passe:** 1234 (crypté dans la base de données)

## Modèles de données

### User (Table: users)
- `id` - INTEGER (PRIMARY KEY, AUTO_INCREMENT à partir de 2300)
- `nom` - VARCHAR(100) (NOT NULL)
- `email` - VARCHAR(120) (UNIQUE, NOT NULL)
- `mot_de_passe` - VARCHAR(255) (NOT NULL, crypté avec bcrypt)
- `code_parrainage` - VARCHAR(50) (NULLABLE)
- `created_at` - DATETIME

### Admin (Table: admins)
- `id` - INTEGER (PRIMARY KEY)
- `email` - VARCHAR(120) (UNIQUE, NOT NULL)
- `mot_de_passe` - VARCHAR(255) (NOT NULL, crypté avec bcrypt)
- `created_at` - DATETIME

### Product (Table: products)
- `id` - INTEGER (PRIMARY KEY)
- `name` - VARCHAR(200) (NOT NULL)
- `description` - TEXT
- `price` - DECIMAL(10, 2) (NOT NULL)
- `stock` - INTEGER
- `created_at` - DATETIME
- `updated_at` - DATETIME

## API Endpoints

### User CRUD
- `POST /api/users` - Créer un nouvel utilisateur
- `GET /api/users` - Récupérer tous les utilisateurs
- `GET /api/users/<id>` - Récupérer un utilisateur par ID
- `PUT /api/users/<id>` - Mettre à jour un utilisateur
- `DELETE /api/users/<id>` - Supprimer un utilisateur

Consultez [API_TESTING.md](API_TESTING.md) pour des exemples détaillés de requêtes.

## Démarrer l'application

```bash
py app.py
```

L'application sera accessible à l'adresse: `http://localhost:5000`

## Test de la connexion à la base de données

Visitez: `http://localhost:5000/test-db`

## Sécurité

- Tous les mots de passe sont cryptés avec **bcrypt** avant d'être stockés
- Les mots de passe ne sont jamais retournés dans les réponses API
- Protection contre les injections SQL grâce à SQLAlchemy ORM

## Développement futur

- Ajouter l'authentification JWT
- Implémenter des middlewares de validation
- Ajouter des tests unitaires
- Créer des endpoints pour les produits
- Implémenter un système de pagination

## Auteur

Andrianiavo (andrianiavo@gmail.com)
