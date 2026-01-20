from flask import jsonify, request
from app import db
from models import User, Transaction
from datetime import datetime

class BalanceController:
    @staticmethod
    def get_balance(user_id):
        """Get user balance: recharges + gains - retraits"""
        recharges = db.session.query(db.func.sum(Transaction.montant)).filter(
            Transaction.user_id == user_id, Transaction.action == 'recharge'
        ).scalar() or 0
        retraits = db.session.query(db.func.sum(Transaction.montant)).filter(
            Transaction.user_id == user_id, Transaction.action == 'retrait'
        ).scalar() or 0
        gains = db.session.query(db.func.sum(Transaction.montant)).filter(
            Transaction.user_id == user_id, Transaction.action == 'gain'
        ).scalar() or 0
        balance = float(recharges) + float(gains) - float(retraits)
        return jsonify({'balance': balance}), 200

    @staticmethod
    def add_transaction(user_id):
        """Add transaction (recharge, retrait, gain)"""
        data = request.get_json()
        action = data.get('action')
        montant = data.get('montant')
        commentaire = data.get('commentaire')
        date_transaction = data.get('date_transaction', datetime.utcnow())

        if not action or montant is None:
            return jsonify({'error': 'Missing action or montant'}), 400

        transaction = Transaction(
            user_id=user_id,
            action=action,
            montant=montant,
            commentaire=commentaire,
            date_transaction=date_transaction
        )
        db.session.add(transaction)
        db.session.commit()
        return jsonify({
            'message': 'Transaction added',
            'transaction': {
                'id': transaction.id,
                'action': action,
                'montant': float(montant),
                'commentaire': commentaire,
                'date_transaction': transaction.date_transaction.isoformat()
            }
        }), 201

    @staticmethod
    def get_user_balance_info(user_id):
        """User info + balance"""
        user = User.query.filter_by(id=user_id).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404

        recharges = db.session.query(db.func.sum(Transaction.montant)).filter(
            Transaction.user_id == user_id, Transaction.action == 'recharge'
        ).scalar() or 0
        retraits = db.session.query(db.func.sum(Transaction.montant)).filter(
            Transaction.user_id == user_id, Transaction.action == 'retrait'
        ).scalar() or 0
        gains = db.session.query(db.func.sum(Transaction.montant)).filter(
            Transaction.user_id == user_id, Transaction.action == 'gain'
        ).scalar() or 0
        balance = float(recharges) + float(gains) - float(retraits)

        return jsonify({
            'user': {
                'id': user.id,
                'nom': user.nom,
                'email': user.email
            },
            'balance': balance
        }), 200

    @staticmethod
    def get_total_earnings(user_id):
        """Total earnings (gains)"""
        total = db.session.query(db.func.sum(Transaction.montant)).filter(
            Transaction.user_id == user_id, Transaction.action == 'gain'
        ).scalar() or 0
        return jsonify({'total_earnings': float(total)}), 200

    @staticmethod
    def get_withdrawal_history(user_id):
        """Withdrawal history, newest first"""
        withdrawals = Transaction.query.filter(
            Transaction.user_id == user_id, Transaction.action != 'gain'
        ).order_by(Transaction.date_transaction.desc()).all()

        history = []
        for t in withdrawals:
            history.append({
                'id': t.id,
                'montant': float(t.montant),
                'commentaire': t.commentaire,
                'date_transaction': t.date_transaction.isoformat()
            })
        return jsonify({'withdrawals': history}), 200

    @staticmethod
    def get_transaction_history(user_id):
        transactions = Transaction.query.filter(
            Transaction.user_id == user_id
        ).order_by(Transaction.date_transaction.desc()).limit(30).all()

        history = []
        for t in transactions:
            history.append({
                'id': t.id,
                'action': t.action,
                'montant': float(t.montant),
                'commentaire': t.commentaire,
                'date_transaction': t.date_transaction.isoformat()
            })
        return jsonify({'transactions': history}), 200

    @staticmethod
    def get_all_transaction_history():
        transactions = Transaction.query.order_by(Transaction.date_transaction.desc()).limit(30).all()
        history = []
        for t in transactions:
            history.append({
                'id': t.id,
                'action': t.action,
                'montant': float(t.montant),
                'commentaire': t.commentaire,
                'date_transaction': t.date_transaction.isoformat()
            })
        return jsonify({'transactions': history}), 200