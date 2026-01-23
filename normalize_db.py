from app import app, db
from models import User, Book, BorrowRequest

def normalize_database():
    with app.app_context():
        print("Normalizing Users...")
        users = User.query.all()
        for user in users:
            user.username = user.username.lower()
            user.email = user.email.lower()
            user.role = user.role.lower()
        
        print("Normalizing Books...")
        books = Book.query.all()
        for book in books:
            book.title = book.title.lower() if book.title else book.title
            book.author = book.author.lower() if book.author else book.author
            book.category = book.category.lower() if book.category else book.category
            book.location = book.location.lower() if book.location else book.location
            book.description = book.description.lower() if book.description else book.description
        
        print("Normalizing BorrowRequests...")
        reqs = BorrowRequest.query.all()
        for req in reqs:
            req.proposed_location = req.proposed_location.lower() if req.proposed_location else req.proposed_location
            req.request_status = req.request_status.lower() if req.request_status else req.request_status
            
        try:
            db.session.commit()
            print("Database normalization successful!")
        except Exception as e:
            db.session.rollback()
            print(f"Error during normalization: {e}")

if __name__ == '__main__':
    normalize_database()
