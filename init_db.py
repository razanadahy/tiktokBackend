from app import app, db
import pymysql
from models import Admin, User

# Create database if it doesn't exist
def create_database():
    try:
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='',
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

if __name__ == '__main__':
    create_database()
    create_tables()
    create_default_admin()
