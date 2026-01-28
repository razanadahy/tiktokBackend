from flask import jsonify, request
from extension import db
from models import Boost, BoostStatut
from util.auth_utils import user_required
from utils import generate_id


class BoostController:
    @staticmethod
    @user_required
    def add_boost():
        data = request.form
        idCommande = data.get('idCommande')
        if not idCommande:
            return jsonify({'error': 'idCommande requis'}), 400

        boost = Boost(
            idBoost=generate_id(),
            idUtilisateur=request.user.id,
            idCommande=idCommande,
            statut=BoostStatut.EN_COURS
        )
        db.session.add(boost)
        db.session.commit()

        return jsonify({
            'message': 'Boost ajouté',
            'idBoost': boost.idBoost
        }), 201