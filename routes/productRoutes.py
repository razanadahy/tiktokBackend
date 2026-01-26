from flask import Blueprint
from controllers.productController import ProductController

product_bp = Blueprint('product', __name__, url_prefix='/api/products')

# Get all produits
product_bp.route('', methods=['GET'])(ProductController.get_all_produits)

# Get single produit
product_bp.route('/<idProduit>', methods=['GET'])(ProductController.get_produit)

# Get all revendeurs
product_bp.route('/revendeurs', methods=['GET'])(ProductController.get_all_revendeurs)

# Create revendeur
product_bp.route('/revendeur', methods=['POST'])(ProductController.create_revendeur)

# Update revendeur
product_bp.route('/revendeur/<idRevendeur>', methods=['PUT'])(ProductController.update_revendeur)

# Delete revendeur
product_bp.route('/revendeur/<idRevendeur>', methods=['DELETE'])(ProductController.delete_revendeur)

# Create produit
product_bp.route('/produit', methods=['POST'])(ProductController.create_produit)

# Create commande
product_bp.route('/commande', methods=['POST'])(ProductController.create_commande)

# Create boost
product_bp.route('/boost', methods=['POST'])(ProductController.create_boost)

# Update stat produit boost
product_bp.route('/stat/<idStat>', methods=['PUT'])(ProductController.update_stat_produit_boost)

# Top 5 produits by boosts
product_bp.route('/top-boosts', methods=['GET'])(ProductController.get_top_boosts)