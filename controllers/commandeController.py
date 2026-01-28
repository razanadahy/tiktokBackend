from flask import jsonify, request
from extension import db
from models import Commande, CommandeStatut
import os
import uuid
import json
from werkzeug.utils import secure_filename
from utils import generate_id

class CommandeController:
    @staticmethod
    def add_commande():
        data = request.form
        description_commande = data.get('description_commande')
        code = data.get('code')
        commission_total = data.get('commission_total')
        cout = data.get('cout')
        tableauProduit_str = data.get('tableauProduit')

        if not all([description_commande, code, commission_total, cout, tableauProduit_str]):
            return jsonify({'error': 'Champs requis manquants'}), 400

        try:
            commission_total = float(commission_total)
            cout = float(cout)
            tableauProduit = json.loads(tableauProduit_str)
        except (ValueError, json.JSONDecodeError):
            return jsonify({'error': 'Données invalides (commission, cout, tableauProduit JSON)'}), 400

        # Vérifier code unique
        if Commande.query.filter_by(code=code).first():
            return jsonify({'error': 'Code commande déjà utilisé'}), 400

        # Upload image
        image = request.files.get('image')
        image_filename = None
        if image and image.filename != '':
            if not image.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                return jsonify({'error': 'Image doit être PNG, JPG ou JPEG'}), 400

            uploads_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
            os.makedirs(uploads_dir, exist_ok=True)
            filename = secure_filename(image.filename)
            image_filename = f"{uuid.uuid4().hex}_{filename}"
            image_path = os.path.join(uploads_dir, image_filename)
            image.save(image_path)
        else:
            return jsonify({'error': 'Image requise'}), 400

        # Créer commande
        commande = Commande(
            idCommande=generate_id(),
            description_commande=description_commande,
            code=code,
            commission_total=commission_total,
            cout=cout,
            tableauProduit=tableauProduit,
            statut=CommandeStatut.EN_ATTENTE,
            image=image_filename
        )
        db.session.add(commande)
        db.session.commit()

        return jsonify({
            'message': 'Commande créée avec succès',
            'commande': {
                'idCommande': commande.idCommande,
                'code': commande.code,
                'statut': commande.statut.value,
                'image': image_filename
            }
        }), 201
