from app import app, db
from models import User, Book, BorrowRequest
from werkzeug.security import generate_password_hash
import random

def seed_database():
    with app.app_context():
        # Clean slate
        print("Cleaning database...")
        db.drop_all()
        db.create_all()
        
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
        
        # Create Books
        print("Creating books...")
        categories = ['Fiction', 'Non-Fiction', 'Science', 'Technology', 'History', 'Art']
        
        # Helper to get random user (excluding admin ideally, but fine for now)
        def get_owner():
            return random.choice(users_objs[1:]) # Skip admin
            
        book_list = [
            ("The Great Gatsby", "F. Scott Fitzgerald", "Fiction", "Physical", None),
            ("To Kill a Mockingbird", "Harper Lee", "Fiction", "Physical", None),
            ("1984", "George Orwell", "Fiction", "Physical", None),
            ("Pride and Prejudice", "Jane Austen", "Fiction", "Physical", None),
            ("The Catcher in the Rye", "J.D. Salinger", "Fiction", "Physical", None),
            ("Sapiens", "Yuval Noah Harari", "Non-Fiction", "Digital", "http://example.com/sapiens.pdf"),
            ("Clean Code", "Robert C. Martin", "Technology", "Physical", None),
            ("The Pragmatic Programmer", "Andrew Hunt", "Technology", "Digital", "http://example.com/pragmatic.pdf"),
            ("Introduction to Algorithms", "Thomas H. Cormen", "Technology", "Physical", None),
            ("Design Patterns", "Erich Gamma", "Technology", "Physical", None),
            ("A Short History of Nearly Everything", "Bill Bryson", "Science", "Digital", "http://example.com/history.pdf"),
            ("Cosmos", "Carl Sagan", "Science", "Physical", None),
            ("The Art of War", "Sun Tzu", "History", "Digital", "http://example.com/artofwar.pdf"),
            ("Guns, Germs, and Steel", "Jared Diamond", "History", "Physical", None),
            ("Thinking, Fast and Slow", "Daniel Kahneman", "Non-Fiction", "Physical", None)
        ]
        
        books_objs = []
        for title, author, cat, btype, link in book_list:
            b = Book(title=title, author=author, category=cat, type=btype, file_link=link, owner=get_owner())
            books_objs.append(b)
            
        db.session.add_all(books_objs)
        db.session.commit()
        
        # Create Requests
        print("Creating requests...")
        # Randomly create some requests
        for _ in range(5):
            book = random.choice(books_objs)
            borrower = random.choice(users_objs[1:])
            
            # Don't borrow own book
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
        print("Seeding Complete!")

if __name__ == '__main__':
    seed_database()
