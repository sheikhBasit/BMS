from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), nullable=False, default='Member') # Member or Admin
    is_blocked = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(20), nullable=False) # Physical or Digital
    file_link = db.Column(db.String(500), nullable=True) # Link to digital resource
    filename = db.Column(db.String(500), nullable=True) # Uploaded file path
    likes = db.Column(db.Integer, default=0) # New Interactive Feature
    status = db.Column(db.String(20), default='Available') # Available, Borrowed, Returned
    
    # Adding owner relationship as implied by workflow
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    owner = db.relationship('User', backref=db.backref('books', lazy=True))

class BorrowRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    borrower_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    proposed_date = db.Column(db.String(20))
    proposed_time = db.Column(db.String(20))
    proposed_location = db.Column(db.String(200))
    request_status = db.Column(db.String(20), default='Pending') # Pending, Accepted, Rejected

    book = db.relationship('Book', backref=db.backref('requests', lazy=True))
    borrower = db.relationship('User', backref=db.backref('borrow_requests', lazy=True))
