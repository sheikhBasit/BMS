
import pytest
from models import Book, User, BookLike, BorrowRequest

def login(client, username, password):
    return client.post('/login', data=dict(
        username=username,
        password=password
    ), follow_redirects=True)

def test_edit_book(client, init_database):
    login(client, 'testuser', 'userpass')
    # Add a book first
    client.post('/add_book', data=dict(
        title='Original Title',
        author='Original Author',
        category='Fiction',
        type='Physical'
    ), follow_redirects=True)
    
    book = Book.query.filter_by(title='Original Title').first()
    
    # Edit the book
    response = client.post(f'/edit_book/{book.id}', data=dict(
        title='Updated Title',
        author='Updated Author',
        category='Science',
        description='Updated Description',
        location='Updated Location'
    ), follow_redirects=True)
    
    assert response.status_code == 200
    updated_book = Book.query.get(book.id)
    assert updated_book.title == 'Updated Title'
    assert updated_book.category == 'Science'

def test_delete_book(client, init_database):
    login(client, 'testuser', 'userpass')
    client.post('/add_book', data=dict(
        title='Book to Delete',
        author='Author',
        category='Fiction',
        type='Physical'
    ), follow_redirects=True)
    
    book = Book.query.filter_by(title='Book to Delete').first()
    
    # Delete the book
    response = client.post(f'/delete_book/{book.id}', follow_redirects=True)
    assert response.status_code == 200
    
    deleted_book = Book.query.get(book.id)
    assert deleted_book.is_deleted == True

def test_like_book_api(client, init_database):
    login(client, 'testuser', 'userpass')
    client.post('/add_book', data=dict(
        title='Likable Book',
        author='Author',
        category='Fiction',
        type='Physical'
    ), follow_redirects=True)
    
    book = Book.query.filter_by(title='Likable Book').first()
    
    # Like the book via API
    response = client.post(f'/api/like/{book.id}')
    assert response.status_code == 200
    data = response.get_json()
    assert data['likes'] == 1
    assert data['user_liked'] == True
    
    # Unlike the book
    response = client.post(f'/api/like/{book.id}')
    data = response.get_json()
    assert data['likes'] == 0
    assert data['user_liked'] == False

def test_admin_block_user(client, init_database):
    # Try to block user as non-admin
    login(client, 'testuser', 'userpass')
    user_to_block = User.query.filter_by(username='testuser').first()
    # Note: testuser trying to block themselves or another user? 
    # Let's say testuser tries to block admin (won't work anyway due to logic) 
    # or just try the endpoint.
    user_to_block = User.query.filter_by(username='testuser').first()
    response = client.post(f'/toggle_block_user/{user_to_block.id}', follow_redirects=True)
    assert response.status_code == 403
    
    client.get('/logout', follow_redirects=True)
    
    # Block user as admin
    login(client, 'admin', 'adminpass')
    response = client.post(f'/toggle_block_user/{user_to_block.id}', follow_redirects=True)
    assert response.status_code == 200
    assert User.query.get(user_to_block.id).is_blocked == True
    
    client.get('/logout', follow_redirects=True)
    
    # Try logging in as blocked user
    response = login(client, 'testuser', 'userpass')
    assert b'Your account has been blocked' in response.data

def test_book_detail_and_likes_page(client, init_database):
    login(client, 'testuser', 'userpass')
    client.post('/add_book', data=dict(
        title='Detailed Book',
        author='Author',
        category='Fiction',
        type='Physical'
    ), follow_redirects=True)
    book = Book.query.filter_by(title='Detailed Book').first()
    
    # View detail
    response = client.get(f'/book/{book.id}')
    assert response.status_code == 200
    assert b'Detailed Book' in response.data
    
    # Like it
    client.post(f'/api/like/{book.id}')
    
    # View my likes
    response = client.get('/my_likes')
    assert response.status_code == 200
    assert b'Detailed Book' in response.data

def test_search_categories(client, init_database):
    login(client, 'testuser', 'userpass')
    client.post('/add_book', data=dict(title='Sci Book', author='A', category='Science', type='Physical'), follow_redirects=True)
    client.post('/add_book', data=dict(title='Hist Book', author='B', category='History', type='Physical'), follow_redirects=True)
    
    # Search for Science
    response = client.get('/index?q=Science')
    assert b'Sci Book' in response.data
    assert b'Hist Book' not in response.data
