from flask import Blueprint
from controllers.boostController import BoostController

boost_bp = Blueprint('boost', __name__, url_prefix='/api/boost')

# Ajouter un boost (POST multipart/form-data)
boost_bp.route('/add', methods=['POST'])(BoostController.add_boost)