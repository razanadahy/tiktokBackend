from flask import Blueprint
from controllers.balanceController import BalanceController

balance_bp = Blueprint('balance', __name__, url_prefix='/api/balance')

# Get balance for user
balance_bp.route('/<user_id>', methods=['GET'])(BalanceController.get_balance)

# Add transaction (recharge, retrait, gain)
balance_bp.route('/add/<user_id>', methods=['POST'])(BalanceController.add_transaction)

# User info + balance
balance_bp.route('/user/<user_id>', methods=['GET'])(BalanceController.get_user_balance_info)

# Total earnings (gains)
balance_bp.route('/earnings/<user_id>', methods=['GET'])(BalanceController.get_total_earnings)

# Withdrawal history (newest first)
balance_bp.route('/withdrawals/<user_id>', methods=['GET'])(BalanceController.get_withdrawal_history)

# Transaction history (last 30, newest first)
balance_bp.route('/history/<user_id>', methods=['GET'])(BalanceController.get_transaction_history)

balance_bp.route('/history', methods=['GET'])(BalanceController.get_all_transaction_history)