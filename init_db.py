from app import app, db
import pymysql
from models import Admin, User, Qualification, Revendeur, Produit, MinRetrait

# Create database if it doesn't exist
def create_database():
    try:
        connection = pymysql.connect(
            host='localhost',
            user='adr',
            password='Niavo jr171102!',
            port=3306
        )
        cursor = connection.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS tiktokshop")
        print("Database 'tiktokshop' created or already exists")
        connection.close()
    except Exception as e:
        print(f"Error creating database: {e}")

# Drop and create tables
def create_tables():
    with app.app_context():
        db.drop_all()
        db.create_all()

        # IDs now generated as String(12), no AUTO_INCREMENT

        print("Tables created successfully (new models + String IDs)")

def create_revendeur_seed():


    with app.app_context():
        # Check if revendeur already exists
        existing = Revendeur.query.first()
        if existing:
            print("Revendeur already exists. Skipping...")
        else:
            revendeur = Revendeur(nom="Amazon", plateforme="Amazon")
            db.session.add(revendeur)
            db.session.commit()
            print("Default Revendeur created: Amazon")

def create_produit_seed():

    with app.app_context():
        # Check if produit already exists
        existing = Produit.query.first()
        if existing:
            print("Produit already exists. Skipping...")
        else:
            revendeur = Revendeur.query.first()
            if revendeur:
                produit = Produit(
                    nom_produit="iPhone 15 Pro",
                    prix=999.99,
                    commission=50.00,
                    revendeur_id=revendeur.id,
                    image_produit="https://m.media-amazon.com/images/I/616mZZm8-7L._AC_SX425_.jpg",
                    linkProduit="https://amazon.com/iphone15"
                )
                db.session.add(produit)
                db.session.commit()
                print("Default Produit created: iPhone 15 Pro")
            else:
                print("No revendeur found for produit seed")

# Create default minRetrait
def create_min_retrait():
    with app.app_context():
        # Check if minRetrait already exists
        existing_min_retrait = MinRetrait.query.first()
        if not existing_min_retrait:
            min_retrait = MinRetrait(
                montant_min=1.00
                # dateModif will be set automatically by default
            )
            db.session.add(min_retrait)
            db.session.commit()
            print(f"Default MinRetrait created: {min_retrait.montant_min}")
        else:
            print(f"MinRetrait already exists: {existing_min_retrait.montant_min}")

# Create default admin
def create_default_admin():
    with app.app_context():
        # Check if admin already exists
        existing_admin = Admin.query.filter_by(email='andrianiavo@gmail.com').first()
        if not existing_admin:
            admin = Admin(email='andrianiavo@gmail.com', mot_de_passe='1234')
            db.session.add(admin)
            db.session.commit()
            print("Default admin created: andrianiavo@gmail.com")
        else:
            print("Admin already exists")

# Create qualifications
def create_qualifications():
    with app.app_context():
        # Check if qualifications already exist
        existing_qualifs = Qualification.query.first()
        if existing_qualifs:
            print("Qualifications already exist. Skipping...")
        else:
            qualifications = [
                Qualification(valeur=0, nom="DEBUTANT"),
                Qualification(valeur=1, nom="VALIDER"),
                Qualification(valeur=2, nom="VIP_1"),
                Qualification(valeur=3, nom="VIP_2"),
                Qualification(valeur=4, nom="VIP_3"),
                Qualification(valeur=5, nom="VIP_4"),
            ]
            db.session.add_all(qualifications)
            db.session.commit()
            print("Qualifications created successfully:")
            for q in qualifications:
                print(f"  - {q.nom} (valeur={q.valeur})")

if __name__ == '__main__':
    print("executé...")
    create_database()
    create_tables()
    create_qualifications()
    create_default_admin()

    # Seed Revendeur
    create_revendeur_seed()

    # Seed Produit
    create_produit_seed()

    # Seed MinRetrait
    create_min_retrait()

    print("\nDatabase initialization complete!")
