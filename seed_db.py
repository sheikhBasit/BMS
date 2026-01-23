from app import app, db
from models import User, Book, BorrowRequest
from werkzeug.security import generate_password_hash
import random

def seed_database(force_reset=False):
    with app.app_context():
        # Clean slate only if forced
        if force_reset:
            print("Cleaning database...")
            db.drop_all()
            db.create_all()
        else:
            db.create_all()
        
        # Check if users already exist to avoid duplicate errors if not resetting
        if not force_reset and User.query.filter_by(username='admin').first():
             users_objs = User.query.all()
             print("Users already exist, skipping user creation...")
        else:
            # Create Users
            print("Creating users...")
            users_data = [
                ('admin', 'admin@bms.com', 'Admin'),
                ('alice', 'alice@example.com', 'Member'),
                ('bob', 'bob@example.com', 'Member'),
                ('charlie', 'charlie@example.com', 'Member'),
                ('david', 'david@example.com', 'Member'),
                ('eve', 'eve@example.com', 'Member')
            ]
            
            users_objs = []
            for username, email, role in users_data:
                u = User(username=username, email=email, role=role)
                if username == 'admin':
                    u.set_password('admin123')
                else:
                    u.set_password('password')
                users_objs.append(u)
            
            db.session.add_all(users_objs)
            db.session.commit()
        
        # Create Books only if count is low or we want to ensure these specific classics exist
        print("Ensuring seed books exist...")
        
        # Helper to get random user
        def get_owner():
            return random.choice(users_objs[1:]) # Skip admin
            
        # ... (book_list remains same)
        
        books_added = 0
        for title, author, cat, btype, link, loc, desc in book_list:
            # Check if book already exists (by title and author)
            exists = Book.query.filter_by(title=title, author=author).first()
            if not exists:
                b = Book(title=title, author=author, category=cat, type=btype, file_link=link, owner=get_owner(), location=loc, description=desc)
                db.session.add(b)
                books_added += 1
        
        db.session.commit()
        print(f"Added {books_added} new books.")
        
        # Create Requests only if database was empty/fresh
        if books_added > 0:
            print("Creating sample requests...")
            # We need a fresh list of books for random selection
            current_books = Book.query.all()
            for _ in range(5):
                book = random.choice(current_books)
                borrower = random.choice(users_objs[1:])
                
                if book.owner != borrower and book.status == 'Available' and book.type == 'Physical':
                    req = BorrowRequest(
                        book=book,
                        borrower=borrower,
                        proposed_date="2026-02-01",
                        proposed_time="10:00",
                        proposed_location="Community Center",
                        request_status="Pending"
                    )
                    db.session.add(req)
            db.session.commit()
        
        print("Seeding/Check Complete!")

if __name__ == '__main__':
    seed_database(force_reset=True)
