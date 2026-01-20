from flask import jsonify, request
from app import db
from models import User, Qualification, UtilisateurQualification, Parametre


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

            # Get the "Debutant" qualification (valeur=0)
            debutant_qualif = Qualification.query.filter_by(valeur=0).first()

            # Create user's qualification (Debutant by default)
            user_qualification = UtilisateurQualification(
                id_utilisateur=new_user.id,
                id_qualification=debutant_qualif.id
            )
            db.session.add(user_qualification)

            # Create default parameters (ANG, DOLLAR)
            user_parametre = Parametre(
                id_utilisateur=new_user.id,
                langue='ANG',
                devise='DOLLAR'
            )
            db.session.add(user_parametre)
            db.session.commit()

            return jsonify({
                'message': 'User created successfully',
                'user': {
                    'id': new_user.id,
                    'nom': new_user.nom,
                    'email': new_user.email,
                    'code_parrainage': new_user.code_parrainage,
                    'qualification': {
                        'id': debutant_qualif.id,
                        'valeur': debutant_qualif.valeur,
                        'nom': debutant_qualif.nom
                    },
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
            user = User.query.filter_by(id=user_id).first()

            if not user:
                return jsonify({'error': 'User not found'}), 404

            return jsonify({
                'users': {
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
            user = User.query.filter_by(id=user_id).first()

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
            user = User.query.filter_by(id=user_id).first()

            if not user:
                return jsonify({'error': 'User not found'}), 404

            db.session.delete(user)
            db.session.commit()

            return jsonify({'message': 'User deleted successfully'}), 200

        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

    @staticmethod
    def change_password(user_id):
        """Change user password"""
        try:
            data = request.get_json()

            # Validate required fields
            required_fields = ['precedent_mdp', 'nouveau_mdp']
            for field in required_fields:
                if field not in data:
                    return jsonify({'error': f'Missing required field: {field}'}), 400

            # Check if user exists
            user = User.query.filter_by(id=user_id).first()
            if not user:
                return jsonify({'error': 'User not found'}), 404

            # Verify current password
            if not user.check_password(data['precedent_mdp']):
                return jsonify({'error': 'Incorrect current password'}), 401

            # Update password
            from app import bcrypt
            user.mot_de_passe = bcrypt.generate_password_hash(data['nouveau_mdp']).decode('utf-8')
            db.session.commit()

            return jsonify({
                'message': 'Password changed successfully'
            }), 200

        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

    @staticmethod
    def get_current_user():
        """Get current user from token"""
        try:
            user_id = getattr(request, 'current_user_id', None)
            if not user_id:
                return jsonify({'error': 'No user context found'}), 401

            user = User.query.filter_by(id=user_id).first()
            if not user:
                return jsonify({'error': 'User not found'}), 404

            return jsonify({
                'users': {
                    'id': user.id,
                    'nom': user.nom,
                    'email': user.email,
                    'code_parrainage': user.code_parrainage,
                    'created_at': user.created_at.isoformat()
                }
            }), 200

        except Exception as e:
            return jsonify({'error': str(e)}), 500
