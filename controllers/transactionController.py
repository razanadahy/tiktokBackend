from flask import jsonify, request
from models import Transaction, TransactionStatus, Parrainage
from extension import db
from util.auth_utils import admin_required

class TransactionController:

    @staticmethod
    @admin_required
    def update_transaction(transaction_id):
        """Update transaction montant, status, or commentaire"""
        try:
            transaction = Transaction.query.filter_by(id=transaction_id).first()
            if not transaction:
                return jsonify({'error': 'Transaction not found'}), 404

            data = request.get_json()
            print(data['montant'])
            if 'montant' in data:
                transaction.montant = float(data['montant'])

            if 'status' in data:
                print(data['status'])
                # Assume status is string matching TransactionStatus values
                valid_statuses = [s.name for s in TransactionStatus]
                if data['status'] not in valid_statuses:
                    return jsonify({'error': f'Invalid status. Must be one of: {valid_statuses}'}), 400
                transaction.status = data['status']  # or TransactionStatus[data['status']]

            if 'commentaire' in data:
                transaction.commentaire = data['commentaire']

            db.session.commit()
            return jsonify({'message': 'Transaction updated successfully', 'transaction_id': transaction_id}), 200

        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

    @staticmethod
    @admin_required
    def update_parrainage(parrainage_id):
        """Update parrainage montant or statut"""
        try:
            parrainage = Parrainage.query.filter_by(idParainnage=parrainage_id).first()
            if not parrainage:
                return jsonify({'error': 'Parrainage not found'}), 404

            data = request.get_json()

            if 'montant' in data:
                parrainage.montant = float(data['montant'])
                print(data['montant'], data['status'])

            if 'status' in data:
                valid_statuses = [s.name for s in TransactionStatus]
                if data['status'] not in valid_statuses:
                    return jsonify({'error': f'Invalid statut. Must be one of: {valid_statuses}'}), 400
                parrainage.statut = data['status']

                # Update linked transaction status
                transaction = Transaction.query.filter_by(id=parrainage.idTransaction).first()
                if transaction:
                    transaction.status = data['status']
                    transaction.montant = float(data['montant'])

            db.session.commit()
            return jsonify({'message': 'Parrainage updated successfully', 'parrainage_id': parrainage_id}), 200

        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
