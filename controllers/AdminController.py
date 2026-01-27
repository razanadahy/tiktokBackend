from flask import jsonify, request
from models import Admin, User, Boost, Transaction, TransactionStatus, Parrainage
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
    def get_dashboard_finance():
        """Get finance stats for today (recharge and retrait)"""
        try:
            from datetime import datetime, time
            from sqlalchemy import func

            # Get start of today
            today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

            # Query transactions for today, filter by recharge/retrait
            transactions = Transaction.query.filter(
                Transaction.date_transaction >= today_start,
                Transaction.action.in_(['recharge', 'retrait'])
            ).all()

            tx_data = []
            total_recharge = 0
            total_retrait = 0

            for tx in transactions:
                if tx.status == TransactionStatus.COMPLETED:
                    if tx.action == 'recharge':
                        total_recharge += float(tx.montant)
                    elif tx.action == 'retrait':
                        total_retrait += float(tx.montant)

                tx_data.append({
                    "id": tx.id,
                    "user": tx.user.nom if tx.user else "Unknown",
                    "idUser": tx.user.id if tx.user else "Unknown",
                    "type": tx.action,
                    "amount": float(tx.montant),
                    "date": tx.date_transaction.strftime('%Y-%m-%d %H:%M:%S'),
                    "status": tx.status.value if hasattr(tx.status, 'value') else str(tx.status)
                })

            return jsonify({
                "total_transaction": len(tx_data),
                "total_recharge": total_recharge,
                "total_retrait": total_retrait,
                "transactions": tx_data
            }), 200

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @staticmethod
    @admin_required
    def get_dashboard_boosts():
        """Get completed boosts for today"""
        try:
            from datetime import datetime
            from models import Commande

            # Get start of today
            today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

            # Query boosts that are completed and joined with Commande date today
            # The date to check is in Commande table
            boosts = Boost.query.filter(
                Boost.statut == BoostStatut.TERMINEE,
                Boost.date >= today_start
            ).all()

            boost_data = []

            for boost in boosts:
                boost_data.append({
                    "id": boost.idBoost,
                    "user": boost.user.nom if boost.user else "Unknown",
                    "commande_code": boost.commande.code if boost.commande else "Unknown",
                    "commission": float(boost.commande.commission_total) if (boost.commande and boost.commande.commission_total) else 0.0,
                    "date": boost.date.strftime('%Y-%m-%d %H:%M:%S')
                })

            return jsonify({
                "total_boosts": len(boost_data),
                "boosts": boost_data
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

    @staticmethod
    @admin_required
    def transaction_normal():
        try:
            transactions = Transaction.query.filter(
                Transaction.action.in_(['recharge', 'retrait'])
            ).order_by(Transaction.date_transaction.desc()).all()

            tx_data = []
            for tx in transactions:
                user = tx.user
                tx_data.append({
                    "idtransaction": tx.id,
                    "userId": tx.user_id,
                    "userName": user.nom if user else "Unknown",
                    "userEmail": user.email if user else "Unknown",
                    "date": tx.date_transaction.strftime('%Y-%m-%d %H:%M:%S'),
                    "type": tx.action,
                    "valeur": float(tx.montant),
                    "status": tx.status.value,
                    "proof_image": tx.image_filename,
                    "transaction_hash": tx.transaction_hash,
                    "sender_address": tx.sender_address,
                    "recipient_address": tx.recipient_address
                })

            return jsonify({
                "transactions": tx_data
            }), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @staticmethod
    @admin_required
    def transactionParrainage():
        try:
            parrainages = Parrainage.query.order_by(Parrainage.date.desc()).all()

            tx_data = []
            for p in parrainages:
                old_user = p.old_user
                tx_data.append({
                    "idtransaction": p.idParainnage,
                    "userId": p.idOldUser,
                    "userName": old_user.nom if old_user else "Unknown",
                    "userEmail": old_user.email if old_user else "Unknown",
                    "date": p.date.strftime('%Y-%m-%d %H:%M:%S') if p.date else None,
                    "type": "gain",
                    "valeur": float(p.montant),
                    "status": p.statut.value if hasattr(p.statut, 'value') else str(p.statut)
                })

            return jsonify({
                "transactions": tx_data
            }), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500