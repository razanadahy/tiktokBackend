from datetime import datetime

from flask import jsonify, request
from extension import db
from models import Commande, CommandeStatut, Produit, Revendeur
import os
import uuid
import json
from werkzeug.utils import secure_filename

from util.auth_utils import admin_required
from utils import generate_id

class CommandeController:
    @staticmethod
    @admin_required
    def add_commande():
        data = request.form
        description_commande = data.get('description_commande')
        code = data.get('code')
        commission_total = data.get('commission_total')
        cout = data.get('cout')
        tableauProduit_str = data.get('tableauProduit')
        date = data.get('date')

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
            image=image_filename,
            date=date
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

    @staticmethod
    def list_commandes():
        commandes = Commande.query.all()
        result = []
        for commande in commandes:
            # Fetch product details from DB using idProduits
            processed_produits = []
            if commande.tableauProduit:
                for prod_id in commande.tableauProduit:
                    produit = Produit.query.filter_by(idProduit=prod_id).first()
                    if produit:
                        processed_produits.append({
                            'id': produit.idProduit,
                            'name': produit.nom_produit,
                            'price': str(produit.prix)
                        })

            result.append({
                'idCommande': commande.idCommande,
                'description_commande': commande.description_commande,
                'code': commande.code,
                'commission_total': commande.commission_total,
                'cout': commande.cout,
                'tableauProduit': processed_produits,
                'statut': commande.statut.value,
                'image': commande.image,
                'date': commande.date
            })
        return jsonify({'commandes': result})

    @staticmethod
    @admin_required
    def update_commande(idCommande):
        commande = Commande.query.filter_by(idCommande=idCommande).first()
        if not commande:
            return jsonify({'error': 'Commande non trouvée'}), 404

        data = request.form

        # Champs optionnels
        description_commande = data.get('description_commande')
        if description_commande is not None:
            commande.description_commande = description_commande

        code = data.get('code')
        if code is not None:
            if code != commande.code and Commande.query.filter_by(code=code).first():
                return jsonify({'error': 'Code déjà utilisé'}), 400
            commande.code = code

        commission_total = data.get('commission_total')
        if commission_total is not None:
            try:
                commande.commission_total = float(commission_total)
            except ValueError:
                return jsonify({'error': 'commission_total invalide'}), 400

        cout = data.get('cout')
        if cout is not None:
            try:
                commande.cout = float(cout)
            except ValueError:
                return jsonify({'error': 'cout invalide'}), 400

        tableauProduit_str = data.get('tableauProduit')
        if tableauProduit_str is not None:
            try:
                tableauProduit_full = json.loads(tableauProduit_str)
                if isinstance(tableauProduit_full, list):
                    commande.tableauProduit = tableauProduit_full
            except (json.JSONDecodeError, ValueError):
                return jsonify({'error': 'tableauProduit invalide'}), 400

        # Image optionnelle
        image = request.files.get('image')

        if image and image.filename != '':
            if not image.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                return jsonify({'error': 'Image invalide'}), 400
            uploads_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
            os.makedirs(uploads_dir, exist_ok=True)
            if commande.image:
                old_path = os.path.join(uploads_dir, commande.image)
                if os.path.exists(old_path):
                    os.remove(old_path)
            filename = secure_filename(image.filename)
            image_filename = f"{uuid.uuid4().hex}_{filename}"
            image_path = os.path.join(uploads_dir, image_filename)
            image.save(image_path)
            commande.image = image_filename

        if data.get('date') != '':
            commande.date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        db.session.commit()
        return jsonify({
            'message': 'Commande mise à jour',
            'commande': {
                'idCommande': commande.idCommande,
                'code': commande.code,
                'statut': commande.statut.value if commande.statut else None,
                'image': commande.image
            }
        }), 200

    @staticmethod
    @admin_required
    def set_status_en_attente(idCommande):
        commande = Commande.query.filter_by(idCommande=idCommande).first()
        if not commande:
            return jsonify({'error': 'Commande non trouvée'}), 404

        commande.statut = CommandeStatut.COMPLETEE
        db.session.commit()

        return jsonify({
            'message': 'Statut changé en EN_ATTENTE',
            'idCommande': idCommande
        }), 200

    @staticmethod
    def get_commande_detail(idCommande):
        commande = Commande.query.filter_by(idCommande=idCommande).first()
        if not commande:
            return jsonify({'error': 'Commande non trouvée'}), 404

        # Produits complets
        produits = []
        if commande.tableauProduit:
            for prod_id in commande.tableauProduit:
                produit = Produit.query.filter_by(idProduit=prod_id).first()
                if produit:
                    produits.append({
                        'id': produit.idProduit,
                        'image': produit.image_produit,
                        'nom': produit.nom_produit,
                        'linkProduit': produit.linkProduit,
                        'prix': str(produit.prix)
                    })

        # Revendeur du premier produit
        revendeur = None
        if produits:
            first_prod_id = commande.tableauProduit[0]
            first_produit = Produit.query.filter_by(idProduit=first_prod_id).first()
            if first_produit and first_produit.revendeur:
                revendeur = {
                    'nom': first_produit.revendeur.nom,
                    'plateforme': first_produit.revendeur.plateforme
                }

        return jsonify({
            'commande': {
                'description_commande': commande.description_commande,
                'code': commande.code,
                'date': commande.date.isoformat() if commande.date else None,
                'cout': float(commande.cout) if commande.cout else None,
                'commission_total': float(commande.commission_total) if commande.commission_total else None,
                'statut': commande.statut.value if commande.statut else None,
                'image': commande.image
            },
            'produits': produits,
            'revendeur': revendeur
        })
