from app import app, db
from models import User, Book
import os

def init_database():
    # Ensure the instance folder exists if Flask decides to put it there
    # But based on our config 'sqlite:///bms.db', it likely goes to the root or instance folder depending on Flask version defaults. 
    # Let's print the location.
    
    with app.app_context():
        db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        if not os.path.exists(db_path) and not os.path.isabs(db_path):
             # Some Flask versions/configs map relative paths to instance folders.
             # We will start by letting SQLAlchemy do its thing via create_all
             pass
             
        print("Creating database...")
        db.create_all()
        print("Database tables created.")
        
        # Check if Admin exists, if not create one
        if not User.query.filter_by(role='Admin').first():
            print("Creating default Admin User...")
            admin = User(username='admin', email='admin@bms.com', role='Admin')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("Admin user created: username='admin', password='admin123'")
        else:
            print("Admin user already exists.")

        print("Database setup complete.")

if __name__ == '__main__':
    init_database()
