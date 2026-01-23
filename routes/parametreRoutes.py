from flask import Blueprint
from controllers.parametreController import ParametreController

parametre_bp = Blueprint('parametre', __name__, url_prefix='/api/parametres')

# Get user's parametre
parametre_bp.route('/user/<user_id>', methods=['GET'])(ParametreController.get_user_parametre)

# Update user's parametre
parametre_bp.route('/user/<user_id>', methods=['PUT'])(ParametreController.update_user_parametre)

# Update min retrait
parametre_bp.route('/min-retrait', methods=['PUT'])(ParametreController.update_min_retrait)
