from app import db, bcrypt
from datetime import datetime
import enum


class QualificationValue(enum.Enum):
    DEBUTANT = 0
    VALIDER = 1
    VIP_1 = 2
    VIP_2 = 3
    VIP_3 = 4
    VIP_4 = 5


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
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

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
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

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    valeur = db.Column(db.Integer, unique=True, nullable=False)
    nom = db.Column(db.String(50), nullable=False)

    def __init__(self, valeur, nom):
        self.valeur = valeur
        self.nom = nom

    def __repr__(self):
        return f'<Qualification {self.nom}>'


class UtilisateurQualification(db.Model):
    __tablename__ = 'utilisateur_qualifications'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_utilisateur = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    id_qualification = db.Column(db.Integer, db.ForeignKey('qualifications.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', back_populates='qualification')
    qualification = db.relationship('Qualification')

    def __repr__(self):
        return f'<UtilisateurQualification user={self.id_utilisateur} qualif={self.id_qualification}>'


class Parametre(db.Model):
    __tablename__ = 'parametres'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_utilisateur = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
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


class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    stock = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Product {self.name}>'
