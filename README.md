# BookShare - Cozy Reading Community 📚☕

## Overview
BookShare is a warm, inviting web-based community platform that brings book lovers together. With a **cozy library aesthetic** featuring warm amber tones and library-themed backgrounds, the platform facilitates sharing and borrowing of both physical and digital books in a comfortable, reading-focused environment.

## ✨ Key Features

### 📖 Book Management
- **Add Physical Books** with location and description
- **Add Digital Books** with PDF upload (max 16MB, drag-and-drop)
- **Search & Browse** by title, author, or category
- **Detailed Book Pages** with embedded PDF viewer
- **Like/Unlike Books** with one-time toggle
- **Soft Delete** preserves data integrity

### 🔐 User Features
- **Secure Registration** with validation (username, email, password)
- **Role-Based Access** (Member and Admin)
- **Personal Dashboard** with column layout
- **My Likes Page** to track favorite books
- **Borrow Requests** with date/time validation

### 👥 Borrowing Workflow
- **Physical Books**: Request with proposed date, time, and location
- **Digital Books**: Instant PDF access and download
- **Request Management**: Accept, Reject, or Return
- **Status Tracking**: Available, Borrowed, Returned

### 🎨 Cozy Reading Theme
- **Warm Color Palette**: Amber (#d4a574), Brown (#8b7355), Cream (#e8c4a0)
- **Library Backgrounds**: Vintage bookshelves and reading nooks
- **Comfortable Design**: Soft glows, warm shadows, eye-friendly colors
- **Modern UI**: Glassmorphism with cozy aesthetics

### 🛡️ Admin Features
- **Dashboard Analytics** with Chart.js visualizations
- **Books by Type** (Doughnut chart)
- **Book Status** (Bar chart)
- **Universal Edit/Delete** permissions
- **User & Request Management**

### ✅ Robust Validations
- **Frontend**: HTML5 attributes (minlength, maxlength, pattern, type)
- **Backend**: Field length, format, and enum checks
- **File Upload**: Size limits (16MB), secure filenames
- **Date/Time**: Prevents past selections

## Technology Stack
- **Backend**: Flask (Python 2.3.3)
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: Flask-Login with password hashing
- **Frontend**: HTML5, CSS3 (Cozy Reading Theme), Vanilla JavaScript
- **Charts**: Chart.js for analytics
- **Alerts**: SweetAlert2 with custom styling
- **File Storage**: Local uploads + Cloudinary support

## Installation & Setup

### Prerequisites
- Python 3.8+
- pip

### Steps
1. **Clone the repository** (if applicable) or navigate to the project directory.

2. **Create a Virtual Environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the Database**:
   ```bash
   python init_db.py
   ```

5. **(Optional) Seed with Sample Data**:
   This will create sample users (admin, alice, bob, charlie) and books.
   ```bash
   python seed_db.py
   ```

## Running the Application
1. Ensure your virtual environment is active.
2. Run the Flask app:
   ```bash
   python app.py
   ```
3. Open your browser and visit: `http://127.0.0.1:5000`

### Default Accounts (from Seeding)
- **Admin**: `admin` / `admin123`
- **User**: `alice` / `password`
- **User**: `bob` / `password`

## Running Tests
The project includes a comprehensive test suite using `pytest`.

```bash
pytest
```
This will run all tests located in the `tests/` directory, covering endpoints, authentication, and borrow workflows.

## Project Structure
```
BMS/
├── app.py                          # Main Flask application and routes
├── models.py                       # Database models (User, Book, BorrowRequest, BookLike)
├── config.py                       # Configuration settings
├── init_db.py                      # Database initialization
├── seed_db.py                      # Sample data seeding
├── requirements.txt                # Python dependencies
├── vercel.json                     # Vercel deployment config
├── .vercelignore                   # Files to exclude from deployment
├── static/
│   ├── style.css                   # Cozy reading theme CSS
│   └── uploads/                    # Digital book PDFs (local)
├── templates/                      # Jinja2 HTML templates
│   ├── base.html                   # Base layout with nav
│   ├── index.html                  # Public book search
│   ├── login.html                  # Login page
│   ├── register.html               # Registration page
│   ├── dashboard.html              # Member dashboard (column layout)
│   ├── admin.html                  # Admin dashboard with charts
│   ├── add_book.html               # Add book form with file upload
│   ├── edit_book.html              # Edit book form
│   ├── book_detail.html            # Detailed book view with PDF
│   ├── my_likes.html               # User's liked books
│   └── request_borrow.html         # Borrow request form
├── tests/                          # Pytest test suite
│   ├── conftest.py
│   ├── test_endpoints.py
│   └── test_extended.py
└── Documentation/
    ├── QUICK_REFERENCE.md          # User guide and credentials
    ├── FEATURE_IMPLEMENTATION_SUMMARY.md
    ├── COZY_THEME_GUIDE.md         # Theme documentation
    └── DEPLOYMENT.md               # Vercel deployment guide
```

## 🚀 Deployment to Vercel

### Quick Deploy
1. Push code to GitHub/GitLab
2. Import project to Vercel dashboard
3. Configure environment variables
4. Deploy!

### Environment Variables Needed
```
SECRET_KEY=your-secret-key
FLASK_ENV=production
DATABASE_URL=your-postgres-url (for production)
```

### Important Notes
- **Database**: SQLite doesn't work on Vercel (use PostgreSQL)
- **File Uploads**: Use Cloudinary or Vercel Blob Storage
- **Full Guide**: See `DEPLOYMENT.md` for detailed instructions

## 📚 Documentation

- **`QUICK_REFERENCE.md`** - Login credentials, common workflows, troubleshooting
- **`FEATURE_IMPLEMENTATION_SUMMARY.md`** - All features and technical details
- **`COZY_THEME_GUIDE.md`** - Theme transformation documentation
- **`DEPLOYMENT.md`** - Complete Vercel deployment guide

## 🎨 Theme Customization

The cozy reading theme can be customized via CSS variables in `static/style.css`:
```css
:root {
    --primary: #d4a574;      /* Amber */
    --secondary: #8b7355;    /* Brown */
    --accent: #e8c4a0;       /* Cream */
    --cozy-glow: rgba(212, 165, 116, 0.2);
}
```

## Supervisor Information
- **Name**: Muhammad Ilyas
- **Email**: Muhammad.ilyas@vu.edu.pk
- **Teams**: ilyas.vu@outlook.com

---

**Made with ❤️ for book lovers**
