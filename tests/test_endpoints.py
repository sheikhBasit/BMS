import pytest
from models import Book, BorrowRequest, User

def login(client, username, password):
    return client.post('/login', data=dict(
        username=username,
        password=password
    ), follow_redirects=True)

def logout(client):
    return client.get('/logout', follow_redirects=True)

def test_register(client):
    response = client.post('/register', data=dict(
        username='newuser',
        email='new@example.com',
        password='password',
        role='Member'
    ), follow_redirects=True)
    assert response.status_code == 200
    assert User.query.filter_by(username='newuser').first() is not None

def test_login_logout(client, init_database):
    response = login(client, 'testuser', 'userpass')
    assert response.status_code == 200
    assert b'Welcome, testuser' in response.data
    
    response = logout(client)
    assert response.status_code == 200
    assert b'Login' in response.data

def test_add_book(client, init_database):
    login(client, 'testuser', 'userpass')
    response = client.post('/add_book', data=dict(
        title='The Great Gatsby',
        author='F. Scott Fitzgerald',
        category='Classic',
        type='Physical'
    ), follow_redirects=True)
    
    assert response.status_code == 200
    assert Book.query.filter_by(title='The Great Gatsby').first() is not None

def test_index_search(client, init_database):
    login(client, 'testuser', 'userpass')
    # Add a book first
    client.post('/add_book', data=dict(title='Harry Potter', author='Rowling', category='Fantasy', type='Physical'), follow_redirects=True)
    
    response = client.get('/index?q=Potter')
    assert response.status_code == 200
    assert b'Harry Potter' in response.data
    
    # Simple check to ensure we don't match everything (unless DB is recycled properly)
    # Since we use in-memory DB per session/function scope might be needed if side effects.
    # conftest 'client' fixture re-creates DB per test, so it's clean.
    
    response = client.get('/index?q=Gatsby')
    assert b'Harry Potter' not in response.data

def test_borrow_request_workflow(client, init_database):
    # testuser adds a book
    login(client, 'testuser', 'userpass')
    client.post('/add_book', data=dict(title='Shared Book', author='Me', category='Test', type='Physical'), follow_redirects=True)
    logout(client)
    
    # admin (acting as another user) borrows it
    login(client, 'admin', 'adminpass')
    book = Book.query.filter_by(title='Shared Book').first()
    
    response = client.post(f'/request_borrow/{book.id}', data=dict(
        date='2023-01-01',
        time='12:00',
        location='Library'
    ), follow_redirects=True)
    assert response.status_code == 200
    assert BorrowRequest.query.filter_by(book_id=book.id).first() is not None
    logout(client)
    
    # testuser accepts it
    login(client, 'testuser', 'userpass')
    req = BorrowRequest.query.filter_by(book_id=book.id).first()
    response = client.post(f'/handle_request/{req.id}', data=dict(action='accept'), follow_redirects=True)
    
    assert response.status_code == 200
    assert req.request_status == 'Accepted'
    assert book.status == 'Borrowed'

def test_admin_dashboard(client, init_database):
    login(client, 'testuser', 'userpass')
    response = client.get('/admin')
    assert response.status_code == 403
    logout(client)
    
    login(client, 'admin', 'adminpass')
    response = client.get('/admin')
    assert response.status_code == 200
    assert b'All Users' in response.data
