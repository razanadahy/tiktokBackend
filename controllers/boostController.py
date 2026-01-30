import os
from flask import jsonify, request, current_app
from werkzeug.utils import secure_filename

from controllers.userController import UserController
from extension import db
from models import Boost, BoostStatut, Commande, Transaction, TransactionStatus, StatProduitBoost, \
    StatProduitBoostTypePreuve, StatProduitBoostStatut
from util.auth_utils import user_required, admin_required
from utils import generate_id


class BoostController:
    @staticmethod
    @user_required
    def add_boost(idCommande):
        user_id = request.user.id

        if not idCommande:
            return jsonify({'error': 'idCommande required'}), 400

        # Get the command details
        commande = Commande.query.get(idCommande)
        if not commande:
            return jsonify({'error': 'Commande not found'}), 404

        # Get user balance

        current_balance = UserController.get_balance(user_id)

        # Check if user has sufficient balance
        command_cost = float(commande.cout)
        if command_cost > current_balance:
            return jsonify({'error': 'Insufficient balance'}), 400

        # Create system transaction (retrait)
        transaction_id = generate_id()
        transaction = Transaction(
            id=transaction_id,
            user_id=user_id,
            action='retrait',
            montant=command_cost,
            commentaire='system',
            status=TransactionStatus.PENDING
        )
        db.session.add(transaction)

        # Create the boost
        boost = Boost(
            idUtilisateur=user_id,
            idCommande=idCommande,
            statut=BoostStatut.A_VALIDE,
            transaction_id = transaction_id
        )
        db.session.add(boost)

        # Commit both transaction and boost
        db.session.commit()

        return jsonify({
            'message': 'Boost added successfully',
            'idBoost': boost.idBoost,
            'transaction_id': transaction_id
        }), 201

    @staticmethod
    def get_boosts_by_user(user_id):
        boosts = Boost.query.filter_by(idUtilisateur=user_id).all()
        result = []
        for boost in boosts:
            result.append({
                'idBoost': boost.idBoost,
                'idCommande': boost.idCommande,
                'statut': boost.statut.value,
                'dateCreation': boost.dateCreation.isoformat()
            })
        return jsonify(result), 200

    @staticmethod
    def update_boost_status(idBoost, new_status):
        boost = Boost.query.get(idBoost)
        if not boost:
            return jsonify({'error': 'Boost not found'}), 404

        if new_status not in BoostStatut._value2member_map_:
            return jsonify({'error': 'Invalid status'}), 400

        boost.statut = BoostStatut(new_status)
        db.session.commit()

        return jsonify({
            'message': 'Boost status updated successfully',
            'idBoost': boost.idBoost,
            'new_status': boost.statut.value
        }), 200

    @staticmethod
    def delete_boost(idBoost):
        boost = Boost.query.get(idBoost)
        if not boost:
            return jsonify({'error': 'Boost not found'}), 404

        db.session.delete(boost)
        db.session.commit()

        return jsonify({
            'message': 'Boost deleted successfully',
            'idBoost': idBoost
        }), 200

    @staticmethod
    def get_boost_details(idBoost):
        boost = Boost.query.get(idBoost)
        if not boost:
            return jsonify({'error': 'Boost not found'}), 404

        # Get user info
        user = boost.user
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Get command info
        commande = boost.commande
        if not commande:
            return jsonify({'error': 'Commande not found'}), 404

        # Build statProduitBoost array
        stat_produits = []
        for stat in boost.stats:
            produit = stat.produit
            if produit:
                stat_produits.append({
                    'idProduit': produit.idProduit,
                    'cout': float(stat.cout),
                    'commission': float(stat.commission),
                    'nomProduit': produit.nom_produit,
                    'idStat': stat.idStatProduitBoost,
                    'image': produit.image_produit,
                    'prix': produit.prix,
                    'lien': produit.linkProduit,
                    'statut' : stat.statut.value,
                })

        return jsonify({
            'idBoost': boost.idBoost,
            'user': {
                'nom': user.nom,
                'email': user.email
            },
            'date': boost.date.isoformat(),
            'idCommande': boost.idCommande,
            'statProduitBoost': stat_produits,
            'code': commande.code,
            "title": commande.description_commande,
        }), 200

    @staticmethod
    @admin_required
    def get_all_boosts():
        boosts = Boost.query.filter(Boost.statut.in_([BoostStatut.A_VALIDE, BoostStatut.EN_COURS])).all()
        results = []

        for boost in boosts:
            user = boost.user
            commande = boost.commande

            # Build statProduitBoost array
            stat_produits = []
            for stat in boost.stats:
                produit = stat.produit
                if produit:
                    stat_produits.append({
                        'idProduit': produit.idProduit,
                        'cout': float(stat.cout),
                        'commission': float(stat.commission),
                        'nomProduit': produit.nom_produit,
                        'idStat': stat.idStatProduitBoost,
                    })

            results.append({
                'idBoost': boost.idBoost,
                'user': {
                    'nom': user.nom if user else 'Unknown',
                    'email': user.email if user else 'Unknown',
                    'id': user.id if user else 'Unknown'
                },
                'date': boost.date.isoformat(),
                'idCommande': boost.idCommande,
                'code': commande.code,
                'prixCommande': commande.cout,
                'commission': commande.commission_total,
                'statProduitBoost': stat_produits,
                'statut': boost.statut.value
            })

        return jsonify(results), 200

    @staticmethod
    def get_boosts_by_status(status):
        if status not in [s.value for s in BoostStatut]:
            return jsonify({'error': 'Invalid status'}), 400

        boosts = Boost.query.filter_by(statut=BoostStatut(status)).all()
        results = []

        for boost in boosts:
            user = boost.user
            commande = boost.commande

            # Build statProduitBoost array
            stat_produits = []
            for stat in boost.stats:
                produit = stat.produit
                if produit:
                    stat_produits.append({
                        'idProduit': produit.idProduit,
                        'cout': float(stat.cout),
                        'commission': float(stat.commission),
                        'nomProduit': produit.nom_produit
                    })

            results.append({
                'idBoost': boost.idBoost,
                'user': {
                    'nom': user.nom if user else 'Unknown',
                    'email': user.email if user else 'Unknown'
                },
                'date': boost.date.isoformat(),
                'idCommande': boost.idCommande,
                'statProduitBoost': stat_produits
            })

        return jsonify(results), 200

    @staticmethod
    def get_commande_details(idCommande):
        commande = Commande.query.get(idCommande)
        if not commande:
            return jsonify({'error': 'Commande not found'}), 404

        # Get all boosts for this commande
        boosts = Boost.query.filter_by(idCommande=idCommande).all()
        boost_results = []

        for boost in boosts:
            user = boost.user

            # Build statProduitBoost array
            stat_produits = []
            for stat in boost.stats:
                produit = stat.produit
                if produit:
                    stat_produits.append({
                        'idProduit': produit.idProduit,
                        'cout': float(stat.cout),
                        'commission': float(stat.commission),
                        'nomProduit': produit.nom_produit
                    })

            boost_results.append({
                'idBoost': boost.idBoost,
                'nom': user.nom if user else 'Unknown',
                'email': user.email if user else 'Unknown',
                'date': boost.date.isoformat(),
                'statProduitBoost': stat_produits
            })

        return jsonify({
            'idCommande': commande.idCommande,
            'code': commande.code,
            'date': commande.date.isoformat(),
            'commission_total': float(commande.commission_total) if commande.commission_total else 0,
            'cout': float(commande.cout) if commande.cout else 0,
            'boosts': boost_results
        }), 200

    @staticmethod
    @admin_required
    def update_stat_produit_boost(idBoost):
        """Update multiple stat produit boost entries"""
        try:
            data = request.get_json()

            if not isinstance(data, list):
                return jsonify({'error': 'Request body must be an array'}), 400

            if not data:
                return jsonify({'error': 'No data provided'}), 400
            boost = Boost.query.get(idBoost)
            if boost.statut==BoostStatut.A_VALIDE:
                boost.statut = BoostStatut.EN_COURS
                trans = Transaction.query.get(boost.transaction_id)
                if trans:
                    trans.status = TransactionStatus.COMPLETED

            updated_stats = []
            errors = []

            for item in data:
                id_stat = item.get('idStat')
                if not id_stat:
                    errors.append(f'Missing idStat for item')
                    continue

                stat = StatProduitBoost.query.get(id_stat)
                if not stat:
                    errors.append(f'Stat with id {id_stat} not found')
                    continue

                # Update cost
                if 'cost' in item:
                    stat.cout = item['cost']

                # Update commission
                if 'commission' in item:
                    stat.commission = item['commission']

                updated_stats.append({
                    'idStat': stat.idStatProduitBoost,
                    'cout': float(stat.cout),
                    'commission': float(stat.commission),
                })

            if errors:
                db.session.rollback()
                return jsonify({
                    'error': 'Some updates failed',
                    'details': errors
                }), 400

            db.session.commit()

            return jsonify({
                'success': True,
                'updated': len(updated_stats),
                'stats': updated_stats
            }), 200

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating stat produit boost: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Failed to update stats',
                'detail': str(e) if current_app.debug else None
            }), 500
        finally:
            db.session.close()

    @staticmethod
    @user_required
    def get_boosts_user():
        user_id = request.user.id
        boosts = Boost.query.filter_by(idUtilisateur = user_id).all()
        results = []

        for boost in boosts:
            user = boost.user
            commande = boost.commande

            # Build statProduitBoost array
            stat_produits = []
            totalPrix=0
            for stat in boost.stats:
                produit = stat.produit
                if produit:
                    stat_produits.append({
                        'idProduit': produit.idProduit,
                        'cout': float(stat.cout),
                        'commission': float(stat.commission),
                        'nomProduit': produit.nom_produit,
                        'idStat': stat.idStatProduitBoost,
                    })
                    totalPrix+=float(stat.commission)

            results.append({
                'idBoost': boost.idBoost,
                'user': {
                    'nom': user.nom if user else 'Unknown',
                    'email': user.email if user else 'Unknown',
                    'id': user.id if user else 'Unknown'
                },
                'date': boost.date.isoformat(),
                'idCommande': boost.idCommande,
                'code': commande.code,
                "title": commande.description_commande,
                'prixCommande': commande.cout,
                'commission': commande.commission_total if boost.statut in [BoostStatut.A_VALIDE, BoostStatut.EN_COURS] or totalPrix == 0 else totalPrix,
                'statProduitBoost': stat_produits,
                'statut': boost.statut.value,
            })

        return jsonify(results), 200

    @staticmethod
    @user_required
    def add_preuve_stat_produit_boost():
        try:
            id_stat = request.form.get('idStatProduitBoost')
            preuve = request.form.get('Preuve')
            type_preuve = request.form.get('typePreuve')

            if not id_stat:
                return jsonify({'error': 'idStatProduitBoost est requis'}), 400
            if not type_preuve:
                return jsonify({'error': 'typePreuve est requis'}), 400

            # Vérifier que le typePreuve est valide
            if type_preuve not in ['lien', 'screenshot']:
                return jsonify({'error': 'typePreuve doit être "lien" ou "screenshot"'}), 400

            # Récupérer le stat produit boost
            stat = StatProduitBoost.query.get(id_stat)
            if not stat:
                return jsonify({'error': 'StatProduitBoost non trouvé'}), 404

            user_id = request.user.id
            boost = stat.boost
            if boost.idUtilisateur != user_id:
                return jsonify({'error': 'Accès non autorisé'}), 403

            preuve_value = None

            if type_preuve == 'lien':
                if not preuve:
                    return jsonify({'error': 'Preuve (lien) est requise'}), 400
                preuve_value = preuve

            elif type_preuve == 'screenshot':
                if 'Preuve' not in request.files:
                    return jsonify({'error': 'Fichier screenshot est requis'}), 400

                file = request.files['Preuve']
                if file.filename == '':
                    return jsonify({'error': 'Aucun fichier sélectionné'}), 400

                # Créer le dossier uploads s'il n'existe pas
                uploads_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
                os.makedirs(uploads_dir, exist_ok=True)

                # Sauvegarder le fichier avec un nom sécurisé
                filename = secure_filename(file.filename)
                unique_filename = f"{generate_id()}_{filename}"
                file_path = os.path.join(uploads_dir, unique_filename)
                file.save(file_path)

                preuve_value = unique_filename

            # Mettre à jour le stat produit boost
            stat.Preuve = preuve_value
            stat.typePreuve = StatProduitBoostTypePreuve(type_preuve)
            stat.statut = StatProduitBoostStatut.TERMINEE
            stats_termines = [s for s in boost.stats if s.statut == StatProduitBoostStatut.TERMINEE]
            # print(len(stats_termines))
            # # if boostsCountProduitFinished == len (boost.stats):
            # print(len (boost.stats)) #je veux avoir la taille de stats qui a un statut terminé
            if len(stats_termines) >= len (boost.stats):
                boost.statut = BoostStatut.EN_ATTENTE
            db.session.commit()

            return jsonify({
                'success': True,
                'message': 'Preuve ajoutée avec succès',
                'idStatProduitBoost': stat.idStatProduitBoost,
                'typePreuve': type_preuve,
                'Preuve': preuve_value
            }), 200

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Erreur lors de l'ajout de la preuve: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Échec de l\'ajout de la preuve',
                'detail': str(e) if current_app.debug else None
            }), 500
        finally:
            db.session.close()
