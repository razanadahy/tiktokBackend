from extension import db, bcrypt
from datetime import datetime
import enum
from utils import generate_id
from sqlalchemy import event


class QualificationValue(enum.Enum):
    DEBUTANT = 0
    VALIDER = 1
    VIP_1 = 2
    VIP_2 = 3
    VIP_3 = 4
    VIP_4 = 5


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.String(12), primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    mot_de_passe = db.Column(db.String(255), nullable=False)
    code_parrainage = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship to UtilisateurQualification
    qualification = db.relationship('UtilisateurQualification', back_populates='user', uselist=False)

    def __init__(self, nom, email, mot_de_passe, code_parrainage=None):
        self.nom = nom
        self.email = email
        self.mot_de_passe = bcrypt.generate_password_hash(mot_de_passe).decode('utf-8')
        self.code_parrainage = code_parrainage

    def check_password(self, password):
        return bcrypt.check_password_hash(self.mot_de_passe, password)

    def __repr__(self):
        return f'<User {self.nom}>'


class Admin(db.Model):
    __tablename__ = 'admins'

    id = db.Column(db.String(12), primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    mot_de_passe = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, email, mot_de_passe):
        self.email = email
        self.mot_de_passe = bcrypt.generate_password_hash(mot_de_passe).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.mot_de_passe, password)

    def __repr__(self):
        return f'<Admin {self.email}>'


class Qualification(db.Model):
    __tablename__ = 'qualifications'

    id = db.Column(db.String(12), primary_key=True)
    valeur = db.Column(db.Integer, unique=True, nullable=False)
    nom = db.Column(db.String(50), nullable=False)

    def __init__(self, valeur, nom):
        self.valeur = valeur
        self.nom = nom

    def __repr__(self):
        return f'<Qualification {self.nom}>'


class UtilisateurQualification(db.Model):
    __tablename__ = 'utilisateur_qualifications'

    id = db.Column(db.String(12), primary_key=True)
    id_utilisateur = db.Column(db.String(12), db.ForeignKey('users.id'), nullable=False)
    id_qualification = db.Column(db.String(12), db.ForeignKey('qualifications.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', back_populates='qualification')
    qualification = db.relationship('Qualification')

    def __repr__(self):
        return f'<UtilisateurQualification user={self.id_utilisateur} qualif={self.id_qualification}>'


class Parametre(db.Model):
    __tablename__ = 'parametres'

    id = db.Column(db.String(12), primary_key=True)
    id_utilisateur = db.Column(db.String(12), db.ForeignKey('users.id'), nullable=False, unique=True)
    langue = db.Column(db.String(10), nullable=False, default='ANG')
    devise = db.Column(db.String(10), nullable=False, default='DOLLAR')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    user = db.relationship('User', backref='parametre')

    def __init__(self, id_utilisateur, langue='ANG', devise='DOLLAR'):
        self.id_utilisateur = id_utilisateur
        self.langue = langue
        self.devise = devise

    def __repr__(self):
        return f'<Parametre user={self.id_utilisateur} langue={self.langue} devise={self.devise}>'


class TransactionStatus(enum.Enum):
    PENDING = 'pending'
    FAILED = 'failed'
    COMPLETED = 'completed'

class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.String(12), primary_key=True)
    user_id = db.Column(db.String(12), db.ForeignKey('users.id'), nullable=False)
    date_transaction = db.Column(db.DateTime, default=datetime.utcnow)
    action = db.Column(db.String(20), nullable=False)  # recharge, retrait, gain
    montant = db.Column(db.Numeric(10, 2), nullable=False)
    commentaire = db.Column(db.String(255), nullable=True)
    status = db.Column(db.Enum(TransactionStatus), default=TransactionStatus.PENDING, nullable=False)
    sender_address = db.Column(db.String(255), nullable=True)
    recipient_address = db.Column(db.String(255), nullable=True)
    transaction_hash = db.Column(db.String(100), nullable=True)
    image_filename = db.Column(db.String(255), nullable=True)

    user = db.relationship('User', backref='transactions')

    def __repr__(self):
        return f'<Transaction {self.action} {self.montant} for user {self.user_id}>'

