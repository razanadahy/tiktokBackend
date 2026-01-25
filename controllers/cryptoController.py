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
            'message': 'Crypto added',
            'crypto': {
                'idCrypto': crypto.idCrypto,
                'nomCrypto': crypto.nomCrypto,
                'sigleCrypto': crypto.sigleCrypto,
                'adress': crypto.adress,
                'minDepot': float(crypto.minDepot)
            }
        }), 201