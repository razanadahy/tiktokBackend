from flask import Blueprint
from controllers.boostController import BoostController

boost_bp = Blueprint('boost', __name__, url_prefix='/api/boost')

# Ajouter un boost (POST multipart/form-data)
boost_bp.route('/add/<idCommande>', methods=['POST'])(BoostController.add_boost)

# Obtenir les détails d'un boost
boost_bp.route('/details/<idBoost>', methods=['GET'])(BoostController.get_boost_details)

# Route admin pour obtenir les détails d'un boost
boost_bp.route('/admin/details/<idBoost>', methods=['GET'])(BoostController.admin_get_boost_details)

# Obtenir tous les boosts
boost_bp.route('/all', methods=['GET'])(BoostController.get_all_boosts)

# Obtenir les boosts par statut
boost_bp.route('/status/<status>', methods=['GET'])(BoostController.get_boosts_by_status)

# Obtenir les détails d'une commande avec tous ses boosts
boost_bp.route('/commande/<idCommande>', methods=['GET'])(BoostController.get_commande_details)