class Revendeur(db.Model):
    __tablename__ = 'revendeurs'

    id = db.Column(db.String(12), primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    plateforme = db.Column(db.String(100), nullable=False)
    produits = db.relationship('Produit', back_populates='revendeur')

    def __repr__(self):
        return f'<Revendeur {self.nom}>'

class Produit(db.Model):
    __tablename__ = 'produits'

    idProduit = db.Column(db.String(12), primary_key=True)
    image_produit = db.Column(db.String(500))
    nom_produit = db.Column(db.String(255), nullable=False)
    prix = db.Column(db.Numeric(10,2), nullable=False)
    commission = db.Column(db.Numeric(10,2), nullable=False)
    revendeur_id = db.Column(db.String(12), db.ForeignKey('revendeurs.id'), nullable=False)
    description_produit = db.Column(db.Text, nullable=True)
    linkProduit = db.Column(db.String(500))
    revendeur = db.relationship('Revendeur', back_populates='produits')
    stats = db.relationship('StatProduitBoost', back_populates='produit')

    def __repr__(self):
        return f'<Produit {self.nom_produit}>'

class CommandeStatut(enum.Enum):
    EN_ATTENTE = 'En attente'
    COMPLETEE = 'complétée'

class StatProduitBoostStatut(enum.Enum):
    A_FAIRE = 'à faire'
    EN_COURS = 'en cours'
    TERMINEE = 'terminé'
    A_REFAIRE = "à refaire" #pour ouvrir le modal et acivé la modification

class BoostStatut(enum.Enum):
    EN_COURS = 'en cours'
    A_VALIDE = 'à validé'
    TERMINEE = 'terminé'
    EN_ATTENTE = 'en attente'
    A_REFAIRE = "à refaire"

class StatProduitBoostTypePreuve(enum.Enum):
    LIEN = 'lien'
    SCREENSHOT = 'screenshot'

class Commande(db.Model):
    __tablename__ = 'commandes'

    idCommande = db.Column(db.String(12), primary_key=True)
    description_commande = db.Column(db.Text)
    code = db.Column(db.String(50), unique=True, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    commission_total = db.Column(db.Numeric(10,2))
    cout = db.Column(db.Numeric(10,2))
    tableauProduit = db.Column(db.JSON)
    statut = db.Column(db.Enum(CommandeStatut))
    image = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f'<Commande {self.idCommande}>'


class Boost(db.Model):
    __tablename__ = 'boosts'

    idBoost = db.Column(db.String(12), primary_key=True)
    idCommande = db.Column(db.String(12), db.ForeignKey('commandes.idCommande'), nullable=False)
    idUtilisateur = db.Column(db.String(12), db.ForeignKey('users.id'), nullable=False)
    transaction_id = db.Column(db.String(12), db.ForeignKey('transactions.id'), nullable=True)
    commande = db.relationship('Commande')
    user = db.relationship('User')
    transaction = db.relationship('Transaction')
    stats = db.relationship('StatProduitBoost', back_populates='boost')
    statut = db.Column(db.Enum(BoostStatut), default=BoostStatut.A_VALIDE, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Boost {self.idBoost}>'

class StatProduitBoost(db.Model):
    __tablename__ = 'stat_produit_boost'

    idStatProduitBoost = db.Column(db.String(12), primary_key=True)
    idBoost = db.Column(db.String(12), db.ForeignKey('boosts.idBoost'), nullable=False)
    idProduit = db.Column(db.String(12), db.ForeignKey('produits.idProduit'), nullable=False)
    cout = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    commission = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    statut = db.Column(db.Enum(StatProduitBoostStatut), default=StatProduitBoostStatut.A_FAIRE)
    Preuve = db.Column(db.Text)
    typePreuve = db.Column(db.Enum(StatProduitBoostTypePreuve))
    boost = db.relationship('Boost', back_populates='stats')
    produit = db.relationship('Produit', back_populates='stats')

    def __repr__(self):
        return f'<StatProduitBoost {self.idStatProduitBoost}>'

class Crypto(db.Model):
    __tablename__ = 'cryptos'

    idCrypto = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nomCrypto = db.Column(db.String(100), nullable=False)
    sigleCrypto = db.Column(db.String(20), nullable=False)
    commentaire = db.Column(db.String(255), nullable=True)
    adress = db.Column(db.String(500), nullable=False)
    minDepot = db.Column(db.Numeric(10, 2), nullable=False)
    isDeleted = db.Column(db.Boolean, default=False, nullable=False)

    def __repr__(self):
        return f'<Crypto {self.nomCrypto} ({self.sigleCrypto})>'

class ConfigRetrait(db.Model):
    __tablename__ = 'config_retraits'

    id = db.Column(db.String(12), primary_key=True)
    userId = db.Column(db.String(12), db.ForeignKey('users.id'), nullable=False)
    depositAdress = db.Column(db.String(500), nullable=False)
    coin = db.Column(db.String(50), nullable=False)
    reseau = db.Column(db.String(100), nullable=False)
    dateModif = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', backref='config_retraits')

    def __repr__(self):
        return f'<ConfigRetrait {self.id} for user {self.userId}>'


class MinRetrait(db.Model):
    __tablename__ = 'min_retraits'

    id = db.Column(db.String(12), primary_key=True)
    montant_min = db.Column(db.Numeric(10, 2), nullable=False)
    dateModif = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<MinRetrait {self.coin} {self.montant_min} {self.devise}>'

class Parrainage(db.Model):
    __tablename__ = 'parrainages'

    idParainnage = db.Column(db.String(12), primary_key=True)
    idTransaction = db.Column(db.String(12), db.ForeignKey('transactions.id'), nullable=False)
    idNewUser = db.Column(db.String(12), db.ForeignKey('users.id'), nullable=False)
    idOldUser = db.Column(db.String(12), db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    statut = db.Column(db.Enum(TransactionStatus), default=TransactionStatus.PENDING, nullable=False)
    montant = db.Column(db.Numeric(10, 2), nullable=False)

    # Relationships
    transaction = db.relationship('Transaction', backref='parrainages')
    new_user = db.relationship('User', foreign_keys=[idNewUser])
    old_user = db.relationship('User', foreign_keys=[idOldUser])

    def __repr__(self):
        return f'<Parrainage {self.idParainnage} {self.montant}>'


# Event listeners for ID generation
@event.listens_for(Parrainage, 'before_insert')
def set_parrainage_id(mapper, connect, target):
    if not target.idParainnage:
        target.idParainnage = generate_id()

# Event listeners for ID generation (existing models)
@event.listens_for(User, 'before_insert')
def set_user_id(mapper, connect, target):
    if not target.id:
        target.id = generate_id()

@event.listens_for(Revendeur, 'before_insert')
def set_revendeur_id(mapper, connect, target):
    if not target.id:
        target.id = generate_id()

@event.listens_for(Produit, 'before_insert')
def set_produit_id(mapper, connect, target):
    if not target.idProduit:
        target.idProduit = generate_id()

@event.listens_for(ConfigRetrait, 'before_insert')
def set_produit_id(mapper, connect, target):
    if not target.id:
        target.id = generate_id()

@event.listens_for(Commande, 'before_insert')
def set_commande_id(mapper, connect, target):
    if not target.idCommande:
        target.idCommande = generate_id()

@event.listens_for(Boost, 'before_insert')
def set_boost_id(mapper, connect, target):
    if not target.idBoost:
        target.idBoost = generate_id()

@event.listens_for(StatProduitBoost, 'before_insert')
def set_stat_id(mapper, connect, target):
    if not target.idStatProduitBoost:
        target.idStatProduitBoost = generate_id()

# Event listeners for legacy models
@event.listens_for(Qualification, 'before_insert')
def set_qualification_id(mapper, connect, target):
    if not target.id:
        target.id = generate_id()

@event.listens_for(Admin, 'before_insert')
def set_admin_id(mapper, connect, target):
    if not target.id:
        target.id = generate_id()

@event.listens_for(UtilisateurQualification, 'before_insert')
def set_uq_id(mapper, connect, target):
    if not target.id:
        target.id = generate_id()

@event.listens_for(Parametre, 'before_insert')
def set_parametre_id(mapper, connect, target):
    if not target.id:
        target.id = generate_id()

@event.listens_for(Transaction, 'before_insert')
def set_transaction_id(mapper, connect, target):
    if not target.id:
        target.id = generate_id()

@event.listens_for(MinRetrait, 'before_insert')
def set_min_retrait_id(mapper, connect, target):
    if not target.id:
        target.id = generate_id()

# Auto-create StatProduitBoost on Boost insert
@event.listens_for(Boost, 'after_insert')
def auto_create_stats(mapper, connection, boost):
    from sqlalchemy.orm import Session

    # Create a new session for this operation
    session = Session(bind=connection)

    try:
        commande = session.query(Commande).filter_by(idCommande=boost.idCommande).first()
        if commande and commande.tableauProduit:
            for idProduit in commande.tableauProduit:
                if idProduit:
                    existing = session.query(StatProduitBoost).filter_by(
                        idBoost=boost.idBoost,
                        idProduit=idProduit
                    ).first()
                    if not existing:
                        stat = StatProduitBoost(
                            idBoost=boost.idBoost,
                            idProduit=idProduit,
                            cout=0.00,
                            commission=0.00
                        )
                        session.add(stat)
        session.commit()
    finally:
        session.close()
