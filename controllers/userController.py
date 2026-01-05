from flask import jsonify, request
from app import db
from models import User


class UserController:

    @staticmethod
    def create_user():
        """Create a new user"""
        try:
            data = request.get_json()

            # Validate required fields
            required_fields = ['nom', 'email', 'mot_de_passe']
            for field in required_fields:
                if field not in data:
                    return jsonify({'error': f'Missing required field: {field}'}), 400

            # Check if email already exists
            existing_user = User.query.filter_by(email=data['email']).first()
            if existing_user:
                return jsonify({'error': 'Email already exists'}), 400

            # Create new user
            new_user = User(
                nom=data['nom'],
                email=data['email'],
                mot_de_passe=data['mot_de_passe'],
                code_parrainage=data.get('code_parrainage')
            )

            db.session.add(new_user)
            db.session.commit()

            return jsonify({
                'message': 'User created successfully',
                'user': {
                    'id': new_user.id,
                    'nom': new_user.nom,
                    'email': new_user.email,
                    'code_parrainage': new_user.code_parrainage,
                    'created_at': new_user.created_at.isoformat()
                }
            }), 201

        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

    @staticmethod
    def get_all_users():
        """Get all users"""
        try:
            users = User.query.all()
            users_list = []

            for user in users:
                users_list.append({
                    'id': user.id,
                    'nom': user.nom,
                    'email': user.email,
                    'code_parrainage': user.code_parrainage,
                    'created_at': user.created_at.isoformat()
                })

            return jsonify({'users': users_list}), 200

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @staticmethod
    def get_user(user_id):
        """Get a single user by ID"""
        try:
            user = User.query.get(user_id)

            if not user:
                return jsonify({'error': 'User not found'}), 404

            return jsonify({
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
    def update_user(user_id):
        """Update a user"""
        try:
            user = User.query.get(user_id)

            if not user:
                return jsonify({'error': 'User not found'}), 404

            data = request.get_json()

            # Update fields if provided
            if 'nom' in data:
                user.nom = data['nom']

            if 'email' in data:
                # Check if new email already exists for another user
                existing_user = User.query.filter_by(email=data['email']).first()
                if existing_user and existing_user.id != user_id:
                    return jsonify({'error': 'Email already exists'}), 400
                user.email = data['email']

            if 'mot_de_passe' in data:
                from app import bcrypt
                user.mot_de_passe = bcrypt.generate_password_hash(data['mot_de_passe']).decode('utf-8')

            if 'code_parrainage' in data:
                user.code_parrainage = data['code_parrainage']

            db.session.commit()

            return jsonify({
                'message': 'User updated successfully',
                'user': {
                    'id': user.id,
                    'nom': user.nom,
                    'email': user.email,
                    'code_parrainage': user.code_parrainage,
                    'created_at': user.created_at.isoformat()
                }
            }), 200

        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

    @staticmethod
    def delete_user(user_id):
        """Delete a user"""
        try:
            user = User.query.get(user_id)

            if not user:
                return jsonify({'error': 'User not found'}), 404

            db.session.delete(user)
            db.session.commit()

            return jsonify({'message': 'User deleted successfully'}), 200

        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
