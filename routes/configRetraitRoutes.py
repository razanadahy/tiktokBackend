from flask import Blueprint
from controllers.configRetraitController import ConfigRetraitController

configRetrait_bp = Blueprint('configRetrait', __name__, url_prefix='/api/config-retrait')

# Get config for user
configRetrait_bp.route('/<user_id>', methods=['GET'])(ConfigRetraitController.get_config)

# Add new config for user
configRetrait_bp.route('/<user_id>', methods=['POST'])(ConfigRetraitController.add_config)

# Update existing config for user
configRetrait_bp.route('/<user_id>', methods=['PUT'])(ConfigRetraitController.update_config)

# Delete config for user
configRetrait_bp.route('/<user_id>', methods=['DELETE'])(ConfigRetraitController.delete_config)
