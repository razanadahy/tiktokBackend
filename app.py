from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask import request
from config import Config
import jwt
from functools import wraps

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:5173", "http://127.0.0.1:5173"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Authorization", "Content-Type", "X-Requested-With"],
        "expose_headers": ["Link"]
    }
})

# Rate limiting configuration
def rate_limit_key():
    if request.method == 'OPTIONS':
        return None  # Skip rate limiting for CORS preflight
    return get_remote_address()

limiter = Limiter(
    app=app,
    key_func=rate_limit_key,
    default_limits=["1000 per day", "200 per hour"],
    storage_uri="memory://"
)

# Import routes after app initialization
from routes.userRoutes import user_bp
from routes.authRoutes import auth_bp
from routes.qualificationRoutes import qualification_bp
from routes.parametreRoutes import parametre_bp
from routes.balanceRoutes import balance_bp
from routes.productRoutes import product_bp

# Register blueprints
app.register_blueprint(user_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(qualification_bp)
app.register_blueprint(parametre_bp)
app.register_blueprint(balance_bp)
app.register_blueprint(product_bp)


@app.before_request
def check_token_middleware():
    """Verify JWT token for all routes except login and static/public endpoints"""

    # List of endpoints to exclude from token verification
    excluded_endpoints = [
        'auth.login_user',
        'auth.login_admin',
        'user.create_user',  # User registration endpoint
        'static'
    ]

    # Skip auth for OPTIONS and excluded endpoints
    if request.method == 'OPTIONS' or request.endpoint in excluded_endpoints:
        return None

    # Get token from header
    auth_header = request.headers.get('Authorization')

    if not auth_header:
        return jsonify({'error': 'Missing authorization token'}), 401

    try:
        # Expected format: "Bearer <token>"
        if 'Bearer ' not in auth_header:
            return jsonify({'error': 'Invalid token format'}), 401

        token = auth_header.split(" ")[1]

        # Verify token
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])

        # Add user info to request context
        request.current_user_id = payload.get('user_id')

    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token has expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 401


if __name__ == '__main__':
    app.run(debug=True)
