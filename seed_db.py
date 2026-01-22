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
            ("The Great Gatsby", "F. Scott Fitzgerald", "Fiction", "Physical", None, "Main Library, Shelf A", "Classic novel of the Jazz Age."),
            ("To Kill a Mockingbird", "Harper Lee", "Fiction", "Physical", None, "Community Center Drop-off", "Powerful story of racial injustice."),
            ("1984", "George Orwell", "Fiction", "Physical", None, "Westside Book Club", "Dystopian social science fiction."),
            ("Pride and Prejudice", "Jane Austen", "Fiction", "Physical", None, "Available on Weekends", "Romantic novel of manners."),
            ("The Catcher in the Rye", "J.D. Salinger", "Fiction", "Physical", None, "Coffee Shop Downtown", "A story of teenage alienation."),
            ("Sapiens", "Yuval Noah Harari", "Non-Fiction", "Digital", "https://upload.wikimedia.org/wikipedia/commons/2/25/Sapiens_A_Brief_History_of_Humankind.pdf", None, "A brief history of humankind."),
            ("Clean Code", "Robert C. Martin", "Technology", "Physical", None, "Tech Hub Office", "A Handbook of Agile Software Craftsmanship."),
            ("The Pragmatic Programmer", "Andrew Hunt", "Technology", "Digital", "https://www.cin.ufpe.br/~sugar/files/The%20Pragmatic%20Programmer%20-%20From%20Journeyman%20to%20Master.pdf", None, "From Journeyman to Master."),
            ("Introduction to Algorithms", "Thomas H. Cormen", "Technology", "Physical", None, "University Lab", "Comprehensive guide to algorithms."),
            ("Design Patterns", "Erich Gamma", "Technology", "Physical", None, "Dev Lounge", "Elements of Reusable Object-Oriented Software."),
            ("A Short History of Nearly Everything", "Bill Bryson", "Science", "Digital", "http://www.metaphysicspirit.com/books/A%20Short%20History%20of%20Nearly%20Everything.pdf", None, "Bill Bryson explains science to the layperson."),
            ("Cosmos", "Carl Sagan", "Science", "Physical", None, "Science Museum Gift Shop", "The story of cosmic evolution."),
            ("The Art of War", "Sun Tzu", "History", "Digital", "https://sites.ualberta.ca/~enoch/Readings/The_Art_of_War.pdf", None, "Ancient Chinese military treatise."),
            ("Guns, Germs, and Steel", "Jared Diamond", "History", "Physical", None, "History Dept.", "The Fates of Human Societies."),
            ("Thinking, Fast and Slow", "Daniel Kahneman", "Non-Fiction", "Physical", None, "Psychology Wing", "System 1 and System 2 thinking.")
        ]
        
        books_objs = []
        for title, author, cat, btype, link, loc, desc in book_list:
            b = Book(title=title, author=author, category=cat, type=btype, file_link=link, owner=get_owner(), location=loc, description=desc)
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
