from flask import jsonify, request

from controllers.userController import UserController
from extension import db
from models import Boost, BoostStatut, Commande, Transaction, TransactionStatus
from util.auth_utils import user_required
from utils import generate_id


class BoostController:
    @staticmethod
    @user_required
    def add_boost(idCommande):
        user_id = request.user.id

        if not idCommande:
            return jsonify({'error': 'idCommande required'}), 400

        # Get the command details
        commande = Commande.query.get(idCommande)
        if not commande:
            return jsonify({'error': 'Commande not found'}), 404

        # Get user balance

        current_balance = UserController.get_balance(user_id)

        # Check if user has sufficient balance
        command_cost = float(commande.cout)
        if command_cost > current_balance:
            return jsonify({'error': 'Insufficient balance'}), 400

        # Create system transaction (retrait)
        transaction_id = generate_id()
        transaction = Transaction(
            id=transaction_id,
            user_id=user_id,
            action='retrait',
            montant=command_cost,
            commentaire='system',
            status=TransactionStatus.PENDING
        )
        db.session.add(transaction)

        # Create the boost
        boost = Boost(
            idUtilisateur=user_id,
            idCommande=idCommande,
            statut=BoostStatut.A_VALIDE,
            transaction_id = transaction_id
        )
        db.session.add(boost)

        # Commit both transaction and boost
        db.session.commit()

        return jsonify({
            'message': 'Boost added successfully',
            'idBoost': boost.idBoost,
            'transaction_id': transaction_id
        }), 201

    @staticmethod
    def get_boosts_by_user(user_id):
        boosts = Boost.query.filter_by(idUtilisateur=user_id).all()
        result = []
        for boost in boosts:
            result.append({
                'idBoost': boost.idBoost,
                'idCommande': boost.idCommande,
                'statut': boost.statut.value,
                'dateCreation': boost.dateCreation.isoformat()
            })
        return jsonify(result), 200

    @staticmethod
    def update_boost_status(idBoost, new_status):
        boost = Boost.query.get(idBoost)
        if not boost:
            return jsonify({'error': 'Boost not found'}), 404

        if new_status not in BoostStatut._value2member_map_:
            return jsonify({'error': 'Invalid status'}), 400

        boost.statut = BoostStatut(new_status)
        db.session.commit()

        return jsonify({
            'message': 'Boost status updated successfully',
            'idBoost': boost.idBoost,
            'new_status': boost.statut.value
        }), 200

    @staticmethod
    def delete_boost(idBoost):
        boost = Boost.query.get(idBoost)
        if not boost:
            return jsonify({'error': 'Boost not found'}), 404

        db.session.delete(boost)
        db.session.commit()

        return jsonify({
            'message': 'Boost deleted successfully',
            'idBoost': idBoost
        }), 200
