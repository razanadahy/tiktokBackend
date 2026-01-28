import jwt
import functools
from flask import request, jsonify, current_app
from models import Admin

def admin_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Admin authorization required'}), 401

        try:
            token = auth_header.split(' ')[1]
            payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            admin_id = payload.get('admin_id')
            admin = Admin.query.filter_by(id=admin_id).first()
            print(admin, token, admin_id)
            if not admin:
                return jsonify({'error': 'Admin access denied'}), 403
            # Attach admin to request for use in function if needed
            request.admin = admin
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        return f(*args, **kwargs)
    return decorated_function


def user_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'User authorization required'}), 401

        try:
            token = auth_header.split(' ')[1]
            payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            user_id = payload.get('user_id')
            from models import User
            user = User.query.filter_by(id=user_id).first()
            if not user:
                return jsonify({'error': 'User access denied'}), 403
            request.user = user
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        return f(*args, **kwargs)
    return decorated_function