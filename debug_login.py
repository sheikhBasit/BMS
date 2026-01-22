from app import app
from models import User

def check_login():
    with app.app_context():
        # Check standard user
        u = User.query.filter_by(username='alice').first()
        if u:
            print(f"User alice found. Hash: {u.password_hash}")
            if u.check_password('password'):
                print("Password 'password' verifies correctly.")
            else:
                print("Password 'password' FAILED verification.")
        else:
            print("User alice NOT found.")

if __name__ == '__main__':
    check_login()
