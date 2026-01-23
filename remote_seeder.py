
import requests
import random
import time

BASE_URL = "https://bms-three-peach.vercel.app"

# Data for seeding
USERNAMES = [f"user_{i}" for i in range(1, 16)]
EMAILS = [f"user_{i}@example.com" for i in range(1, 16)]
PASSWORD = "Password123!"

CATEGORIES = [
    'Fiction', 'Non-Fiction', 'Science', 'Technology', 
    'History', 'Biography', 'Self-Help', 'Business',
    'Art', 'Philosophy', 'Religion', 'Mystery',
    'Romance', 'Thriller', 'Fantasy', 'Other'
]

BOOKS_DATA = [
    ("The Midnight Library", "Matt Haig", "Fiction", "Physical", "Neighborhood Shelf", "A place between life and death."),
    ("Atomic Habits", "James Clear", "Self-Help", "Digital", "https://example.com/atomic.pdf", "Tiny changes, remarkable results."),
    ("Deep Work", "Cal Newport", "Business", "Physical", "Office Lobby", "Focus in a distracted world."),
    ("Sapiens", "Yuval Noah Harari", "History", "Digital", "https://example.com/sapiens.pdf", "A brief history of humankind."),
    ("Clean Code", "Robert C. Martin", "Technology", "Physical", "Tech Hub shelf 4", "Art of software craftsmanship."),
    ("The Alchemist", "Paulo Coelho", "Fiction", "Physical", "Coffee Shop Basket", "Follow your dreams."),
    ("Project Hail Mary", "Andy Weir", "Science", "Digital", "https://example.com/hailmary.pdf", "Interstellar survival story."),
    ("The Silent Patient", "Alex Michaelides", "Thriller", "Physical", "Mystery Section", "A woman's act of violence against her husband."),
    ("Educated", "Tara Westover", "Biography", "Digital", "https://example.com/educated.pdf", "A memoir of struggle and survival."),
    ("Zero to One", "Peter Thiel", "Business", "Physical", "Startup Incubator", "Notes on startups and the future."),
    ("The Psychology of Money", "Morgan Housel", "Finance", "Digital", "https://example.com/money.pdf", "Timeless lessons on wealth and greed."),
    ("Circe", "Madeline Miller", "Fantasy", "Physical", "Mythology Shelf", "The goddess Circe tells her story."),
    ("Hyperfocus", "Chris Bailey", "Self-Help", "Physical", "Reading Room", "How to manage your attention."),
    ("The Pragmatic Programmer", "Andrew Hunt", "Technology", "Digital", "https://example.com/pragmatic.pdf", "From Journeyman to Master."),
    ("Becoming", "Michelle Obama", "Biography", "Physical", "Main Library", "The life of the former First Lady."),
    ("Dune", "Frank Herbert", "Fantasy", "Digital", "https://example.com/dune.pdf", "Epic desert politics."),
    ("1984", "George Orwell", "Fiction", "Physical", "Classic Section", "Dystopian future."),
    ("Thinking, Fast and Slow", "Daniel Kahneman", "Science", "Digital", "https://example.com/thinking.pdf", "Two systems of thought."),
    ("The Great Gatsby", "F. Scott Fitzgerald", "Fiction", "Physical", "Classic Shelf A", "The Jazz Age."),
    ("Meditations", "Marcus Aurelius", "Philosophy", "Digital", "https://example.com/meditations.pdf", "Stoic philosophy."),
    ("The Art of War", "Sun Tzu", "History", "Digital", "https://example.com/artofwar.pdf", "Ancient military treatise."),
    ("Stiff", "Mary Roach", "Science", "Physical", "Science Wing", "Curious lives of human cadavers."),
    ("Man's Search for Meaning", "Viktor Frankl", "Philosophy", "Physical", "Psychology Section", "Survival in Nazi camps."),
    ("The Lean Startup", "Eric Ries", "Business", "Digital", "https://example.com/lean.pdf", "Continuous innovation.")
]

def seed():
    session_pool = []
    book_ids = []

    print(f"--- Seeding {len(USERNAMES)} Users ---")
    for i in range(len(USERNAMES)):
        s = requests.Session()
        username = USERNAMES[i]
        email = EMAILS[i]
        
        # 1. Register
        print(f"Registering {username}...")
        reg_data = {
            'username': username,
            'email': email,
            'password': PASSWORD
        }
        res = s.post(f"{BASE_URL}/register", data=reg_data, allow_redirects=True)
        if "Logout" in res.text or "Index" in res.url:
            print(f"Successfully registered and logged in {username}")
        else:
            # Maybe already exists, try logging in
            print(f"Registration might have failed (user exists?), trying login...")
            login_data = {
                'username': username,
                'password': PASSWORD
            }
            res = s.post(f"{BASE_URL}/login", data=login_data, allow_redirects=True)
            if "Logout" in res.text:
                print(f"Logged in as {username}")
            else:
                print(f"Failed to log in as {username}")
                continue
        
        session_pool.append((s, username))

        # 2. Add 2 Books for each user
        for _ in range(2):
            if not BOOKS_DATA: break
            title, author, cat, btype, loc_link, desc = BOOKS_DATA.pop(0)
            print(f"Adding book '{title}' by {username}...")
            
            # Note: The server expects 'type' as Physical/Digital, and for digital 'file_link'
            book_payload = {
                'title': title,
                'author': author,
                'category': cat if cat in CATEGORIES else 'Other',
                'type': btype,
                'description': desc
            }
            if btype == 'Digital':
                book_payload['file_link'] = loc_link
            else:
                book_payload['location'] = loc_link
                
            res = s.post(f"{BASE_URL}/add_book", data=book_payload, allow_redirects=True)
            
            # Since we can't easily get the ID from the response (it redirects to index),
            # we'll have to find it in the index or just assume it's there.
            # Actually, the user wants us to share books too. 
            # Let's scrape the index to find book IDs.
            
    print("--- Scraping Book IDs for borrowing ---")
    # Use one session to get all books
    s = session_pool[0][0]
    res = s.get(f"{BASE_URL}/index")
    # Very simple scraping of book detail links: /book/<id>
    import re
    book_ids = re.findall(r'/book/(\d+)', res.text)
    book_ids = list(set(book_ids))
    print(f"Found {len(book_ids)} books on the index.")

    print(f"--- Creating {len(USERNAMES)} Borrow Requests ---")
    # We want ~15-20 requests
    for _ in range(20):
        # Pick a random session (borrower)
        s, username = random.choice(session_pool)
        if not book_ids: break
        
        target_id = random.choice(book_ids)
        
        # Check if it's a digital or physical book (optional, but let's just try)
        # Digital borrow is a GET, Physical is a POST
        
        # Let's hit the book page first to see if it's available or owned by current user
        res = s.get(f"{BASE_URL}/book/{target_id}")
        if f"Owner: {username}" in res.text or "Borrowed" in res.text:
            continue # Can't borrow own or already borrowed
            
        if "Digital Product" in res.text or "https://" in res.text:
            # Digital
            print(f"User {username} borrowing digital book {target_id}...")
            s.get(f"{BASE_URL}/request_borrow/{target_id}", allow_redirects=True)
        else:
            # Physical
            print(f"User {username} requesting physical book {target_id}...")
            req_data = {
                'date': '2026-02-15',
                'time': '14:00',
                'location': 'Downtown Park'
            }
            s.post(f"{BASE_URL}/request_borrow/{target_id}", data=req_data, allow_redirects=True)

    print("--- Seeding Complete ---")

if __name__ == "__main__":
    seed()
