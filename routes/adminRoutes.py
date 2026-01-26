from flask import Blueprint
from controllers.AdminController import AdminController
from util.auth_utils import admin_required

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

# Dashboard stats
admin_bp.route('/dashboard-stats', methods=['GET'])(AdminController.get_dashboard_stats)

# Admin profile (GET/PUT)
admin_bp.route('/profile', methods=['PUT'])(AdminController.update_profile)

