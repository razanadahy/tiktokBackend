from flask import jsonify, request
from app import db
from models import User, Transaction, TransactionStatus
from datetime import datetime
import os
import uuid
from werkzeug.utils import secure_filename

class BalanceController:
    @staticmethod
    def get_balance(user_id):
        """Get user balance: recharges + gains - retraits"""
        recharges = db.session.query(db.func.sum(Transaction.montant)).filter(
            Transaction.user_id == user_id, Transaction.action == 'recharge', Transaction.status == TransactionStatus.COMPLETED
        ).scalar() or 0
        retraits = db.session.query(db.func.sum(Transaction.montant)).filter(
            Transaction.user_id == user_id, Transaction.action == 'retrait', Transaction.status == TransactionStatus.COMPLETED
        ).scalar() or 0
        gains = db.session.query(db.func.sum(Transaction.montant)).filter(
            Transaction.user_id == user_id, Transaction.action == 'gain', Transaction.status == TransactionStatus.COMPLETED
        ).scalar() or 0
        balance = float(recharges) + float(gains) - float(retraits)
        return jsonify({'balance': balance}), 200

    @staticmethod
    def add_transaction(user_id):

        # Check if action is recharge
        data = request.form

        montant = data.get('montant')
        commentaire = data.get('commentaire')
        sender_address = data.get('sender_address')
        recipient_address = data.get('recipient_address')
        transaction_hash = data.get('transaction_hash')

        if not montant or float(montant) <= 0:
            return jsonify({'error': 'Valid montant required'}), 400

        if not all([sender_address, recipient_address, transaction_hash]):
            return jsonify({'error': 'sender_address, recipient_address, transaction_hash required'}), 400

        # Handle image upload
        image = request.files.get('image')
        if not image or image.filename == '':
            return jsonify({'error': 'Payment proof image required'}), 400

        if not image.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            return jsonify({'error': 'Image must be PNG, JPG, or JPEG'}), 400

        # Secure filename and save
        filename = secure_filename(image.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        upload_folder = 'uploads/proofs'
        os.makedirs(upload_folder, exist_ok=True)
        image_path = os.path.join(upload_folder, unique_filename)
        image.save(image_path)

        transaction = Transaction(
            user_id=user_id,
            action='recharge',
            montant=float(montant),
            commentaire=commentaire,
            sender_address=sender_address,
            recipient_address=recipient_address,
            transaction_hash=transaction_hash,
            image_filename=unique_filename,
            # status defaults to PENDING
        )
        db.session.add(transaction)
        db.session.commit()

        return jsonify({
            'message': 'Recharge transaction added (pending approval)',
            'transaction': {
                'id': transaction.id,
                'montant': float(montant),
                'commentaire': commentaire,
                'sender_address': sender_address,
                'recipient_address': recipient_address,
                'transaction_hash': transaction_hash,
                'image_filename': unique_filename,
                'status': transaction.status.value,
                'date_transaction': transaction.date_transaction.isoformat()
            }
        }), 201

    @staticmethod
    def add_gain(user_id):
        "\"\"Add gain transaction (minimal, status=completed)"""
        data = request.get_json()
        montant = data.get('montant')
        commentaire = data.get('commentaire')

        if not montant or float(montant) <= 0:
            return jsonify({'error': 'Valid montant required'}), 400

        transaction = Transaction(
            user_id=user_id,
            action='gain',
            montant=float(montant),
            commentaire=commentaire,
            status=TransactionStatus.COMPLETED
        )
        db.session.add(transaction)
        db.session.commit()
        return jsonify({'message': 'Gain added', 'transaction_id': transaction.id}), 201

    @staticmethod
    def add_retrait(user_id):
        "\"\"Add retrait transaction (minimal, status=completed)"""
        data = request.get_json()
        montant = data.get('montant')
        commentaire = data.get('commentaire')

        if not montant or float(montant) <= 0:
            return jsonify({'error': 'Valid montant required'}), 400

        transaction = Transaction(
            user_id=user_id,
            action='retrait',
            montant=float(montant),
            commentaire=commentaire,
            status=TransactionStatus.COMPLETED
        )
        db.session.add(transaction)
        db.session.commit()
        return jsonify({'message': 'Retrait added', 'transaction_id': transaction.id}), 201

    @staticmethod
    def get_user_balance_info(user_id):
        """User info + balance"""
        user = User.query.filter_by(id=user_id).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404

        recharges = db.session.query(db.func.sum(Transaction.montant)).filter(
            Transaction.user_id == user_id, Transaction.action == 'recharge', Transaction.status == TransactionStatus.COMPLETED
        ).scalar() or 0
        retraits = db.session.query(db.func.sum(Transaction.montant)).filter(
            Transaction.user_id == user_id, Transaction.action == 'retrait', Transaction.status == TransactionStatus.COMPLETED
        ).scalar() or 0
        gains = db.session.query(db.func.sum(Transaction.montant)).filter(
            Transaction.user_id == user_id, Transaction.action == 'gain', Transaction.status == TransactionStatus.COMPLETED
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
            Transaction.user_id == user_id, Transaction.action == 'gain', Transaction.status == TransactionStatus.COMPLETED
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