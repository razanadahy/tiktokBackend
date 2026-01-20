from flask import jsonify, request
from app import db
from models import User, Qualification, UtilisateurQualification


class QualificationController:

    @staticmethod
    def get_user_qualification(user_id):
        """Get qualification of a user by user_id"""
        try:
            # Check if user exists
            user = User.query.filter_by(id=user_id).first()
            if not user:
                return jsonify({'error': 'User not found'}), 404

            # Get user's qualification
            user_qualif = UtilisateurQualification.query.filter_by(id_utilisateur=user_id).first()

            if not user_qualif:
                return jsonify({
                    'user_id': user_id,
                    'qualification': None,
                    'message': 'User has no qualification assigned'
                }), 200

            qualification = Qualification.query.filter_by(id=user_qualif.id_qualification).first()

            return jsonify({
                'user_id': user_id,
                'qualification': {
                    'id': qualification.id,
                    'valeur': qualification.valeur,
                    'nom': qualification.nom
                },
                'assigned_at': user_qualif.created_at.isoformat()
            }), 200

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @staticmethod
    def update_user_qualification(user_id):
        """Update/set qualification of a user"""
        try:
            data = request.get_json()

            # Validate required fields
            if 'id_qualification' not in data:
                return jsonify({'error': 'Missing required field: id_qualification'}), 400

            # Check if user exists
            user = User.query.filter_by(id=user_id).first()
            if not user:
                return jsonify({'error': 'User not found'}), 404

            # Check if qualification exists
            qualification = Qualification.query.get(data['id_qualification'])
            if not qualification:
                return jsonify({'error': 'Qualification not found'}), 404

            # Check if user already has a qualification
            user_qualif = UtilisateurQualification.query.filter_by(id_utilisateur=user_id).first()

            if user_qualif:
                # Update existing qualification
                old_qualif_id = user_qualif.id_qualification
                user_qualif.id_qualification = data['id_qualification']
                message = f'Qualification updated from {old_qualif_id} to {data["id_qualification"]}'
            else:
                # Create new qualification assignment
                user_qualif = UtilisateurQualification(
                    id_utilisateur=user_id,
                    id_qualification=data['id_qualification']
                )
                db.session.add(user_qualif)
                message = 'Qualification assigned successfully'

            db.session.commit()

            return jsonify({
                'message': message,
                'user_id': user_id,
                'qualification': {
                    'id': qualification.id,
                    'valeur': qualification.valeur,
                    'nom': qualification.nom
                }
            }), 200

        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
