import pytest
from app import app, db
from models import User

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()

@pytest.fixture
def init_database(client):
    # Create default user and admin
    admin = User(username='admin', email='admin@example.com', role='Admin')
    admin.set_password('adminpass')
    
    user = User(username='testuser', email='user@example.com', role='Member')
    user.set_password('userpass')
    
    db.session.add(admin)
    db.session.add(user)
    db.session.commit()
    
    yield db 
