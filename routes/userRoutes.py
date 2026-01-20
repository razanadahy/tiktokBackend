from flask import Blueprint
from controllers.userController import UserController

user_bp = Blueprint('user', __name__, url_prefix='/api/users')

# Create a new user
user_bp.route('', methods=['POST'])(UserController.create_user)

# Get all users
user_bp.route('', methods=['GET'])(UserController.get_all_users)

# Get a single user by ID
user_bp.route('/<user_id>', methods=['GET'])(UserController.get_user)

# Update a user
user_bp.route('/<user_id>', methods=['PUT'])(UserController.update_user)

# Delete a user
user_bp.route('/<user_id>', methods=['DELETE'])(UserController.delete_user)

# Change password
user_bp.route('/<user_id>/password', methods=['PUT'])(UserController.change_password)

# Get current user from token
user_bp.route('/me', methods=['GET'])(UserController.get_current_user)
