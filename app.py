from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
CORS(app)

# Rate limiting configuration
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# Import routes after app initialization
from routes.userRoutes import user_bp
from routes.authRoutes import auth_bp
from routes.qualificationRoutes import qualification_bp
from routes.parametreRoutes import parametre_bp

# Register blueprints
app.register_blueprint(user_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(qualification_bp)
app.register_blueprint(parametre_bp)


if __name__ == '__main__':
    app.run(debug=True)
