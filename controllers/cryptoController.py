from flask import jsonify, request
from extension import db
from models import Crypto
from util.auth_utils import admin_required


class CryptoController:
    @staticmethod
    def list_cryptos():
        cryptos = Crypto.query.filter_by(isDeleted=False).all()
        result = []
        for crypto in cryptos:
            result.append({
                'idCrypto': crypto.idCrypto,
                'nomCrypto': crypto.nomCrypto,
                'sigleCrypto': crypto.sigleCrypto,
                'commentaire': crypto.commentaire,
                'adress': crypto.adress,
                'minDepot': float(crypto.minDepot)
            })
        return jsonify( result), 200

    @staticmethod
    @admin_required
    def add_crypto():
        data = request.get_json()
        nomCrypto = data.get('nomCrypto')
        sigleCrypto = data.get('sigleCrypto')
        commentaire = data.get('commentaire')
        adress = data.get('adress')
        minDepot = data.get('minDepot')

        if not all([nomCrypto, sigleCrypto, adress, minDepot]):
            return jsonify({'error': 'Missing required fields'}), 400

        crypto = Crypto(
            nomCrypto=nomCrypto,
            sigleCrypto=sigleCrypto,
            commentaire=commentaire,
            adress=adress,
            minDepot=float(minDepot)
        )
        db.session.add(crypto)
        db.session.commit()
        return jsonify({
            'message': 'Crypto ajouté',
            'crypto': {
                'idCrypto': crypto.idCrypto,
                'nomCrypto': crypto.nomCrypto,
                'sigleCrypto': crypto.sigleCrypto,
                'adress': crypto.adress,
                'minDepot': float(crypto.minDepot),
                'commentaire': crypto.commentaire
            }
        }), 201

    @staticmethod
    def get_crypto(id):
        crypto = Crypto.query.get(id)
        if not crypto or crypto.isDeleted:
            return jsonify({'error': 'Crypto not found'}), 404

        return jsonify({
            'idCrypto': crypto.idCrypto,
            'nomCrypto': crypto.nomCrypto,
            'sigleCrypto': crypto.sigleCrypto,
            'commentaire': crypto.commentaire,
            'adress': crypto.adress,
            'minDepot': float(crypto.minDepot)
        }), 200

    @staticmethod
    @admin_required
    def update_crypto(id):
        data = request.get_json()
        crypto = Crypto.query.get(id)

        if not crypto or crypto.isDeleted:
            return jsonify({'error': 'Crypto not found'}), 404

        if 'nomCrypto' in data:
            crypto.nomCrypto = data['nomCrypto']
        if 'sigleCrypto' in data:
            crypto.sigleCrypto = data['sigleCrypto']
        if 'commentaire' in data:
            crypto.commentaire = data['commentaire']
        if 'adress' in data:
            crypto.adress = data['adress']
        if 'minDepot' in data:
            crypto.minDepot = float(data['minDepot'])

        try:
            db.session.commit()
            return jsonify({
                'message': 'Crypto updated',
                'crypto': {
                    'idCrypto': crypto.idCrypto,
                    'nomCrypto': crypto.nomCrypto,
                    'sigleCrypto': crypto.sigleCrypto,
                    'adress': crypto.adress,
                    'minDepot': float(crypto.minDepot),
                    'commentaire': crypto.commentaire,
                }
            }), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

    @staticmethod
    @admin_required
    def delete_crypto(id):
        crypto = Crypto.query.get(id)

        if not crypto or crypto.isDeleted:
            return jsonify({'error': 'Crypto not found'}), 404

        crypto.isDeleted = True

        try:
            db.session.commit()
            return jsonify({'message': 'Crypto successfully deleted'}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
