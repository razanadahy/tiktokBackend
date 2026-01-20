from flask import Blueprint
from controllers.qualificationController import QualificationController

qualification_bp = Blueprint('qualification', __name__, url_prefix='/api/qualifications')

# Get user's qualification
qualification_bp.route('/user/<user_id>', methods=['GET'])(QualificationController.get_user_qualification)

# Update user's qualification
qualification_bp.route('/user/<user_id>', methods=['PUT'])(QualificationController.update_user_qualification)
