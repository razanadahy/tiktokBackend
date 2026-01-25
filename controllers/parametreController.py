from flask import jsonify, request
from extension import db
from models import User, Parametre, MinRetrait
from util.auth_utils import admin_required


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

            # Get minRetrait
            minRetrait = MinRetrait.query.first()  # Get the first (and probably only) minRetrait

            if not parametre:
                return jsonify({
                    'user_id': user_id,
                    'parametre': None,
                    'minRetrait':  1.00,
                    'message': 'User has no parameters assigned'
                }), 200

            # Format minRetrait data
            minRetrait_data = 1
            if minRetrait:
                minRetrait_data = minRetrait.montant_min

            return jsonify({
                'user_id': user_id,
                'parametre': {
                    'id': parametre.id,
                    'langue': parametre.langue,
                    'devise': parametre.devise
                },
                'minRetrait': minRetrait_data,
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

    @staticmethod
    @admin_required
    def update_min_retrait():
        """Update minimum withdrawal amount"""
        try:
            data = request.get_json()

            # Validate required fields
            if 'montant_min' not in data:
                return jsonify({'error': 'montant_min is required'}), 400

            montant_min = data.get('montant_min')
            devise = data.get('devise', 'USD')
            coin = data.get('coin', 'USDT')

            # Validate montant_min is positive number
            try:
                montant_min_float = float(montant_min)
                if montant_min_float <= 0:
                    return jsonify({'error': 'montant_min must be a positive number'}), 400
            except ValueError:
                return jsonify({'error': 'montant_min must be a valid number'}), 400

            # Get existing minRetrait or create new one
            minRetrait = MinRetrait.query.first()

            if minRetrait:
                # Update existing minRetrait
                minRetrait.montant_min = montant_min_float
                minRetrait.devise = devise
                minRetrait.coin = coin
                message = 'MinRetrait updated successfully'
            else:
                # Create new minRetrait
                minRetrait = MinRetrait(
                    montant_min=montant_min_float,
                    devise=devise,
                    coin=coin
                )
                db.session.add(minRetrait)
                message = 'MinRetrait created successfully'

            db.session.commit()

            return jsonify({
                'message': message,
                'minRetrait': {
                    'id': minRetrait.id,
                    'montant_min': float(minRetrait.montant_min),
                    'devise': minRetrait.devise,
                    'coin': minRetrait.coin,
                    'dateModif': minRetrait.dateModif.isoformat()
                }
            }), 200

        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
