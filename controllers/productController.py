import os
import uuid
import secrets
import json
from datetime import datetime
from flask import jsonify, request, current_app
from werkzeug.utils import secure_filename
from extension import db
from models import Revendeur, Produit, Commande, CommandeStatut, Boost, StatProduitBoost, StatProduitBoostStatut, StatProduitBoostTypePreuve, User
from util.auth_utils import admin_required
from utils import generate_id

class ProductController:
    @staticmethod
    @admin_required
    def get_all_revendeurs():
        """Get all revendeurs"""
        try:
            revendeurs = Revendeur.query.all()
            output = []
            for r in revendeurs:
                output.append({
                    'id': r.id,
                    'nom': r.nom,
                    'plateforme': r.plateforme
                })
            return jsonify({'revendeurs': output}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @staticmethod
    @admin_required
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
    @admin_required
    def update_revendeur(idRevendeur):
        """Update revendeur"""
        try:
            data = request.get_json()
            revendeur = Revendeur.query.filter_by(id=idRevendeur).first()
            if not revendeur:
                return jsonify({'error': 'Revendeur not found'}), 404

            if 'nom' in data:
                revendeur.nom = data['nom']
            if 'plateforme' in data:
                revendeur.plateforme = data['plateforme']

            db.session.commit()
            return jsonify({
                'message': 'Revendeur updated',
                'revendeur': {
                    'id': revendeur.id,
                    'nom': revendeur.nom,
                    'plateforme': revendeur.plateforme
                }
            }), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

    @staticmethod
    @admin_required
    def delete_revendeur(idRevendeur):
        """Delete revendeur"""
        try:
            revendeur = Revendeur.query.filter_by(id=idRevendeur).first()
            if not revendeur:
                return jsonify({'error': 'Revendeur not found'}), 404

            db.session.delete(revendeur)
            db.session.commit()
            return jsonify({'message': 'Revendeur deleted'}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

    @staticmethod
    @admin_required
    def create_produit():
        """Create produit with image upload"""
        try:
            # Handle multipart/form-data
            if 'image_produit' not in request.files:
                return jsonify({'error': 'Missing image_produit file'}), 400

            file = request.files['image_produit']
            if file.filename == '':
                return jsonify({'error': 'No selected file'}), 400

            # Get form data
            nom_produit = request.form.get('nom_produit')
            prix = request.form.get('prix')
            commission = request.form.get('commission')
            revendeur_id = request.form.get('revendeur_id')
            description_produit = request.form.get('description_produit')
            linkProduit = request.form.get('linkProduit')

            required = [nom_produit, prix, commission, revendeur_id]
            if not all(required):
                return jsonify({'error': 'Missing required fields (nom_produit, prix, commission, revendeur_id)'}), 400

            # Check revendeur exists
            revendeur = Revendeur.query.filter_by(id=revendeur_id).first()
            if not revendeur:
                return jsonify({'error': 'Revendeur not found'}), 404

            # Save file with UUID name
            filename = secure_filename(file.filename)
            file_ext = os.path.splitext(filename)[1]
            unique_filename = f"{uuid.uuid4()}{file_ext}"

            upload_folder = os.path.join(current_app.root_path, 'uploads')
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)

            file_path = os.path.join(upload_folder, unique_filename)
            file.save(file_path)

            produit = Produit(
                nom_produit=nom_produit,
                prix=prix,
                commission=commission,
                revendeur_id=revendeur_id,
                image_produit=unique_filename,
                description_produit=description_produit,
                linkProduit=linkProduit
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
                    'revendeur_id': produit.revendeur_id,
                    'image_produit': produit.image_produit,
                    'description_produit': produit.description_produit,
                    'linkProduit': produit.linkProduit
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
        """Top 5 produits by StatProduitBoost count with explicit joins"""
        try:
            from sqlalchemy import func, desc

            # Query with explicit join condition and proper aliasing
            query = db.session.query(
                Produit.idProduit,
                Produit.nom_produit,
                Produit.image_produit,
                Produit.prix,
                Produit.linkProduit,
                func.count(StatProduitBoost.idStatProduitBoost).label('boost_count')
            ).outerjoin(
                StatProduitBoost,
                Produit.idProduit == StatProduitBoost.idProduit
            ).group_by(
                Produit.idProduit
            ).order_by(
                desc('boost_count')
            ).limit(5)

            # Execute query
            results = query.all()

            # Format results with null safety
            top_products = []
            for row in results:
                top_products.append({
                    'idProduit': row.idProduit,
                    'nom_produit': row.nom_produit or 'N/A',
                    'image_produit': row.image_produit or '',
                    'prix': float(row.prix) if row.prix else 0.0,
                    'linkProduit': row.linkProduit or '',
                    'countStatProduitBoost': row.boost_count or 0
                })

            return jsonify({
                'success': True,
                'top_boosts': top_products,
                'total_found': len(top_products)
            }), 200

        except Exception as e:
            # Log the error for debugging
            current_app.logger.error(f"Error in get_top_boosts: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'An error occurred while fetching top boosts',
                'detail': str(e) if current_app.debug else None
            }), 500
        finally:
            # Ensure session is closed
            db.session.close()

    @staticmethod
    def get_all_produits_with_boost_count():
        """List all produits with their boost count"""
        try:
            from sqlalchemy import func, desc

            # Query all produits with boost count
            query = db.session.query(
                Produit.idProduit,
                Produit.nom_produit,
                Produit.image_produit,
                Produit.prix,
                Produit.linkProduit,
                Produit.description_produit,
                Produit.commission,
                Revendeur.nom.label('revendeur_nom'),
                Revendeur.plateforme.label('revendeur_plateforme'),
                func.count(StatProduitBoost.idStatProduitBoost).label('boost_count')
            ).outerjoin(
                StatProduitBoost,
                Produit.idProduit == StatProduitBoost.idProduit
            ).join(
                Revendeur,
                Produit.revendeur_id == Revendeur.id
            ).group_by(
                Produit.idProduit,
                Revendeur.nom
            ).order_by(
                desc('boost_count')
            )

            # Execute query
            results = query.all()

            # Format results with null safety
            produits_with_boost = []
            for row in results:
                produits_with_boost.append({
                    'idProduit': row.idProduit,
                    'nom_produit': row.nom_produit or 'N/A',
                    'description_produit': row.description_produit or '',
                    'image_produit': row.image_produit or '',
                    'prix': float(row.prix) if row.prix else 0.0,
                    'commission': float(row.commission) if row.commission else 0.0,
                    'linkProduit': row.linkProduit or '',
                    'revendeur': row.revendeur_nom if row.revendeur_nom else 'Unknown',
                    'boost_count': row.boost_count or 0,
                    'plateforme': row.revendeur_plateforme
                })

            return jsonify({
                'success': True,
                'produits': produits_with_boost,
                'total': len(produits_with_boost)
            }), 200

        except Exception as e:
            # Log the error for debugging
            current_app.logger.error(f"Error in get_all_produits_with_boost_count: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'An error occurred while fetching produits with boost count',
                'detail': str(e) if current_app.debug else None
            }), 500
        finally:
            # Ensure session is closed
            db.session.close()

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
