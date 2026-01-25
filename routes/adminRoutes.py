from flask import Blueprint
from controllers.AdminController import AdminController
from util.auth_utils import admin_required

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

# Admin profile (GET/PUT)
admin_bp.route('/profile', methods=['PUT'])(AdminController.update_profile)

