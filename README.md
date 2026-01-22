# Book Sharing Platform (BMS)

## Overview
The Book Sharing Platform is a web-based community application designed to facilitate the sharing and borrowing of both physical and digital books. It connects book owners with borrowers, managing the coordination of physical handovers and digital access permissions effectively.

## Features
- **User Roles**: Member and Admin roles.
- **Book Management**:
    - Add Physical Books with location notes.
    - Add Digital Books with file links.
    - Search books by title, author, or category.
- **Borrowing Workflow**:
    - **Physical Books**: Request borrowing with proposed date, time, and location. Owners can Accept or Reject.
    - **Digital Books**: Instant access upon status change (workflow supported).
- **Dashboards**:
    - **Member Dashboard**: View shared books, received requests, and borrowed items.
    - **Admin Dashboard**: Manage all users and books in the system.
- **Authentication**: Secure login and registration.

## Technology Stack
- **Backend**: Flask (Python)
- **Database**: SQLite (via Flask-SQLAlchemy)
- **Authentication**: Flask-Login
- **Testing**: Pytest
- **Frontend**: HTML5, CSS3 (Glassmorphism Design), Jinja2 Templating

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
├── app.py              # Main application entry point and routes
├── models.py           # Database models (User, Book, BorrowRequest)
├── init_db.py          # Script to initialize database
├── seed_db.py          # Script to populate database with dummy data
├── requirements.txt    # Python dependencies
├── static/
│   └── style.css       # Global CSS styles
├── templates/          # HTML Templates
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── add_book.html
│   └── admin.html
└── tests/              # Test suite
    ├── conftest.py
    ├── test_endpoints.py
    └── test_extended.py
```

## Supervisor Information
- **Name**: Muhammad Ilyas.
- **Email**: Muhammad.ilyas@vu.edu.pk.
- **Teams**: ilyas.vu@outlook.com.
