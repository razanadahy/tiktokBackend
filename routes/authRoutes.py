from flask import Blueprint
from controllers.authController import AuthController

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# User login
auth_bp.route('/login/user', methods=['POST'])(AuthController.login_user)

# Admin login
auth_bp.route('/login/admin', methods=['POST'])(AuthController.login_admin)
