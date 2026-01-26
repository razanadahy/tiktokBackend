from flask import jsonify, request
from models import Admin, User, Boost, Transaction, TransactionStatus
from extension import db
from util.auth_utils import admin_required
from models import BoostStatut

class AdminController:

    @staticmethod
    @admin_required
    def get_dashboard_stats():
        """Get dashboard statistics"""
        from sqlalchemy import func
        try:
            # Total users
            total_users = User.query.count()

            boosts_completed = Boost.query.filter(Boost.statut == BoostStatut.TERMINEE).count()

            # Recharge completed amount
            recharge_completed = db.session.query(func.sum(Transaction.montant)).filter(
                Transaction.action == 'recharge',
                Transaction.status == TransactionStatus.COMPLETED
            ).scalar() or 0

            # Retrait completed amount
            retrait_completed = db.session.query(func.sum(Transaction.montant)).filter(
                Transaction.action == 'retrait',
                Transaction.status == TransactionStatus.COMPLETED
            ).scalar() or 0

            return jsonify({
                'total_users': total_users,
                'boosts_completed': boosts_completed,
                'recharge_completed': float(recharge_completed),
                'retrait_completed': float(retrait_completed)
            }), 200

        except Exception as e:
            return jsonify({'error': str(e)}), 500

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