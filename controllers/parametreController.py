from flask import jsonify, request
from app import db
from models import User, Parametre


class ParametreController:

    @staticmethod
    def get_user_parametre(user_id):
        """Get parameters of a user by user_id"""
        try:
            # Check if user exists
            user = User.query.filter_by(id=user_id).first()
            if not user:
                return jsonify({'error': 'User not found'}), 404

            # Get user's parameters
            parametre = Parametre.query.filter_by(id_utilisateur=user_id).first()

            if not parametre:
                return jsonify({
                    'user_id': user_id,
                    'parametre': None,
                    'message': 'User has no parameters assigned'
                }), 200

            return jsonify({
                'user_id': user_id,
                'parametre': {
                    'id': parametre.id,
                    'langue': parametre.langue,
                    'devise': parametre.devise
                },
                'created_at': parametre.created_at.isoformat(),
                'updated_at': parametre.updated_at.isoformat()
            }), 200

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @staticmethod
    def update_user_parametre(user_id):
        """Update parameters of a user"""
        try:
            data = request.get_json()

            # Check if user exists
            user = User.query.filter_by(id=user_id).first()
            if not user:
                return jsonify({'error': 'User not found'}), 404

            # Validate langue
            if 'langue' in data:
                if data['langue'] not in ['FR', 'ANG']:
                    return jsonify({'error': 'Invalid langue. Must be FR or ANG'}), 400

            # Validate devise
            if 'devise' in data:
                if data['devise'] not in ['EURO', 'DOLLAR']:
                    return jsonify({'error': 'Invalid devise. Must be EURO or DOLLAR'}), 400

            # Get user's parameters
            parametre = Parametre.query.filter_by(id_utilisateur=user_id).first()

            if parametre:
                # Update existing parameters
                updated = False
                if 'langue' in data and data['langue'] != parametre.langue:
                    parametre.langue = data['langue']
                    updated = True
                if 'devise' in data and data['devise'] != parametre.devise:
                    parametre.devise = data['devise']
                    updated = True
                message = 'Parametre updated successfully' if updated else 'No changes made'
            else:
                # Create new parameters
                parametre = Parametre(
                    id_utilisateur=user_id,
                    langue=data.get('langue', 'ANG'),
                    devise=data.get('devise', 'DOLLAR')
                )
                db.session.add(parametre)
                message = 'Parametre created successfully'

            db.session.commit()

            return jsonify({
                'message': message,
                'user_id': user_id,
                'parametre': {
                    'id': parametre.id,
                    'langue': parametre.langue,
                    'devise': parametre.devise
                }
            }), 200

        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
