from flask import Blueprint
from controllers.boostController import BoostController

boost_bp = Blueprint('boost', __name__, url_prefix='/api/boost')

# Ajouter un boost (POST multipart/form-data)
boost_bp.route('/add/<idCommande>', methods=['POST'])(BoostController.add_boost)

# Obtenir les détails d'un boost
boost_bp.route('/details/<idBoost>', methods=['GET'])(BoostController.get_boost_details)


# Obtenir tous les boosts
boost_bp.route('/all', methods=['GET'])(BoostController.get_all_boosts)

boost_bp.route('/user_boost', methods=['GET'])(BoostController.get_boosts_user)

# Obtenir les boosts par statut
boost_bp.route('/status/<status>', methods=['GET'])(BoostController.get_boosts_by_status)

# Obtenir les détails d'une commande avec tous ses boosts
boost_bp.route('/commande/<idCommande>', methods=['GET'])(BoostController.get_commande_details)

# Mettre à jour plusieurs StatProduitBoost
boost_bp.route('/update-stats/<idBoost>', methods=['POST'])(BoostController.update_stat_produit_boost)

# Ajouter une preuve sur un StatProduitBoost (lien ou screenshot)
boost_bp.route('/add-preuve', methods=['POST'])(BoostController.add_preuve_stat_produit_boost)