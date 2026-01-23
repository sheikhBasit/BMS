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

# Fix for Vercel Read-only File System
if os.environ.get('VERCEL'):
    app.instance_path = '/tmp'
    # Ensure SQLite uses the writable /tmp directory if no DATABASE_URL is set
    if not os.environ.get('DATABASE_URL'):
        Config.SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join('/tmp', 'bms.db')

app.config.from_object(Config)

@app.errorhandler(413)
def request_entity_too_large(error):
    flash('File too large. Maximum size is 16MB.')
    return redirect(url_for('add_book'))

db.init_app(app)
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def ensure_ready():
    """Ensure database is connected, admin exists, and books are seeded."""
    try:
        # 1. Ensure Table Creation
        db.create_all()
        
        # 2. Check for Admin
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            print("Creating default admin...")
            admin = User(username='admin', email='admin@bms.com', role='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()

        # 3. Check for Data parity
        if Book.query.count() == 0:
            print("Library empty. Triggering auto-seed...")
            from seed_db import seed_database
            seed_database()
            print("Auto-seeding successful.")
            return True
    except Exception as e:
        print(f"Startup check error: {e}")
    return False

# Trigger basic setup on module load, but we'll also call it in routes
with app.app_context():
    ensure_ready()

@app.context_processor
def inject_db_status():
    connected = False
    db_type = "SQLite"
    try:
        from sqlalchemy import text
        db.session.execute(text('SELECT 1'))
        connected = True
        # Determine DB type
        uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
        if 'postgresql' in uri:
            db_type = "Postgres"
        elif '/tmp/' in uri:
            db_type = "SQLite (Temp)"
    except:
        connected = False
    return dict(db_connected=connected, db_type=db_type)

# Predefined book categories
BOOK_CATEGORIES = [
    'fiction', 'non-fiction', 'science', 'technology', 
    'history', 'biography', 'self-help', 'business',
    'art', 'philosophy', 'religion', 'mystery',
    'romance', 'thriller', 'fantasy', 'other'
]

@app.route('/')
def index_root():
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip().lower()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password')
        role = 'member' # Default role
        
        # Validation
        if not username or not email or not password:
             flash('All fields are required.')
             return redirect(url_for('register'))
        
        if len(username) < 3 or len(username) > 20:
            flash('Username must be between 3 and 20 characters.')
            return redirect(url_for('register'))
        
        if not '@' in email or '.' not in email:
            flash('Please enter a valid email address.')
            return redirect(url_for('register'))
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long.')
            return redirect(url_for('register'))

        if User.query.filter((User.username == username) | (User.email == email)).first():
            flash('Username or Email already exists')
            return redirect(url_for('register'))
            
        user = User(username=username, email=email, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('index'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip().lower()
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        
        user = User.query.filter_by(username=username).first()
        if user:
            if user.check_password(password):
                if user.is_blocked:
                    flash('Your account has been blocked. Please contact support.')
                    return redirect(url_for('login'))
                login_user(user, remember=remember)
                return redirect(url_for('dashboard'))
            else:
                flash('Incorrect password. Please try again.')
        else:
            flash('Username not found. Please check your spelling or register.')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/index')
def index():
    # Only seed if the database is literally empty
    if Book.query.count() == 0:
        ensure_ready()
    
    query = request.args.get('q', '').strip().lower()
    if query:
        # Keyword search: split by space and search for each term
        keywords = query.split()
        filters = []
        for word in keywords:
            word_filter = (Book.title.ilike(f'%{word}%')) | \
                         (Book.author.ilike(f'%{word}%')) | \
                         (Book.category.ilike(f'%{word}%'))
            filters.append(word_filter)
        
        if filters:
            from sqlalchemy import and_
            books = Book.query.filter(Book.is_deleted == False).filter(and_(*filters)).all()
        else:
            books = Book.query.filter_by(is_deleted=False).all()
    else:
        books = Book.query.filter_by(is_deleted=False).all()
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
        title = request.form.get('title', '').strip().lower()
        author = request.form.get('author', '').strip().lower()
        category = request.form.get('category', '').strip().lower()
        b_type = request.form.get('type')
        
        # Validation
        if not title or not author or not category:
             flash('All fields are required.')
             return redirect(url_for('add_book'))
        
        if len(title) < 2 or len(title) > 200:
            flash('Title must be between 2 and 200 characters.')
            return redirect(url_for('add_book'))
        
        if len(author) < 2 or len(author) > 200:
            flash('Author name must be between 2 and 200 characters.')
            return redirect(url_for('add_book'))
        
        if category not in BOOK_CATEGORIES:
            flash('Please select a valid category.')
            return redirect(url_for('add_book'))

        file_link = request.form.get('file_link')
        uploaded_file = request.files.get('file_upload')
        
        final_file_link = file_link
        filename = None
        
        if b_type == 'Digital':
            if uploaded_file and uploaded_file.filename != '':
                if allowed_file(uploaded_file.filename):
                    try:
                        # Cloudinary Upload if on Vercel or configured
                        if os.environ.get('VERCEL') or app.config['CLOUDINARY_API_KEY']:
                            upload_result = cloudinary.uploader.upload(
                                uploaded_file,
                                resource_type="auto",
                                folder="bookshare_digital"
                            )
                            final_file_link = upload_result.get('secure_url')
                            filename = uploaded_file.filename
                        else:
                            # Local Upload Logic (Development only)
                            upload_dir = os.path.join('static', 'uploads')
                            os.makedirs(upload_dir, exist_ok=True)
                            
                            filename = secure_filename(uploaded_file.filename)
                            import uuid
                            unique_filename = f"{uuid.uuid4().hex}_{filename}"
                            
                            file_path = os.path.join(upload_dir, unique_filename)
                            uploaded_file.save(file_path)
                            
                            final_file_link = f"/static/uploads/{unique_filename}"
                            filename = unique_filename
                        
                    except Exception as e:
                        flash(f'Upload failed: {str(e)}')
                        return redirect(url_for('add_book'))
                else:
                    flash('Invalid file type. Allowed: PDF, JPG, PNG, EPUB, MOBI')
                    return redirect(url_for('add_book'))
            elif not file_link:
                 flash('For digital books, you must upload a file or provide a link.')
                 return redirect(url_for('add_book'))
        
        # New fields: location, description
        location_note = request.form.get('location', '').strip().lower()
        description = request.form.get('description', '').strip().lower()

        # Admin can assign owner
        owner = current_user
        if current_user.role == 'admin' and request.form.get('owner_id'):
            owner = User.query.get(request.form.get('owner_id')) or current_user

        book = Book(
            title=title, 
            author=author, 
            category=category, 
            type=b_type, 
            file_link=final_file_link, 
            filename=filename, # Storing just the filename too if useful
            owner=owner,
            location=location_note,
            description=description
        )
        db.session.add(book)
        db.session.commit()
        return redirect(url_for('index'))
    
    users = []
    if current_user.role == 'admin':
        users = User.query.all()

    return render_template('add_book.html', categories=BOOK_CATEGORIES, users=users)

@app.route('/edit_book/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_book(id):
    book = Book.query.get_or_404(id)
    # Admin can edit any book, Owner can edit their own
    if book.owner != current_user and current_user.role != 'admin':
        return "Unauthorized", 403
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip().lower()
        author = request.form.get('author', '').strip().lower()
        category = request.form.get('category', '').strip().lower()
        description = request.form.get('description', '').strip().lower()
        location = request.form.get('location', '').strip().lower()
        
        # Validation
        if not title or not author or not category:
            flash('Title, Author, and Category are required.')
            return redirect(url_for('edit_book', id=id))
        
        if len(title) < 2 or len(title) > 200:
            flash('Title must be between 2 and 200 characters.')
            return redirect(url_for('edit_book', id=id))
        
        if len(author) < 2 or len(author) > 200:
            flash('Author name must be between 2 and 200 characters.')
            return redirect(url_for('edit_book', id=id))
        
        if category not in BOOK_CATEGORIES:
            flash('Please select a valid category.')
            return redirect(url_for('edit_book', id=id))
        
        book.title = title
        book.author = author
        book.category = category
        book.description = description
        book.location = location
        
        db.session.commit()
        flash('Book updated successfully.')
        if current_user.role == 'admin':
             return redirect(url_for('admin_dashboard'))
        return redirect(url_for('dashboard'))
        
    return render_template('edit_book.html', book=book, categories=BOOK_CATEGORIES)

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
        location = request.form.get('location', '').strip().lower()
        
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
    
    if req.book.owner != current_user and current_user.role != 'admin':
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
        new_location = request.form.get('location', '').strip().lower()
        if new_date: req.proposed_date = new_date
        if new_time: req.proposed_time = new_time
        if new_location: req.proposed_location = new_location
        flash('Suggestions sent to borrower.')
        
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/return_book/<int:req_id>', methods=['POST'])
@login_required
def return_book(req_id):
    req = BorrowRequest.query.get_or_404(req_id)
    
    # Logic: Owner returns Physical, Borrower returns Digital
    if req.book.type == 'Physical':
        if req.book.owner != current_user and current_user.role != 'admin':
             return "Unauthorized", 403
        req.book.status = 'Returned'
        
    elif req.book.type == 'Digital':
        if req.borrower != current_user and current_user.role != 'Admin':
             return "Unauthorized", 403
        req.book.status = 'Returned'

    db.session.commit()
    flash('Book marked as Returned.')
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Role-based redirection
    if current_user.role == 'admin':
        return redirect(url_for('admin_dashboard'))
    
    # Member Dashboard Logic
    # Update: Filter out deleted books
    my_books = Book.query.filter_by(owner=current_user, is_deleted=False).all()
    borrowed_requests = BorrowRequest.query.filter_by(borrower=current_user).all()
    # Received requests for non-deleted books
    received_requests = BorrowRequest.query.join(Book).filter(Book.owner == current_user, Book.is_deleted == False).all()
    
    return render_template('dashboard.html', my_books=my_books, borrowed_requests=borrowed_requests, received_requests=received_requests)

@app.route('/admin')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        return "Unauthorized", 403
        
    users = User.query.all()
    books = Book.query.filter_by(is_deleted=False).all()
    
    # Metrics
    total_users = User.query.count()
    total_books = Book.query.filter_by(is_deleted=False).count()
    total_requests = BorrowRequest.query.count()
    active_borrows = Book.query.filter_by(status='Borrowed', is_deleted=False).count()
    
    # Chart data
    physical_books = Book.query.filter_by(type='Physical', is_deleted=False).count()
    digital_books = Book.query.filter_by(type='Digital', is_deleted=False).count()
    
    available_books = Book.query.filter_by(status='Available', is_deleted=False).count()
    borrowed_books = Book.query.filter_by(status='Borrowed', is_deleted=False).count()
    returned_books = Book.query.filter_by(status='Returned', is_deleted=False).count()
    
    returned_books = Book.query.filter_by(status='Returned', is_deleted=False).count()
    
    # All requests for admin to view
    all_requests = BorrowRequest.query.all()
    
    return render_template('admin.html', 
        users=users, 
        books=books,
        total_users=total_users,
        total_books=total_books,
        total_requests=total_requests,
        active_borrows=active_borrows,
        physical_books=physical_books,
        digital_books=digital_books,
        available_books=available_books,
        borrowed_books=borrowed_books,
        returned_books=returned_books,
        all_requests=all_requests
    )

@app.route('/admin/add_user', methods=['POST'])
@login_required
def admin_add_user():
    if current_user.role != 'admin':
        return "Unauthorized", 403
    
    username = request.form.get('username', '').strip().lower()
    email = request.form.get('email', '').strip().lower()
    password = request.form.get('password')
    role = request.form.get('role', 'member').lower()
    
    if not username or not email or not password:
        flash('All fields are required.')
        return redirect(url_for('admin_dashboard'))
    
    if User.query.filter((User.username == username) | (User.email == email)).first():
        flash('Username or Email already exists')
        return redirect(url_for('admin_dashboard'))
        
    user = User(username=username, email=email, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    flash(f'User {username} created successfully.')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete_user/<int:id>', methods=['POST'])
@login_required
def admin_delete_user(id):
    if current_user.role != 'admin':
        return "Unauthorized", 403
    user = User.query.get_or_404(id)
    if user.username == 'admin':
        flash('Cannot delete primary admin.')
        return redirect(url_for('admin_dashboard'))
    
    # Option: delete their books too? For now just delete user
    db.session.delete(user)
    db.session.commit()
    flash(f'User {user.username} deleted.')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/seed-data', methods=['POST', 'GET'])
def admin_seed_data():
    try:
        from seed_db import seed_database
        # Default to safe mode (non-destructive)
        seed_database(force_reset=False)
        return "Database Checked and Seeded Successfully (Preserving custom data)!", 200
    except Exception as e:
        return f"Seeding failed: {str(e)}", 500

@app.route('/admin/delete_book/<int:id>', methods=['POST'])
@login_required
def delete_book_admin(id):
    if current_user.role != 'admin':
        return "Unauthorized", 403
    book = Book.query.get_or_404(id)
    book.is_deleted = True
    db.session.commit()
    flash('Book removed by Admin (Soft Deleted).')
    return redirect(url_for('admin_dashboard'))

@app.route('/toggle_block_user/<int:id>', methods=['POST'])
@login_required
def toggle_block_user(id):
    if current_user.role != 'admin':
        return "Unauthorized", 403
    user = User.query.get_or_404(id)
    if user.username == 'admin': # Protect admin
        flash('Cannot block admin.')
        return redirect(url_for('admin_dashboard'))
        
    user.is_blocked = not user.is_blocked
    db.session.commit()
    status = 'blocked' if user.is_blocked else 'unblocked'
    flash(f'User {user.username} has been {status}.')
    return redirect(url_for('admin_dashboard'))

@app.route('/api/like/<int:book_id>', methods=['POST'])
@login_required
def like_book(book_id):
    from models import BookLike
    book = Book.query.get_or_404(book_id)
    
    # Check if user already liked this book
    existing_like = BookLike.query.filter_by(user_id=current_user.id, book_id=book_id).first()
    
    if existing_like:
        # Unlike: Remove the like
        db.session.delete(existing_like)
        book.likes = max((book.likes or 1) - 1, 0)  # Prevent negative likes
        db.session.commit()
        return {'likes': book.likes, 'user_liked': False, 'action': 'unliked'}
    
    # Like: Add new like
    new_like = BookLike(user_id=current_user.id, book_id=book_id)
    book.likes = (book.likes or 0) + 1
    db.session.add(new_like)
    db.session.commit()
    return {'likes': book.likes, 'user_liked': True, 'action': 'liked'}

@app.route('/book/<int:id>')
def book_detail(id):
    book = Book.query.get_or_404(id)
    if book.is_deleted:
        flash('This book is no longer available.')
        return redirect(url_for('index'))
    
    # Check if current user has liked this book
    user_has_liked = False
    if current_user.is_authenticated:
        from models import BookLike
        user_has_liked = BookLike.query.filter_by(user_id=current_user.id, book_id=id).first() is not None
    
    return render_template('book_detail.html', book=book, user_has_liked=user_has_liked)

@app.route('/my_likes')
@login_required
def my_likes():
    from models import BookLike
    # Get all books the current user has liked
    liked_book_ids = [like.book_id for like in BookLike.query.filter_by(user_id=current_user.id).all()]
    liked_books = Book.query.filter(Book.id.in_(liked_book_ids), Book.is_deleted == False).all() if liked_book_ids else []
    return render_template('my_likes.html', books=liked_books)

@app.route('/delete_book/<int:id>', methods=['POST'])
@login_required
def delete_book(id):
    book = Book.query.get_or_404(id)
    if book.owner != current_user and current_user.role != 'admin':
        return "Unauthorized", 403
    book.is_deleted = True
    db.session.commit()
    flash('Book deleted.')
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
