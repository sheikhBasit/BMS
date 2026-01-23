from app import app, db
from models import User, Book, BorrowRequest
import datetime

def verify_diversity():
    with app.app_context():
        print(f"Total Requests: {BorrowRequest.query.count()}")
        borrowed = Book.query.filter_by(status='borrowed').count()
        returned = Book.query.filter_by(status='returned').count()
        print(f"Borrowed Books: {borrowed}")
        print(f"Returned Books: {returned}")
        
        today = datetime.date.today().strftime('%Y-%m-%d')
        overdue = BorrowRequest.query.join(Book).filter(
            BorrowRequest.request_status.ilike('accepted'),
            Book.status.ilike('borrowed'),
            BorrowRequest.proposed_date < today
        ).count()
        print(f"Overdue Requests (Logic): {overdue}")

if __name__ == '__main__':
    verify_diversity()
