from flask import jsonify, request
from models import Admin
from extension import db
from util.auth_utils import admin_required

class AdminController:

    @staticmethod
    @admin_required
    def update_profile():
        """Update admin profile (email, password)"""
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Get admin by ID
        admin = Admin.query.first()
        if not admin:
            return jsonify({'error': 'Admin not found'}), 404

        # Validate current password
        current_password = data.get('current_password')
        if not current_password:
            return jsonify({'error': 'Current password is required'}), 400

        if not admin.check_password(current_password):
            return jsonify({'error': 'Current password is incorrect'}), 401

        # Update email if provided
        new_email = data.get('new_email')
        admin.email = new_email

        # Update password if provided
        new_password = data.get('new_password')
        if new_password:
            admin.mot_de_passe = new_password

        try:
            db.session.commit()
            return jsonify({
                'message': 'Profile updated successfully',
                'admin': {
                    'id': admin.id,
                    'email': admin.email
                }
            }), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

    @staticmethod
    @admin_required
    def update_admin_profile():
        """Update admin profile (email, password)"""
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Get authorization token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Admin authorization required'}), 401

        token = auth_header.split(' ')[1]
        import jwt
        from flask import current_app
        try:
            payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            admin_id = payload.get('id')
            admin = Admin.query.filter_by(id=admin_id).first()
            print("fdfdsfdsfd", admin, admin_id)
            if not admin:
                return jsonify({'error': 'Admin access denied'}), 403
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401

        # Validate current password
        current_password = data.get('current_password')
        if not current_password:
            return jsonify({'error': 'Current password is required'}), 400

        if not admin.check_password(current_password):
            return jsonify({'error': 'Current password is incorrect'}), 401

        # Update email if provided
        new_email = data.get('new_email')
        admin.email = new_email

        # Update password if provided
        new_password = data.get('new_password')
        if new_password:
            admin.mot_de_passe = new_password

        try:
            db.session.commit()
            return jsonify({
                'message': 'Profile updated successfully',
                'admin': {
                    'id': admin.id,
                    'email': admin.email
                }
            }), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500