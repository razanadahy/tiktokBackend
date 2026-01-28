from flask import Blueprint
from controllers.commandeController import CommandeController

commande_bp = Blueprint('commande', __name__, url_prefix='/api/commande')

# Ajouter une commande (POST multipart/form-data)
commande_bp.route('/add', methods=['POST'])(CommandeController.add_commande)

# Lister les commandes (GET)
commande_bp.route('', methods=['GET'])(CommandeController.list_commandes)

# Update commande (POST multipart/form-data)
commande_bp.route('/update/<idCommande>', methods=['POST'])(CommandeController.update_commande)

# Set statut EN_ATTENTE (POST)
commande_bp.route('/status/<idCommande>', methods=['PUT'])(CommandeController.set_status_en_attente)

# Détail commande (GET)
commande_bp.route('/<idCommande>', methods=['GET'])(CommandeController.get_commande_detail)
