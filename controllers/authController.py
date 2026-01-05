import time
import logging
from flask import jsonify, request
from app import db, limiter
from models import User, Admin

# Configuration du logging
logging.basicConfig(filename='login_attempts.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


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

            return jsonify({
                'message': 'Login successful',
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

            return jsonify({
                'message': 'Admin login successful',
                'admin': {
                    'id': admin.id,
                    'email': admin.email,
                    'created_at': admin.created_at.isoformat()
                }
            }), 200

        except Exception as e:
            logging.error(f"Admin login error: {str(e)}")
            return jsonify({'error': str(e)}), 500
