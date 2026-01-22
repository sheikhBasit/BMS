import pytest
from models import Book, BorrowRequest, User

def login(client, username, password):
    return client.post('/login', data=dict(
        username=username,
        password=password
    ), follow_redirects=True)

def test_login_failure(client, init_database):
    response = login(client, 'testuser', 'wrongpassword')
    assert response.status_code == 200
    assert b'Invalid username or password' in response.data

def test_duplicate_registration(client, init_database):
    # Register 'testuser' again (already exists from init_database)
    response = client.post('/register', data=dict(
        username='testuser',
        email='newemail@example.com',
        password='password',
        role='Member'
    ), follow_redirects=True)
    assert response.status_code == 200
    assert b'Username already exists' in response.data

def test_unauthorized_access(client):
    # Try accessing protected routes without login
    protected_routes = ['/dashboard', '/add_book', '/admin']
    for route in protected_routes:
        response = client.get(route, follow_redirects=True)
        assert b'Login' in response.data  # Should redirect to login page

def test_reject_request_workflow(client, init_database):
    # testuser adds a book
    login(client, 'testuser', 'userpass')
    client.post('/add_book', data=dict(title='Reject Me', author='Me', category='Test', type='Physical'), follow_redirects=True)
    logout(client)
    
    # admin borrows it
    login(client, 'admin', 'adminpass')
    book = Book.query.filter_by(title='Reject Me').first()
    client.post(f'/request_borrow/{book.id}', data=dict(
        date='2023-01-01',
        time='12:00',
        location='Library'
    ), follow_redirects=True)
    logout(client)
    
    # testuser rejects it
    login(client, 'testuser', 'userpass')
    req = BorrowRequest.query.filter_by(book_id=book.id).first()
    response = client.post(f'/handle_request/{req.id}', data=dict(action='reject'), follow_redirects=True)
    
    assert response.status_code == 200
    assert req.request_status == 'Rejected'
    assert book.status == 'Available' # Should remain available if rejected (or become available)

def test_digital_book_add(client, init_database):
    login(client, 'testuser', 'userpass')
    response = client.post('/add_book', data=dict(
        title='Digital Book',
        author='Tech Author',
        category='Tech',
        type='Digital',
        file_link='http://example.com/download'
    ), follow_redirects=True)
    
    book = Book.query.filter_by(title='Digital Book').first()
    assert book is not None
    assert book.type == 'Digital'
    assert book.file_link == 'http://example.com/download'

def logout(client):
    return client.get('/logout', follow_redirects=True)
