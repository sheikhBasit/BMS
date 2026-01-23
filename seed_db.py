from app import app, db
from models import User, Book, BorrowRequest
from werkzeug.security import generate_password_hash
import random

def seed_database(force_reset=False):
    with app.app_context():
        # Clean slate only if forced
        if force_reset:
            print("Cleaning database...")
            db.drop_all()
            db.create_all()
        else:
            db.create_all()
        
        # Check if users already exist to avoid duplicate errors if not resetting
        # Individual User Check & Creation
        print("Ensuring seed users exist...")
        users_data = [
            ('admin', 'admin@bms.com', 'admin'),
            ('alice', 'alice@example.com', 'member'),
            ('bob', 'bob@example.com', 'member'),
            ('charlie', 'charlie@example.com', 'member'),
            ('david', 'david@example.com', 'member'),
            ('eve', 'eve@example.com', 'member')
        ]
        
        users_objs = []
        for username, email, role in users_data:
            u = User.query.filter(User.username.ilike(username)).first()
            if not u:
                u = User(username=username, email=email, role=role.lower())
                if username == 'admin':
                    u.set_password('admin123')
                else:
                    u.set_password('password')
                db.session.add(u)
                db.session.commit()
                print(f"Created user: {username}")
            else:
                # Normalize role for existing users
                if u.role != role.lower():
                    u.role = role.lower()
                    db.session.commit()
            users_objs.append(u)
        
        # Ensure we have the user objects available
        if not users_objs:
            users_objs = User.query.all()
        
        if not users_objs:
            print("ERROR: No users found.")
            return

        # Create Books only if count is low or we want to ensure these specific classics exist
        print("Ensuring seed books exist...")
        
        # Helper to get random user
        def get_owner():
            if len(users_objs) <= 1:
                return users_objs[0]
            # Return a random user excluding the admin if possible
            non_admins = [u for u in users_objs if u.username != 'admin']
            return random.choice(non_admins if non_admins else users_objs)
            
        book_list = [
            ("the great gatsby", "f. scott fitzgerald", "fiction", "physical", None, "main library, shelf a", "classic novel of the jazz age."),
            ("to kill a mockingbird", "harper lee", "fiction", "physical", None, "community center drop-off", "powerful story of racial injustice."),
            ("1984", "george orwell", "fiction", "physical", None, "westside book club", "dystopian social science fiction."),
            ("pride and prejudice", "jane austen", "fiction", "physical", None, "available on weekends", "romantic novel of manners."),
            ("the catcher in the rye", "j.d. salinger", "fiction", "physical", None, "coffee shop downtown", "a story of teenage alienation."),
            ("sapiens", "yuval noah harari", "non-fiction", "digital", "https://upload.wikimedia.org/wikipedia/commons/2/25/Sapiens_A_Brief_History_of_Humankind.pdf", None, "a brief history of humankind."),
            ("clean code", "robert c. martin", "technology", "physical", None, "tech hub office", "a handbook of agile software craftsmanship."),
            ("the pragmatic programmer", "andrew hunt", "technology", "digital", "https://www.cin.ufpe.br/~sugar/files/The%20Pragmatic%20Programmer%20-%20From%20Journeyman%20to%20Master.pdf", None, "from journeyman to master."),
            ("introduction to algorithms", "thomas h. cormen", "technology", "physical", None, "university lab", "comprehensive guide to algorithms."),
            ("design patterns", "erich gamma", "technology", "physical", None, "dev lounge", "elements of reusable object-oriented software."),
            ("a short history of nearly everything", "bill bryson", "science", "digital", "http://www.metaphysicspirit.com/books/A%20Short%20History%20of%20Nearly%20Everything.pdf", None, "bill bryson explains science to the layperson."),
            ("cosmos", "carl sagan", "science", "physical", None, "science museum gift shop", "the story of cosmic evolution."),
            ("the art of war", "sun tzu", "history", "digital", "https://sites.ualberta.ca/~enoch/Readings/The_Art_of_War.pdf", None, "ancient chinese military treatise."),
            ("guns, germs, and steel", "jared diamond", "history", "physical", None, "history dept.", "the fates of human societies."),
            ("thinking, fast and slow", "daniel kahneman", "non-fiction", "physical", None, "psychology wing", "system 1 and system 2 thinking."),
            ("brave new world", "aldous huxley", "fiction", "physical", None, "shelf b-2", "a chilling vision of a consumerist society."),
            ("the hobbit", "j.r.r. tolkien", "fantasy", "physical", None, "children's section", "a great adventure in middle-earth."),
            ("the alchemist", "paulo coelho", "fiction", "digital", "https://example.com/alchemist.pdf", None, "a story about following your dreams."),
            ("deep work", "cal newport", "self-help", "physical", None, "reading corner", "rules for focused success in a distracted world."),
            ("atomic habits", "james clear", "self-help", "digital", "https://example.com/habits.pdf", None, "an easy way to build good habits."),
            ("the silent patient", "alex michaelides", "thriller", "physical", None, "mystery shelf", "a shocking psychological thriller."),
            ("educated", "tara westover", "biography", "physical", None, "memoir section", "a memoir of struggle and survival."),
            ("becoming", "michelle obama", "biography", "digital", "https://example.com/becoming.pdf", None, "the life of the former first lady."),
            ("siddhartha", "hermann hesse", "philosophy", "physical", None, "spirituality a isle", "a journey toward self-discovery."),
            ("the republic", "plato", "philosophy", "digital", "https://example.com/republic.pdf", None, "classic work of political theory."),
            ("meditations", "marcus aurelius", "philosophy", "physical", None, "classic shelf", "stoic philosophy from the roman emperor."),
            ("the selfish gene", "richard dawkins", "science", "physical", None, "biology section", "revolutionary view of evolution."),
            ("astrophysics for people in a hurry", "neil degrasse tyson", "science", "digital", "https://example.com/astro.pdf", None, "the universe explained briefly."),
            ("the wright brothers", "david mccullough", "history", "physical", None, "aviation section", "the story of flight."),
            ("steve jobs", "walter isaacson", "biography", "physical", None, "tech history", "the biography of apple's founder."),
            ("zero to one", "peter thiel", "business", "digital", "https://example.com/zero.pdf", None, "notes on startups and the future."),
            ("the lean startup", "eric ries", "business", "physical", None, "startup lab", "modern approach to building companies."),
            ("good to great", "jim collins", "business", "physical", None, "management shelf", "why some companies leap and others don't."),
            ("foundation", "isaac asimov", "fantasy", "digital", "https://example.com/foundation.pdf", None, "the start of the epic galactic empire."),
            ("dune", "frank herbert", "fantasy", "physical", None, "sci-fi shelf", "epic tale of desert politics and spice."),
            ("big magic", "elizabeth gilbert", "self-help", "physical", None, "creativity wing", "creative living beyond fear."),
            ("the power of habit", "charles duhigg", "non-fiction", "digital", "https://example.com/habit.pdf", None, "why we do what we do."),
            ("outliers", "malcolm gladwell", "non-fiction", "physical", None, "sociology section", "the story of success."),
            ("the book thief", "markus zusak", "fiction", "physical", None, "historical fiction", "narrated by death in nazi germany."),
            ("life of pi", "yann mantel", "fiction", "digital", "https://example.com/pi.pdf", None, "a boy and a tiger on a lifeboat."),
            ("dracula", "bram stoker", "mystery", "physical", None, "gothic section", "the original vampire story."),
            ("sherlock holmes", "arthur conan doyle", "mystery", "digital", "https://example.com/holmes.pdf", None, "the world's greatest detective."),
            ("gone girl", "gillian flynn", "thriller", "physical", None, "thriller shelf", "a dark and twisty marriage story."),
            ("the da vinci code", "dan brown", "mystery", "digital", "https://example.com/davinci.pdf", None, "a religious mystery thriller."),
            ("life 3.0", "max tegmark", "technology", "physical", None, "ai section", "being human in the age of ai."),
            ("superintelligence", "nick bostrom", "technology", "digital", "https://example.com/super.pdf", None, "paths, dangers, and strategies for ai."),
            ("the information", "james gleick", "technology", "physical", None, "history of tech", "a history, a theory, a flood."),
            ("why we sleep", "matthew walker", "science", "physical", None, "health section", "the power of sleep and dreams."),
            ("lab girl", "hope jahren", "science", "digital", "https://example.com/labgirl.pdf", None, "a story of trees and discovery."),
            ("the gene", "siddhartha mukherjee", "science", "physical", None, "genetics shelf", "an intimate history of the gene."),
            ("man's search for meaning", "viktor frankl", "philosophy", "physical", None, "psychology a isle", "psychologist's experience in camps."),
            ("beyond good and evil", "friedrich nietzsche", "philosophy", "digital", "https://example.com/evil.pdf", None, "prelude to a philosophy of the future."),
            ("the stranger", "albert camus", "philosophy", "physical", None, "existentialist section", "the classic of absurdism.")
        ]
        
        books_added = 0
        for title, author, cat, btype, link, loc, desc in book_list:
            exists = Book.query.filter_by(title=title, author=author).first()
            if not exists:
                b = Book(title=title, author=author, category=cat, type=btype, file_link=link, owner=get_owner(), location=loc, description=desc)
                db.session.add(b)
                books_added += 1
        
        db.session.commit()
        print(f"Added {books_added} new books.")
        
        # Borrow Requests: Ensure we have at least 15 requests
        request_count = BorrowRequest.query.count()
        if request_count < 15:
            print(f"Current requests: {request_count}. Adding more to reach target...")
            current_books = Book.query.filter_by(type='physical', is_deleted=False).all()
            non_admins = [u for u in users_objs if u.username != 'admin']
            if current_books and non_admins:
                added_reqs = 0
                for _ in range(20): # Try multiple times to get unique pairs
                    if request_count + added_reqs >= 15:
                        break
                    book = random.choice(current_books)
                    borrower = random.choice(non_admins)
                    
                    # Check if this borrower already requested this book
                    existing = BorrowRequest.query.filter_by(book_id=book.id, borrower_id=borrower.id).first()
                    
                    if book.owner != borrower and not existing:
                        req = BorrowRequest(
                            book=book,
                            borrower=borrower,
                            proposed_date="2026-02-01",
                            proposed_time="10:00",
                            proposed_location="community center",
                            request_status="pending"
                        )
                        db.session.add(req)
                        added_reqs += 1
                db.session.commit()
                print(f"Added {added_reqs} sample requests.")

        # Re-distribute Ownership if needed
        # Often books are seeded as 'admin', let's spread the love
        admin_books = Book.query.filter(Book.owner.has(username='admin')).all()
        if len(admin_books) > 5:
            print(f"Admin owns {len(admin_books)} books. Re-distributing...")
            non_admins = [u for u in users_objs if u.username != 'admin']
            if non_admins:
                for book in admin_books[5:]: # Keep only 5 for admin
                    book.owner = random.choice(non_admins)
                db.session.commit()
                print("Ownership re-distributed.")
        
        print("Seeding/Check Complete!")

if __name__ == '__main__':
    seed_database(force_reset=False)
