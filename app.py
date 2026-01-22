from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, Book, BorrowRequest
from werkzeug.utils import secure_filename
import os
import datetime

from config import Config
import cloudinary
import cloudinary.uploader
import cloudinary.api

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            if user.is_blocked:
                flash('Your account has been blocked. Please contact support.')
                return redirect(url_for('login'))
                
            login_user(user, remember=remember)
            return redirect(url_for('dashboard'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/index')
def index():
    query = request.args.get('q')
    if query:
        books = Book.query.filter((Book.title.contains(query)) | (Book.author.contains(query)) | (Book.category.contains(query))).all()
    else:
        books = Book.query.all()
    return render_template('index.html', books=books)

# Configure Cloudinary
cloudinary.config(
  cloud_name = app.config['CLOUDINARY_CLOUD_NAME'],
  api_key = app.config['CLOUDINARY_API_KEY'],
  api_secret = app.config['CLOUDINARY_API_SECRET']
)

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'epub', 'mobi'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/add_book', methods=['GET', 'POST'])
@login_required
def add_book():
    if request.method == 'POST':
        title = request.form.get('title')
        author = request.form.get('author')
        category = request.form.get('category')
        b_type = request.form.get('type')
        
        # Validation
        if not title or not author or not category:
             flash('All fields are required.')
             return redirect(url_for('add_book'))

        file_link = request.form.get('file_link')
        uploaded_file = request.files.get('file_upload')
        
        final_file_link = file_link
        filename = None
        
        if b_type == 'Digital':
            if uploaded_file and uploaded_file.filename != '':
                if allowed_file(uploaded_file.filename):
                    try:
                        upload_result = cloudinary.uploader.upload(uploaded_file, resource_type="auto")
                        final_file_link = upload_result.get('secure_url')
                        filename = upload_result.get('public_id') # Storing public_id in filename column
                    except Exception as e:
                        flash(f'Upload failed: {str(e)}')
                        return redirect(url_for('add_book'))
                else:
                    flash('Invalid file type. Allowed: PDF, JPG, PNG, EPUB, MOBI')
                    return redirect(url_for('add_book'))
            elif not file_link:
                 flash('For digital books, you must upload a file or provide a link.')
                 return redirect(url_for('add_book'))
        
        book = Book(title=title, author=author, category=category, type=b_type, file_link=final_file_link, filename=filename, owner=current_user)
        db.session.add(book)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add_book.html')

@app.route('/request_borrow/<int:id>', methods=['GET', 'POST'])
@login_required
def request_borrow(id):
    book = Book.query.get_or_404(id)
    
    # Digital immediate borrow
    if book.type == 'Digital':
        book.status = 'Borrowed'
        # Auto-create a "request" to track it
        req = BorrowRequest(
            book=book, 
            borrower=current_user, 
            proposed_date=str(datetime.date.today()),
            proposed_time="00:00",
            proposed_location="Digital",
            request_status="Accepted"
        )
        db.session.add(req)
        db.session.commit()
        flash('Digital book borrowed successfully! You can now download it.')
        return redirect(url_for('dashboard'))

    # Physical workflow
    if request.method == 'POST':
        date = request.form.get('date')
        time = request.form.get('time')
        location = request.form.get('location')
        
        req = BorrowRequest(book=book, borrower=current_user, proposed_date=date, proposed_time=time, proposed_location=location)
        db.session.add(req)
        db.session.commit()
        flash('Request sent successfully.')
        return redirect(url_for('dashboard'))
    return render_template('request_borrow.html', book=book)

@app.route('/handle_request/<int:id>', methods=['POST'])
@login_required
def handle_request(id):
    req = BorrowRequest.query.get_or_404(id)
    action = request.form.get('action') 
    
    if req.book.owner != current_user:
        return "Unauthorized", 403
        
    if action == 'accept':
        req.request_status = 'Accepted'
        req.book.status = 'Borrowed'
    elif action == 'reject':
        req.request_status = 'Rejected'
        req.book.status = 'Available'
    elif action == 'suggest':
        # Suggest alternative details
        new_date = request.form.get('date')
        new_time = request.form.get('time')
        new_location = request.form.get('location')
        if new_date: req.proposed_date = new_date
        if new_time: req.proposed_time = new_time
        if new_location: req.proposed_location = new_location
        # Do not change status to accepted yet, keep pending or mark as 'Changes Proposed' if we had that state. 
        # For simplicity, we'll keep it Pending but update values.
        flash('Suggestions sent to borrower.')
        
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/return_book/<int:req_id>', methods=['POST'])
@login_required
def return_book(req_id):
    req = BorrowRequest.query.get_or_404(req_id)
    
    # Logic: Owner returns Physical, Borrower returns Digital
    if req.book.type == 'Physical':
        if req.book.owner != current_user:
             return "Unauthorized", 403
        req.book.status = 'Returned'
        # req.request_status = 'Returned' # Optional if we want to track request history state
        
    elif req.book.type == 'Digital':
        if req.borrower != current_user:
             return "Unauthorized", 403
        req.book.status = 'Available' # Digital books go back to available immediately? Or Stay 'Returned' until reset?
        # Logic says "Book status always flows as: Available → Borrowed → Returned."
        # For Digital, "Borrower clicks Mark as Returned (or system auto-returns)".
        # Let's set it to Returned, then maybe logic elsewhere makes it Available again? 
        # Actually usually digital books can be borrowed by multiple people or just one.
        # Assuming single-instance model based on "Status" field on Book.
        req.book.status = 'Returned'

    db.session.commit()
    flash('Book marked as Returned.')
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Role-based redirection
    if current_user.role == 'Admin':
        return redirect(url_for('admin_dashboard'))
    
    # Member Dashboard Logic
    my_books = Book.query.filter_by(owner=current_user).all()
    borrowed_requests = BorrowRequest.query.filter_by(borrower=current_user).all()
    received_requests = BorrowRequest.query.join(Book).filter(Book.owner == current_user).all()
    return render_template('dashboard.html', my_books=my_books, borrowed_requests=borrowed_requests, received_requests=received_requests)

@app.route('/admin')
@login_required
def admin_dashboard():
    if current_user.role != 'Admin':
        return "Unauthorized", 403
        
    users = User.query.all()
    books = Book.query.all()
    
    # Metrics
    total_users = User.query.count()
    total_books = Book.query.count()
    total_requests = BorrowRequest.query.count()
    active_borrows = Book.query.filter_by(status='Borrowed').count()
    
    return render_template('admin.html', 
        users=users, 
        books=books,
        total_users=total_users,
        total_books=total_books,
        total_requests=total_requests,
        active_borrows=active_borrows
    )

@app.route('/admin/delete_book/<int:id>', methods=['POST'])
@login_required
def delete_book_admin(id):
    if current_user.role != 'Admin':
        return "Unauthorized", 403
    book = Book.query.get_or_404(id)
    # Also delete associated requests
    BorrowRequest.query.filter_by(book_id=id).delete()
    db.session.delete(book)
    db.session.commit()
    flash('Book removed by Admin.')
    return redirect(url_for('admin'))

@app.route('/toggle_block_user/<int:id>', methods=['POST'])
@login_required
def toggle_block_user(id):
    if current_user.role != 'Admin':
        return "Unauthorized", 403
    user = User.query.get_or_404(id)
    if user.username == 'admin': # Protect admin
        flash('Cannot block admin.')
        return redirect(url_for('admin'))
        
    user.is_blocked = not user.is_blocked
    db.session.commit()
    status = 'blocked' if user.is_blocked else 'unblocked'
    flash(f'User {user.username} has been {status}.')
    return redirect(url_for('admin'))

@app.route('/api/like/<int:book_id>', methods=['POST'])
@login_required
def like_book(book_id):
    book = Book.query.get_or_404(book_id)
    book.likes = (book.likes or 0) + 1
    db.session.commit()
    return {'likes': book.likes}

@app.route('/delete_book/<int:id>', methods=['POST'])
@login_required
def delete_book(id):
    book = Book.query.get_or_404(id)
    if book.owner != current_user:
        return "Unauthorized", 403
    BorrowRequest.query.filter_by(book_id=id).delete()
    db.session.delete(book)
    db.session.commit()
    flash('Book deleted.')
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
