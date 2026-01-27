from flask import Blueprint
from controllers.transactionController import TransactionController

transactions_bp = Blueprint('transactions', __name__, url_prefix='/api/transactions')

# PUT /api/transactions/<id> - Update transaction
transactions_bp.route('/<transaction_id>', methods=['PUT'])(TransactionController.update_transaction)

# PUT /api/transactions/parrainage/<id> - Update parrainage
transactions_bp.route('/parrainage/<parrainage_id>', methods=['PUT'])(TransactionController.update_parrainage)
