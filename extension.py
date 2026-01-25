from flask import request
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

db = SQLAlchemy()
bcrypt = Bcrypt()
limiter = Limiter(
    key_func=lambda: get_remote_address() if request.method != 'OPTIONS' else None,
    default_limits=["1000 per day", "200 per hour"],
    storage_uri="memory://"
)