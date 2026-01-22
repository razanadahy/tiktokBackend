from flask import Blueprint
from controllers.cryptoController import CryptoController

crypto_bp = Blueprint('crypto', __name__, url_prefix='/api/crypto')

# List active cryptos
crypto_bp.route('', methods=['GET'])(CryptoController.list_cryptos)

# Admin: Add crypto
crypto_bp.route('/admin', methods=['POST'])(CryptoController.add_crypto)