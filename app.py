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

    db.create_all()

@app.route('/')
def index_root():
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password')
        role = 'Member' # Default role
        
        if not username or not email or not password:
             flash('All fields are required.')
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
        username = request.form.get('username', '').strip()
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
    query = request.args.get('q', '').strip()
    if query:
        books = Book.query.filter(Book.is_deleted == False).filter((Book.title.contains(query)) | (Book.author.contains(query)) | (Book.category.contains(query))).all()
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
        title = request.form.get('title', '').strip()
        author = request.form.get('author', '').strip()
        category = request.form.get('category', '').strip()
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
                        # Local Upload Logic
                        filename = secure_filename(uploaded_file.filename)
                        # Ensure filename is unique to prevent overwrite
                        import uuid
                        filename = f"{uuid.uuid4().hex}_{filename}"
                        
                        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                        uploaded_file.save(file_path)
                        
                        # Set file_link to the local static route
                        # Note: We store the filename, but for the link we want the URL
                        # But typically we just construct the URL in the template using the filename.
                        # However, for consistency with the 'file_link' field which might be an external URL...
                        # We will store the relative URL in file_link if local.
                        
                        # Actually keeping filename is good.
                        final_file_link = url_for('static', filename='uploads/' + filename) 
                        
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
        location_note = request.form.get('location')
        description = request.form.get('description')

        book = Book(
            title=title, 
            author=author, 
            category=category, 
            type=b_type, 
            file_link=final_file_link, 
            filename=filename, # Storing just the filename too if useful
            owner=current_user,
            location=location_note,
            description=description
        )
        db.session.add(book)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add_book.html')

@app.route('/edit_book/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_book(id):
    book = Book.query.get_or_404(id)
    # Admin can edit any book, Owner can edit their own
    if book.owner != current_user and current_user.role != 'Admin':
        return "Unauthorized", 403
    
    if request.method == 'POST':
        book.title = request.form.get('title', '').strip()
        book.author = request.form.get('author', '').strip()
        book.category = request.form.get('category', '').strip()
        book.description = request.form.get('description', '').strip()
        book.location = request.form.get('location', '').strip()
        
        db.session.commit()
        flash('Book updated successfully.')
        if current_user.role == 'Admin':
             return redirect(url_for('admin_dashboard'))
        return redirect(url_for('dashboard'))
        
    return render_template('edit_book.html', book=book)

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
        flash('Suggestions sent to borrower.')
        
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/return_book/<int:req_id>', methods=['POST'])
@login_required
def return_book(req_id):
    req = BorrowRequest.query.get_or_404(req_id)
    
    # Logic: Owner returns Physical, Borrower returns Digital
    if req.book.type == 'Physical':
        if req.book.owner != current_user and current_user.role != 'Admin':
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
    if current_user.role == 'Admin':
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
    if current_user.role != 'Admin':
        return "Unauthorized", 403
        
    users = User.query.all()
    books = Book.query.filter_by(is_deleted=False).all()
    
    # Metrics
    total_users = User.query.count()
    total_books = Book.query.filter_by(is_deleted=False).count()
    total_requests = BorrowRequest.query.count()
    active_borrows = Book.query.filter_by(status='Borrowed', is_deleted=False).count()
    
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
    book.is_deleted = True
    db.session.commit()
    flash('Book removed by Admin (Soft Deleted).')
    return redirect(url_for('admin_dashboard'))

@app.route('/toggle_block_user/<int:id>', methods=['POST'])
@login_required
def toggle_block_user(id):
    if current_user.role != 'Admin':
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
    book = Book.query.get_or_404(book_id)
    book.likes = (book.likes or 0) + 1
    db.session.commit()
    return {'likes': book.likes}

@app.route('/delete_book/<int:id>', methods=['POST'])
@login_required
def delete_book(id):
    book = Book.query.get_or_404(id)
    if book.owner != current_user and current_user.role != 'Admin':
        return "Unauthorized", 403
    book.is_deleted = True
    db.session.commit()
    flash('Book deleted.')
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
