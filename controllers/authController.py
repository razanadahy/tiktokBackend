import os
import logging
import jwt
from datetime import datetime, timedelta, timezone
from flask import jsonify, request, current_app
from extension import db, limiter
from models import User, Admin


log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)

log_file = os.path.join(log_dir, 'logFile.log')

logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)



class AuthController:

    @staticmethod
    def login_user():
        """User login"""
        try:
            data = request.get_json()

            # Validate required fields
            required_fields = ['email', 'mot_de_passe']
            for field in required_fields:
                if field not in data:
                    return jsonify({'error': f'Missing required field: {field}'}), 400

            # Find user by email
            user = User.query.filter_by(email=data['email']).first()

            if not user:
                return jsonify({'error': 'Invalid email or password'}), 401

            # Check password
            if not user.check_password(data['mot_de_passe']):
                return jsonify({'error': 'Invalid email or password'}), 401

            # Generate token
            token_payload = {
                'user_id': user.id,
                'email': user.email,
                'exp': datetime.now(timezone.utc) + timedelta(hours=1)
            }
            token = jwt.encode(token_payload, current_app.config['SECRET_KEY'], algorithm='HS256')

            return jsonify({
                'token': token,
                'user': {
                    'id': user.id,
                    'nom': user.nom,
                    'email': user.email,
                    'code_parrainage': user.code_parrainage,
                    'created_at': user.created_at.isoformat()
                }
            }), 200

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @staticmethod
    @limiter.limit("5 per 15 minutes", methods=["POST"])
    def login_admin():
        """Admin login with brute force protection"""
        try:
            data = request.get_json()

            # Validate required fields
            required_fields = ['email', 'mot_de_passe']
            for field in required_fields:
                if field not in data:
                    return jsonify({'error': f'Missing required field: {field}'}), 400

            # Log attempt
            ip_address = request.remote_addr
            email = data.get('email', '')

            # Find admin by email
            admin = Admin.query.filter_by(email=email).first()

            if not admin:
                # Log failed attempt (email not found)
                logging.warning(f"Failed login attempt - Email not found: {email} from IP: {ip_address}")
                return jsonify({'error': 'Invalid email or password'}), 401

            # Check password
            if not admin.check_password(data['mot_de_passe']):
                # Log failed attempt (wrong password)
                logging.warning(f"Failed login attempt - Wrong password for: {email} from IP: {ip_address}")
                return jsonify({'error': 'Invalid email or password'}), 401

            # Log successful attempt
            logging.info(f"Successful admin login: {email} from IP: {ip_address}")

            # Generate token for admin
            token_payload = {
                'admin_id': admin.id,
                'email': admin.email,
                'is_admin': True,
                'exp': datetime.now(timezone.utc) + timedelta(hours=1)
            }
            token = jwt.encode(token_payload, current_app.config['SECRET_KEY'], algorithm='HS256')

            return jsonify({'token': token}), 200

        except Exception as e:
            logging.error(f"Admin login error: {str(e)}")
            return jsonify({'error': str(e)}), 500
