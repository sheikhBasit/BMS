# BookShare - Quick Reference Guide

## 🔑 Login Credentials

### Admin Account
- **Username:** `admin`
- **Password:** `admin123`
- **Permissions:** Full access, can edit/delete any book, view analytics

### Test Member Account
- **Username:** `tester1`
- **Password:** `tester123`
- **Permissions:** Standard user, can add/edit/delete own books

---

## 🚀 How to Run

```bash
# Navigate to project directory
cd /home/basitdev/BMS

# Activate virtual environment
source venv/bin/activate

# Run the application
python app.py
```

Application will be available at: **http://127.0.0.1:5000**

---

## 📚 Main Features

### For All Users
1. **Browse Books** - Public index page with search
2. **View Book Details** - Click any book card to see full details
3. **Register/Login** - Create account or sign in
4. **Like Books** - One-time like/unlike with visual feedback

### For Members
1. **Add Books** 
   - Physical or Digital types
   - Upload PDFs (max 16MB)
   - Select from 16 predefined categories
   - Add descriptions and locations
   
2. **Edit/Delete Own Books**
   - Full control over shared books
   - Soft delete (data preserved)
   
3. **Borrow Books**
   - Request to borrow with date/time
   - Cannot select past dates
   
4. **My Dashboard**
   - View shared books
   - Manage incoming requests
   - Track borrowed books
   
5. **My Likes**
   - See all liked books in one place

### For Admins
1. **Edit Any Book** - Universal edit permissions
2. **Delete Any Book** - Can remove any content
3. **Admin Dashboard**
   - User/book/request statistics
   - Interactive charts (Chart.js)
   - Visual metrics with gradients
4. **Manage All Requests** - Approve/reject borrows

---

## 🎨 UI Features

### Modern Design
- Dark theme with glassmorphism
- Smooth hover effects (reduced 3D intensity)
- Responsive grid layouts
- Page-specific backgrounds

### Alerts
- SweetAlert2 with custom styling
- Dynamic icons (✓, ✗, ⚠, ℹ)
- Auto-dismiss after 3 seconds
- Gradient backgrounds

### Forms
- HTML5 validation
- Visual feedback
- Drag-and-drop file upload
- Category dropdowns

---

## 📝 Validations

### Registration
- Username: 3-20 chars, alphanumeric + underscore
- Email: Valid format required
- Password: Minimum 6 characters

### Books
- Title: 2-200 characters
- Author: 2-200 characters
- Category: Must select from dropdown (16 options)
- File Size: Max 16MB for digital books

### Borrow Requests
- Date: Cannot be in the past
- Time: If today, must be in the future

---

## 📂 File Structure

```
BMS/
├── app.py                 # Main Flask application
├── models.py              # Database models
├── config.py              # Configuration
├── seed_db.py             # Database seeding
├── static/
│   ├── style.css          # Main stylesheet
│   └── uploads/           # Digital book PDFs
├── templates/
│   ├── base.html          # Base template
│   ├── index.html         # Public search page
│   ├── login.html
│   ├── register.html
│   ├── add_book.html
│   ├── edit_book.html
│   ├── book_detail.html   # Detailed book view
│   ├── my_likes.html      # User's liked books
│   ├── dashboard.html     # Member dashboard
│   ├── admin.html         # Admin dashboard
│   └── ...
└── instance/
    └── bookshare.db       # SQLite database
```

---

## 🔄 Common Workflows

### Adding a Physical Book
1. Login → Dashboard
2. Click "Add New Book"
3. Select "Physical" type
4. Enter title, author, category (dropdown)
5. Add description and location
6. Submit

### Adding a Digital Book
1. Login → Dashboard
2. Click "Add New Book"
3. Select "Digital" type
4. Enter title, author, category
5. Drag & drop PDF (or click to browse)
6. Submit

### Viewing Book Details
1. Browse index page
2. Click any book card
3. View full details with embedded PDF (if digital)
4. Like/unlike, edit, delete, or request borrow

### Admin Analytics
1. Login as admin
2. Navigate to "Admin" in nav bar
3. View metric cards (users, books, requests, likes)
4. Scroll to see charts:
   - Books by Type (doughnut chart)
   - Book Status (bar chart)

---

## 🛠️ Database Commands

### Reset Database
```bash
# Delete existing database
rm instance/bookshare.db

# Seed with fresh data
python seed_db.py
```

### Check Database
```bash
# Open SQLite
sqlite3 instance/bookshare.db

# View tables
.tables

# View users
SELECT * FROM user;

# View books
SELECT * FROM book WHERE is_deleted = 0;

# Exit
.quit
```

---

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Kill process on port 5000
fuser -k 5000/tcp

# Then restart app
python app.py
```

### File Upload Not Working
- Check `static/uploads` directory exists
- Verify file size is under 16MB
- Ensure PDF format

### Charts Not Displaying
- Check browser console for errors
- Verify Chart.js CDN is loading
- Ensure data exists in database

---

## 📊 Book Categories

The system supports 16 predefined categories:

1. Fiction
2. Science
3. Technology
4. History
5. Biography
6. Fantasy
7. Mystery
8. Romance
9. Thriller
10. Self-Help
11. Business
12. Art
13. Poetry
14. Philosophy
15. Travel
16. Other

---

## 🎨 CSS Variables

Customize the theme by editing these in `style.css`:

```css
:root {
    --bg-gradient: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    --card-bg: rgba(255, 255, 255, 0.05);
    --card-border: rgba(255, 255, 255, 0.1);
    --text-color: #ecf0f1;
    --text-muted: #95a5a6;
    --primary: #6c5ce7;
    --secondary: #00cec9;
}
```

---

## 📱 Responsive Breakpoints

- **Desktop:** > 1024px (multi-column grid)
- **Tablet:** 768px - 1024px (adjusted spacing)
- **Mobile:** < 768px (single-column grid)

---

## ✅ Testing Checklist

- [x] Register new user
- [x] Login with valid credentials
- [x] Add physical book
- [x] Add digital book with PDF
- [x] Edit own book
- [x] Delete own book (soft delete)
- [x] Like/unlike books
- [x] View My Likes page
- [x] View book detail page
- [x] Request to borrow book
- [x] Admin: Edit any book
- [x] Admin: Delete any book
- [x] Admin: View dashboard charts
- [x] Date/time validation
- [x] File size validation
- [x] Category dropdown validation

---

## 🎬 Browser Recording

A complete walkthrough is available in:
`bookshare_updates_test_<timestamp>.webp`

This shows:
- Homepage with refined 3D effects
- Admin dashboard with charts
- Add book with category dropdown
- Edit book with category dropdown
- My Likes page
- User dashboard column layout

---

**Need Help?** Refer to `FEATURE_IMPLEMENTATION_SUMMARY.md` for detailed technical documentation.
