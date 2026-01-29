from flask import jsonify, request
from extension import db
from controllers.userController import UserController
from models import User, Transaction, TransactionStatus, MinRetrait, Parrainage
import os
import uuid
from werkzeug.utils import secure_filename

from util.auth_utils import admin_required
from utils import generate_id


class BalanceController:
    @staticmethod
    def get_balance(user_id):
        """Get user balance: recharges + gains - retraits"""
        recharges = db.session.query(db.func.sum(Transaction.montant)).filter(
            Transaction.user_id == user_id, Transaction.action == 'recharge', Transaction.status == TransactionStatus.COMPLETED
        ).scalar() or 0
        retraits = db.session.query(db.func.sum(Transaction.montant)).filter(
            Transaction.user_id == user_id, Transaction.action == 'retrait', Transaction.status != TransactionStatus.FAILED
        ).scalar() or 0
        gains = db.session.query(db.func.sum(Transaction.montant)).filter(
            Transaction.user_id == user_id, Transaction.action == 'gain', Transaction.status == TransactionStatus.COMPLETED
        ).scalar() or 0
        balance = float(recharges) + float(gains) - float(retraits)
        return jsonify({'balance': balance}), 200

    @staticmethod
    def add_gain(user_id, montant, commentaire, idNewUser):
        try:
            generatedID= generate_id()
            transaction = Transaction(
                id = generatedID,
                user_id=user_id,
                action='gain',
                montant=float(montant),
                commentaire=commentaire,
                status=TransactionStatus.PENDING
            )
            db.session.add(transaction)
            parrainage = Parrainage(
                idTransaction = generatedID,
                idNewUser = idNewUser,
                idOldUser = user_id,
                montant=  montant
            )
            db.session.add(parrainage)
            db.session.commit()
            return True
        except:
            pass
            return False

    @staticmethod
    def add_transaction(user_id): #recharge transaction

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
        log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
        os.makedirs(log_dir, exist_ok=True)
        filename = secure_filename(image.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"

        image_path = os.path.join(log_dir, unique_filename)
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

        user = User.query.filter_by(id=user_id).first()
        if user.code_parrainage:
            BalanceController.add_gain(user.code_parrainage, 0.1*float(montant), "Parrainage", user_id)

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
    def tapitraProduit(user_id):
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
        commentaire = "User Withdrawal"
        mdp = data.get('mdp')

        minRetrait = MinRetrait.query.first()

        dat = minRetrait.montant_min
        if not minRetrait.montant_min:
            dat = 1

        if not montant or float(montant) < dat or float(montant) > UserController.get_balance(user_id):
            return jsonify({'error': 'Valid montant required'}), 400

        if UserController.check_realPass(user_id, mdp):
            transaction = Transaction(
                user_id=user_id,
                action='retrait',
                montant=float(montant),
                commentaire=commentaire,
                status=TransactionStatus.PENDING
            )
            db.session.add(transaction)
            db.session.commit()
            return jsonify({'message': 'Retrait added', 'transaction_id': transaction.id}), 201

        return jsonify({'error': f'Missing required field'}), 400

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
            Transaction.user_id == user_id, Transaction.action == 'retrait', Transaction.status != TransactionStatus.FAILED
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
            Transaction.user_id == user_id, Transaction.action == 'retrait'
        ).order_by(Transaction.date_transaction.desc()).all()

        history = []
        for t in withdrawals:
            history.append({
                'id': t.id,
                'montant': float(t.montant),
                'commentaire': t.commentaire,
                'date_transaction': t.date_transaction.isoformat(),
                'status': t.status.value,
                'action': t.action,
            })
        return jsonify({'withdrawals': history}), 200

    @staticmethod
    def get_transaction_history(user_id):
        transactions = Transaction.query.filter(
            Transaction.user_id == user_id
        ).order_by(Transaction.date_transaction.desc()).all()

        history = []
        for t in transactions:
            history.append({
                'id': t.id,
                'action': t.action,
                'montant': float(t.montant),
                'commentaire': t.commentaire,
                'date_transaction': t.date_transaction.isoformat(),
                'status': t.status.value
            })
        return jsonify({'transactions': history}), 200

    @staticmethod
    def get_all_transaction_history():
        transactions = Transaction.query.filter(
            Transaction.status == TransactionStatus.COMPLETED
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
    @admin_required
    def get_all_pending_transactions():
        """Get all pending transactions (newest first)"""
        transactions = Transaction.query.filter(
            Transaction.status == TransactionStatus.PENDING
        ).order_by(Transaction.date_transaction.desc()).all()
        history = []
        for t in transactions:
            history.append({
                'id': t.id,
                'user_id': t.user_id,
                'action': t.action,
                'montant': float(t.montant),
                'commentaire': t.commentaire,
                'date_transaction': t.date_transaction.isoformat(),
                'image_filename': t.image_filename
            })
        return jsonify({'transactions': history}), 200


    @staticmethod
    def get_transaction_details(transaction_id):
        """Get detailed transaction info including image URL"""
        transaction = Transaction.query.filter_by(id=transaction_id).first()
        if not transaction:
            return jsonify({'error': 'Transaction not found'}), 404

        # Generate image URL if image exists
        image_url = None
        if transaction.image_filename:
            image_url = f"/api/assets/uploads/proofs/{transaction.image_filename}"

        return jsonify({
            'transaction': {
                'id': transaction.id,
                'user_id': transaction.user_id,
                'action': transaction.action,
                'montant': float(transaction.montant),
                'commentaire': transaction.commentaire,
                'sender_address': transaction.sender_address,
                'recipient_address': transaction.recipient_address,
                'transaction_hash': transaction.transaction_hash,
                'image_filename': transaction.image_filename,
                'image_url': image_url,
                'status': transaction.status.value,
                'date_transaction': transaction.date_transaction.isoformat()
            }
        }), 200

    @staticmethod
    @admin_required
    def add_recharge(user_id):
        """Add direct recharge transaction (status=COMPLETED, no proof, minimal fields)"""
        data = request.get_json()
        montant = data.get('montant')
        commentaire = data.get('commentaire')

        if not montant or float(montant) <= 0:
            return jsonify({'error': 'Valid montant required'}), 400

        transaction = Transaction(
            user_id=user_id,
            action='recharge',
            montant=float(montant),
            commentaire=commentaire,
            status=TransactionStatus.COMPLETED
        )
        db.session.add(transaction)
        db.session.commit()

        return jsonify({'message': 'Recharge added successfully (completed)', 'transaction_id': transaction.id}), 201


    @staticmethod
    def getParainnage(user_id):
        parrainages = Parrainage.query.filter_by(idOldUser=user_id).all()

        result = []
        for parrainage in parrainages:
            if parrainage.new_user:
                result.append({
                    'id': parrainage.idParainnage,
                    'idNewUser': parrainage.idNewUser,
                    'nom': parrainage.new_user.nom,
                    'email': parrainage.new_user.email,
                    'montant': float(parrainage.montant),
                    'statut': parrainage.statut.value,
                    'date': parrainage.date.isoformat() if parrainage.date else None,
                    'idTransaction': parrainage.idTransaction
                })

        return jsonify({'parrainages': result}), 200