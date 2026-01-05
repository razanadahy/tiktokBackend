from app import app, db
import pymysql
from models import Admin, User, Qualification, Product

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

        # Modify User table to start id at 2300
        from sqlalchemy import text
        db.session.execute(text('ALTER TABLE users AUTO_INCREMENT = 2300'))
        db.session.commit()

        print("Tables created successfully")

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
    create_database()
    create_tables()
    create_qualifications()
    create_default_admin()
    print("\nDatabase initialization complete!")
