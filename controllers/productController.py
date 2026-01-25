from flask import jsonify, request
from extension import db
from models import Revendeur, Produit, Commande, CommandeStatut, Boost, StatProduitBoost, StatProduitBoostStatut, StatProduitBoostTypePreuve, User
from utils import generate_id
from datetime import datetime
import secrets
import json

class ProductController:
    @staticmethod
    def create_revendeur():
        """Create revendeur"""
        try:
            data = request.get_json()
            required = ['nom', 'plateforme']
            for field in required:
                if field not in data:
                    return jsonify({'error': f'Missing {field}'}), 400

            revendeur = Revendeur(
                nom=data['nom'],
                plateforme=data['plateforme']
            )
            db.session.add(revendeur)
            db.session.commit()
            return jsonify({
                'message': 'Revendeur created',
                'revendeur': {
                    'id': revendeur.id,
                    'nom': revendeur.nom,
                    'plateforme': revendeur.plateforme
                }
            }), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

    @staticmethod
    def create_produit():
        """Create produit"""
        try:
            data = request.get_json()
            required = ['nom_produit', 'prix', 'commission', 'revendeur_id']
            for field in required:
                if field not in data:
                    return jsonify({'error': f'Missing {field}'}), 400

            # Check revendeur exists
            revendeur = Revendeur.query.filter_by(id=data['revendeur_id']).first()
            if not revendeur:
                return jsonify({'error': 'Revendeur not found'}), 404

            produit = Produit(
                nom_produit=data['nom_produit'],
                prix=data['prix'],
                commission=data['commission'],
                revendeur_id=data['revendeur_id'],
                image_produit=data.get('image_produit'),
                linkProduit=data.get('linkProduit')
            )
            db.session.add(produit)
            db.session.commit()
            return jsonify({
                'message': 'Produit created',
                'produit': {
                    'idProduit': produit.idProduit,
                    'nom_produit': produit.nom_produit,
                    'prix': float(produit.prix),
                    'commission': float(produit.commission),
                    'revendeur_id': produit.revendeur_id
                }
            }), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

    @staticmethod
    def create_commande():
        """Create commande with code generation"""
        try:
            data = request.get_json()
            required = ['description_commande', 'tableauProduit', 'user_id']
            for field in required:
                if field not in data:
                    return jsonify({'error': f'Missing {field}'}), 400

            # Validate tableauProduit
            if not isinstance(data['tableauProduit'], list):
                return jsonify({'error': 'tableauProduit must be array'}), 400

            # Check user exists
            user = User.query.filter_by(id=data['user_id']).first()
            if not user:
                return jsonify({'error': 'User not found'}), 404

            # Generate code CMD-YYYY-MM-XXXX
            now = datetime.utcnow()
            serial = secrets.token_hex(4).upper()
            code = f"CMD-{now.year}-{now.month:02d}-{serial}"

            commande = Commande(
                description_commande=data['description_commande'],
                code=code,
                tableauProduit=data['tableauProduit'],
                user_id=data['user_id'],
                commission_total=data.get('commission_total'),
                cout=data.get('cout'),
                statut=CommandeStatut.EN_ATTENTE
            )
            db.session.add(commande)
            db.session.commit()
            return jsonify({
                'message': 'Commande created',
                'commande': {
                    'idCommande': commande.idCommande,
                    'code': commande.code,
                    'statut': commande.statut.value
                }
            }), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

    @staticmethod
    def create_boost():
        """Create boost with validation no 'en cours' stats"""
        try:
            data = request.get_json()
            required = ['idCommande', 'idUtilisateur']
            for field in required:
                if field not in data:
                    return jsonify({'error': f'Missing {field}'}), 400

            # Generate idBoost
            idBoost = generate_id()

            # Check no existing 'en cours' for this idBoost (should be none yet)
            en_cours_count = StatProduitBoost.query.filter(
                StatProduitBoost.idBoost == idBoost,
                StatProduitBoost.statut == StatProduitBoostStatut.EN_COURS
            ).count()
            if en_cours_count > 0:
                return jsonify({'error': 'Existing en cours stats for this boost'}), 400

            boost = Boost(
                idBoost=idBoost,
                idCommande=data['idCommande'],
                idUtilisateur=data['idUtilisateur']
            )
            db.session.add(boost)
            db.session.commit()  # Triggers auto-stats via event
            return jsonify({
                'message': 'Boost created with auto-stats',
                'boost': {'idBoost': idBoost}
            }), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

    @staticmethod
    def update_stat_produit_boost(idStat):
        """Update stat status/proof"""
        try:
            data = request.get_json()
            stat = StatProduitBoost.query.filter_by(idStatProduitBoost=idStat).first()
            if not stat:
                return jsonify({'error': 'Stat not found'}), 404

            if 'statut' in data:
                stat.statut = data['statut']
            if 'Preuve' in data:
                stat.Preuve = data['Preuve']
            if 'typePreuve' in data:
                stat.typePreuve = data['typePreuve']

            db.session.commit()
            return jsonify({'message': 'Stat updated'}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

    @staticmethod
    def get_produit(idProduit):
        """Get single produit by idProduit"""
        try:
            produit = Produit.query.filter_by(idProduit=idProduit).first()
            if not produit:
                return jsonify({'error': 'Produit not found'}), 404

            return jsonify({
                'produit': {
                    'idProduit': produit.idProduit,
                    'nom_produit': produit.nom_produit,
                    'description_produit': produit.description_produit,
                    'image_produit': produit.image_produit,
                    'prix': float(produit.prix),
                    'commission': float(produit.commission),
                    'linkProduit': produit.linkProduit,
                    'revendeur': {
                        'id': produit.revendeur.id,
                        'nom': produit.revendeur.nom,
                        'plateforme': produit.revendeur.plateforme
                    } if produit.revendeur else None
                }
            }), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @staticmethod
    def get_top_boosts():
        """Top 5 produits by StatProduitBoost count"""
        try:
            from sqlalchemy import func
            query = db.session.query(
                Produit.idProduit,
                Produit.nom_produit,
                Produit.image_produit,
                Produit.prix,
                Produit.linkProduit,
                func.count(StatProduitBoost.idStatProduitBoost).label('count')
            ).outerjoin(StatProduitBoost).group_by(Produit.idProduit).order_by(func.desc('count')).limit(5).all()

            top = []
            for row in query:
                top.append({
                    'idProduit': row.idProduit,
                    'nom_produit': row.nom_produit,
                    'image_produit': row.image_produit,
                    'prix': float(row.prix),
                    'countStatProduitBoost': row.count,
                    'linkProduit': row.linkProduit
                })
            return jsonify({'top_boosts': top}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @staticmethod
    def get_all_produits():
        try:
            produits = Produit.query.all()
            list_produits = []
            for p in produits:
                list_produits.append({
                    'idProduit': p.idProduit,
                    'nom_produit': p.nom_produit,
                    'description_produit': p.description_produit,
                    'image_produit': p.image_produit,
                    'prix': float(p.prix),
                    'commission': float(p.commission),
                    'linkProduit': p.linkProduit,
                    'revendeur': p.revendeur.nom if p.revendeur else None
                })
            return jsonify({'produits': list_produits}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500