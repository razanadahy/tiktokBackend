from app import app, db
from sqlalchemy import text, inspect
import pymysql

def create_database_if_not_exists():
    """Crée la DB si elle n'existe pas (comme init_db.py)"""
    try:
        connection = pymysql.connect(
            host='localhost',
            user='adr',
            password='Niavo jr171102!',
            port=3306
        )
        cursor = connection.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS tiktokshop")
        print("Database 'tiktokshop' vérifiée/créée")
        connection.close()
    except Exception as e:
        print(f"Erreur DB: {e}")

def migrate_commandes_image():
    """Ajoute la colonne 'image' à la table 'commandes' si elle n'existe pas"""
    with app.app_context():
        inspector = inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('commandes')]

        if 'image' not in columns:
            print("Colonne 'image' manquante. Ajout en cours...")
            with db.engine.connect() as conn:
                conn.execute(text("ALTER TABLE commandes ADD COLUMN image VARCHAR(255)"))
                conn.commit()
            print("Colonne 'image' ajoutée avec succès!")
        else:
            print("Colonne 'image' existe déjà.")

if __name__ == '__main__':
    print("Migration en cours...")
    create_database_if_not_exists()
    migrate_commandes_image()
    print("Migration terminée!")
