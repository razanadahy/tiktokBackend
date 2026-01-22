from flask import Blueprint
from controllers.assetController import AssetController

asset_bp = Blueprint('assets', __name__, url_prefix='/api/assets')

# Serve uploaded files (images, proofs, etc.)
# GET /api/assets/uploads/proofs/filename.jpg
# GET /api/assets/uploads/any/path/to/file.ext
asset_bp.route('/uploads/<path:filename>', methods=['GET'])(AssetController.serve_uploaded_file)
