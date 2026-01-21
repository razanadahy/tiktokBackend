import jwt
import functools
from flask import request, jsonify, current_app
from app import db
from models import Admin
from config import Config

def admin_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Admin authorization required'}), 401

        try:
            token = auth_header.split(' ')[1]
            payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            admin_id = payload.get('id')  # Assume JWT has 'id' for admin
            admin = Admin.query.filter_by(id=admin_id).first()
            if not admin:
                return jsonify({'error': 'Admin access denied'}), 403
            # Attach admin to request for use in function if needed
            request.admin = admin
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        return f(*args, **kwargs)
    return decorated_function