from flask import Flask, request, jsonify
from flask_cors import CORS
from flask import request
from config import Config
import jwt
from extension import db, bcrypt, limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
app.config.from_object(Config)
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:5173", "http://127.0.0.1:5173"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Authorization", "Content-Type", "X-Requested-With"],
        "expose_headers": ["Link"]
    }
})
db.init_app(app)
bcrypt.init_app(app)
limiter.init_app(app)
# Rate limiting configuration
def rate_limit_key():
    if request.method == 'OPTIONS':
        return None  # Skip rate limiting for CORS preflight
    return get_remote_address()

# Import routes after app initialization
from routes.userRoutes import user_bp
from routes.authRoutes import auth_bp
from routes.qualificationRoutes import qualification_bp
from routes.parametreRoutes import parametre_bp
from routes.balanceRoutes import balance_bp
from routes.productRoutes import product_bp
from routes.cryptoRoutes import crypto_bp
from routes.assetRoutes import asset_bp
from routes.configRetraitRoutes import configRetrait_bp
from routes.adminRoutes import admin_bp
from routes.transactionsRoutes import transactions_bp
from routes.commandeRoutes import commande_bp

# Register blueprints
app.register_blueprint(user_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(qualification_bp)
app.register_blueprint(parametre_bp)
app.register_blueprint(crypto_bp)
app.register_blueprint(balance_bp)
app.register_blueprint(product_bp)
app.register_blueprint(asset_bp)
app.register_blueprint(configRetrait_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(transactions_bp)
app.register_blueprint(commande_bp)


@app.before_request
def check_token_middleware():

    excluded_endpoints = [
        'auth.login_user',
        'auth.login_admin',
        'user.create_user',
        'static'
    ]

    # Skip auth for OPTIONS and excluded endpoints
    if request.method == 'OPTIONS' or request.endpoint in excluded_endpoints or request.blueprint == 'assets':
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
