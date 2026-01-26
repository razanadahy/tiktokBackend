from flask import Blueprint
from controllers.cryptoController import CryptoController

crypto_bp = Blueprint('crypto', __name__, url_prefix='/api/crypto')

# List active cryptos
crypto_bp.route('', methods=['GET'])(CryptoController.list_cryptos)

# Admin: Add crypto
crypto_bp.route('/admin', methods=['POST'])(CryptoController.add_crypto)

# Get crypto by ID
crypto_bp.route('/<int:id>', methods=['GET'])(CryptoController.get_crypto)

# Admin: Update crypto
crypto_bp.route('/admin/<int:id>', methods=['PUT'])(CryptoController.update_crypto)

# Admin: Delete crypto (logical)
crypto_bp.route('/admin/<int:id>', methods=['DELETE'])(CryptoController.delete_crypto)