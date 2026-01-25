from flask import jsonify, request
from extension import db
from models import ConfigRetrait
from datetime import datetime

class ConfigRetraitController:
    @staticmethod
    def get_config(user_id):
        """Get withdrawal config for a user"""
        try:
            config = ConfigRetrait.query.filter_by(userId=user_id).first()

            if not config:
                return jsonify({'error': 'Configuration not found'}), 404

            return jsonify({
                'config': {
                    'id': config.id,
                    'userId': config.userId,
                    'depositAdress': config.depositAdress,
                    'coin': config.coin,
                    'reseau': config.reseau,
                    'dateModif': config.dateModif.isoformat()
                }
            }), 200

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @staticmethod
    def add_config(user_id):
        """Add new withdrawal config for a user"""
        try:
            data = request.get_json()

            # Check if config already exists for this user
            existing_config = ConfigRetrait.query.filter_by(userId=user_id).first()
            if existing_config:
                return jsonify({'error': 'Configuration already exists for this user. Use update instead.'}), 400

            depositAdress = data.get('depositAdress')
            coin = data.get('coin')
            reseau = data.get('reseau')

            if not all([depositAdress, coin, reseau]):
                return jsonify({'error': 'depositAdress, coin, and reseau are required'}), 400

            # Create new config
            config = ConfigRetrait(
                userId=user_id,
                depositAdress=depositAdress,
                coin=coin,
                reseau=reseau
            )

            db.session.add(config)
            db.session.commit()

            return jsonify({
                'message': 'Configuration created successfully',
                'config': {
                    'id': config.id,
                    'userId': config.userId,
                    'depositAdress': config.depositAdress,
                    'coin': config.coin,
                    'reseau': config.reseau,
                    'dateModif': config.dateModif.isoformat()
                }
            }), 201

        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

    @staticmethod
    def update_config(user_id):
        """Update existing withdrawal config for a user"""
        try:
            data = request.get_json()

            # Find existing config
            config = ConfigRetrait.query.filter_by(userId=user_id).first()

            if not config:
                return jsonify({'error': 'Configuration not found'}), 404

            # Update fields if provided
            if 'depositAdress' in data:
                config.depositAdress = data['depositAdress']
            if 'coin' in data:
                config.coin = data['coin']
            if 'reseau' in data:
                config.reseau = data['reseau']

            # dateModif will be automatically updated by onupdate
            db.session.commit()

            return jsonify({
                'message': 'Configuration updated successfully',
                'config': {
                    'id': config.id,
                    'userId': config.userId,
                    'depositAdress': config.depositAdress,
                    'coin': config.coin,
                    'reseau': config.reseau,
                    'dateModif': config.dateModif.isoformat()
                }
            }), 200

        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

    @staticmethod
    def delete_config(user_id):
        """Delete withdrawal config for a user"""
        try:
            config = ConfigRetrait.query.filter_by(userId=user_id).first()

            if not config:
                return jsonify({'error': 'Configuration not found'}), 404

            db.session.delete(config)
            db.session.commit()

            return jsonify({'message': 'Configuration deleted successfully'}), 200

        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
