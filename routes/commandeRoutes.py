from flask import Blueprint
from controllers.commandeController import CommandeController

commande_bp = Blueprint('commande', __name__, url_prefix='/api/commande')

# Ajouter une commande (POST multipart/form-data)
commande_bp.route('/add', methods=['POST'])(CommandeController.add_commande)
