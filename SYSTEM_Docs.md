# System Docs / Technical Guide

## 1. Overview
The **Book Sharing Platform (BMS)** is a Flask-based web application allowing users (Members) to share and borrow physical books and digital resources. It features a modern 3D-styled user interface, an Admin dashboard, and utilizes various third-party services for functionality and aesthetics.

## 2. Technology Stack

### Backend
- **Flask**: The core microframework handling routing, templating, and request logic.
- **SQLAlchemy (Flask-SQLAlchemy)**: ORM for interacting with the SQLite database.
- **Flask-Login**: Manages user sessions, authentication, and access control.
- **Werkzeug**: Handles secure password hashing and file verification.

### Frontend
- **HTML5/CSS3**: Custom styling with `static/style.css` implementing:
  - **Glassmorphism**: Translucent card backgrounds.
  - **3D Effects**: `preserve-3d` and `transform: translateZ` for depth.
- **JavaScript**:
  - **Vanilla-Tilt.js**: Provides the 3D tilt effect on book cards.
  - **Canvas-Confetti**: Renders celebratory animations.
  - **Vanilla JS**: Handles interaction logic (Likes, Search).

### Integrations
- **Cloudinary**: Handles storage of uploaded digital books (PDFs, Images). This ensures scalable file hosting without burdening the local server.
- **Picsum**: Generates unique, consistent book covers based on Book ID (`https://picsum.photos/seed/{id}`).
- **Unsplash**: Provides the high-quality immersive background image.
- **Google Fonts (Outfit)**: Provides the modern typography.

## 3. Architecture & Key Workflows

### Database Models (`models.py`)
1.  **User**: Stores `username`, `email`, `password_hash`, `role` (Admin/Member), and `is_blocked` status.
2.  **Book**: Stores `title`, `author`, `category`, `type` (Physical/Digital), `status` (Available/Borrowed/Returned), `file_link`, `filename`, and `likes`.
3.  **BorrowRequest**: Joint table linking `Book` and `User` (borrower) with exchange details (date/time/location) and `status`.

### Key Workflows
1.  **Digital Borrowing**:
    - **Step 1**: User finds digital book.
    - **Step 2**: Clicks "Get Digital".
    - **Step 3**: System immediately creates an `Accepted` BorrowRequest.
    - **Step 4**: Confetti triggers! File link becomes available in Dashboard.
    
2.  **Physical Borrowing**:
    - **Step 1**: User requests book with Date/Time/Location proposal.
    - **Step 2**: Owner sees request in Dashboard.
    - **Step 3**: Owner can **Accept**, **Reject**, or **Suggest Changes**.
    - **Step 4**: If Accepted, status moves to Borrowed.
    - **Step 5**: Once returned, Owner marks as Returned (Available).

3.  **Admin Functions**:
    - Manage Users: Block/Unblock abusive users.
    - Manage Content: Delete any book in the system.
    - Metrics: View live counts of users, books, and activity.

## 4. Environment Variables / Configuration
- **Cloudinary**: requires `cloud_name`, `api_key`, `api_secret` in `app.py`.
- **Secret Key**: `app.config['SECRET_KEY']` used for sessions.
- **Database URI**: Default is `sqlite:///bms.db`.

## 5. How interactive features work
- **Likes**: A JavaScript `fetch` call hits `/api/like/<id>`, updates the database counter, and returns the new count. The frontend updates the DOM and triggers a small confetti burst on the button.
- **Tilt**: `vanilla-tilt.js` scans for elements with `data-tilt` and applies CSS transforms based on mouse position.

---
*Maintained by the BMS Dev Team*
