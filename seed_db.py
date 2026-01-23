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
        if not force_reset and User.query.filter_by(username='admin').first():
             users_objs = User.query.all()
             print("Users already exist, skipping user creation...")
        else:
             # Create Users
        print("Creating users...")
        users_data = [
            ('admin', 'admin@bms.com', 'Admin'),
            ('alice', 'alice@example.com', 'Member'),
            ('bob', 'bob@example.com', 'Member'),
            ('charlie', 'charlie@example.com', 'Member'),
            ('david', 'david@example.com', 'Member'),
            ('eve', 'eve@example.com', 'Member')
        ]
        
        users_objs = []
        for username, email, role in users_data:
            u = User(username=username, email=email, role=role)
            if username == 'admin':
                u.set_password('admin123')
            else:
                u.set_password('password')
            users_objs.append(u)
        
        db.session.add_all(users_objs)
        db.session.commit()
        
        # Create Books
        print("Creating books...")
        categories = ['Fiction', 'Non-Fiction', 'Science', 'Technology', 'History', 'Art']
        
        # Helper to get random user (excluding admin ideally, but fine for now)
        def get_owner():
            return random.choice(users_objs[1:]) # Skip admin
            
        book_list = [
            ("The Great Gatsby", "F. Scott Fitzgerald", "Fiction", "Physical", None, "Main Library, Shelf A", "Classic novel of the Jazz Age."),
            ("To Kill a Mockingbird", "Harper Lee", "Fiction", "Physical", None, "Community Center Drop-off", "Powerful story of racial injustice."),
            ("1984", "George Orwell", "Fiction", "Physical", None, "Westside Book Club", "Dystopian social science fiction."),
            ("Pride and Prejudice", "Jane Austen", "Fiction", "Physical", None, "Available on Weekends", "Romantic novel of manners."),
            ("The Catcher in the Rye", "J.D. Salinger", "Fiction", "Physical", None, "Coffee Shop Downtown", "A story of teenage alienation."),
            ("Sapiens", "Yuval Noah Harari", "Non-Fiction", "Digital", "https://upload.wikimedia.org/wikipedia/commons/2/25/Sapiens_A_Brief_History_of_Humankind.pdf", None, "A brief history of humankind."),
            ("Clean Code", "Robert C. Martin", "Technology", "Physical", None, "Tech Hub Office", "A Handbook of Agile Software Craftsmanship."),
            ("The Pragmatic Programmer", "Andrew Hunt", "Technology", "Digital", "https://www.cin.ufpe.br/~sugar/files/The%20Pragmatic%20Programmer%20-%20From%20Journeyman%20to%20Master.pdf", None, "From Journeyman to Master."),
            ("Introduction to Algorithms", "Thomas H. Cormen", "Technology", "Physical", None, "University Lab", "Comprehensive guide to algorithms."),
            ("Design Patterns", "Erich Gamma", "Technology", "Physical", None, "Dev Lounge", "Elements of Reusable Object-Oriented Software."),
            ("A Short History of Nearly Everything", "Bill Bryson", "Science", "Digital", "http://www.metaphysicspirit.com/books/A%20Short%20History%20of%20Nearly%20Everything.pdf", None, "Bill Bryson explains science to the layperson."),
            ("Cosmos", "Carl Sagan", "Science", "Physical", None, "Science Museum Gift Shop", "The story of cosmic evolution."),
            ("The Art of War", "Sun Tzu", "History", "Digital", "https://sites.ualberta.ca/~enoch/Readings/The_Art_of_War.pdf", None, "Ancient Chinese military treatise."),
            ("Guns, Germs, and Steel", "Jared Diamond", "History", "Physical", None, "History Dept.", "The Fates of Human Societies."),
            ("Thinking, Fast and Slow", "Daniel Kahneman", "Non-Fiction", "Physical", None, "Psychology Wing", "System 1 and System 2 thinking."),
            # Adding more to reach 50+
            ("Brave New World", "Aldous Huxley", "Fiction", "Physical", None, "Shelf B-2", "A chilling vision of a consumerist society."),
            ("The Hobbit", "J.R.R. Tolkien", "Fantasy", "Physical", None, "Children's Section", "A great adventure in Middle-earth."),
            ("The Alchemist", "Paulo Coelho", "Fiction", "Digital", "https://example.com/alchemist.pdf", None, "A story about following your dreams."),
            ("Deep Work", "Cal Newport", "Self-Help", "Physical", None, "Reading Corner", "Rules for focused success in a distracted world."),
            ("Atomic Habits", "James Clear", "Self-Help", "Digital", "https://example.com/habits.pdf", None, "An easy way to build good habits."),
            ("The Silent Patient", "Alex Michaelides", "Thriller", "Physical", None, "Mystery Shelf", "A shocking psychological thriller."),
            ("Educated", "Tara Westover", "Biography", "Physical", None, "Memoir Section", "A memoir of struggle and survival."),
            ("Becoming", "Michelle Obama", "Biography", "Digital", "https://example.com/becoming.pdf", None, "The life of the former First Lady."),
            ("Siddhartha", "Hermann Hesse", "Philosophy", "Physical", None, "Spirituality A isle", "A journey toward self-discovery."),
            ("The Republic", "Plato", "Philosophy", "Digital", "https://example.com/republic.pdf", None, "Classic work of political theory."),
            ("Meditations", "Marcus Aurelius", "Philosophy", "Physical", None, "Classic Shelf", "Stoic philosophy from the Roman Emperor."),
            ("The Selfish Gene", "Richard Dawkins", "Science", "Physical", None, "Biology Section", "Revolutionary view of evolution."),
            ("Astrophysics for People in a Hurry", "Neil deGrasse Tyson", "Science", "Digital", "https://example.com/astro.pdf", None, "The universe explained briefly."),
            ("The Wright Brothers", "David McCullough", "History", "Physical", None, "Aviation Section", "The story of flight."),
            ("Steve Jobs", "Walter Isaacson", "Biography", "Physical", None, "Tech History", "The biography of Apple's founder."),
            ("Zero to One", "Peter Thiel", "Business", "Digital", "https://example.com/zero.pdf", None, "Notes on startups and the future."),
            ("The Lean Startup", "Eric Ries", "Business", "Physical", None, "Startup Lab", "Modern approach to building companies."),
            ("Good to Great", "Jim Collins", "Business", "Physical", None, "Management Shelf", "Why some companies leap and others don't."),
            ("Foundation", "Isaac Asimov", "Fantasy", "Digital", "https://example.com/foundation.pdf", None, "The start of the epic galactic empire."),
            ("Dune", "Frank Herbert", "Fantasy", "Physical", None, "Sci-Fi Shelf", "Epic tale of desert politics and spice."),
            ("Big Magic", "Elizabeth Gilbert", "Self-Help", "Physical", None, "Creativity Wing", "Creative living beyond fear."),
            ("The Power of Habit", "Charles Duhigg", "Non-Fiction", "Digital", "https://example.com/habit.pdf", None, "Why we do what we do."),
            ("Outliers", "Malcolm Gladwell", "Non-Fiction", "Physical", None, "Sociology Section", "The story of success."),
            ("The Book Thief", "Markus Zusak", "Fiction", "Physical", None, "Historical Fiction", "Narrated by Death in Nazi Germany."),
            ("Life of Pi", "Yann Martel", "Fiction", "Digital", "https://example.com/pi.pdf", None, "A boy and a tiger on a lifeboat."),
            ("Dracula", "Bram Stoker", "Mystery", "Physical", None, "Gothic Section", "The original vampire story."),
            ("Sherlock Holmes", "Arthur Conan Doyle", "Mystery", "Digital", "https://example.com/holmes.pdf", None, "The world's greatest detective."),
            ("Gone Girl", "Gillian Flynn", "Thriller", "Physical", None, "Thriller Shelf", "A dark and twisty marriage story."),
            ("The Da Vinci Code", "Dan Brown", "Mystery", "Digital", "https://example.com/davinci.pdf", None, "A religious mystery thriller."),
            ("Life 3.0", "Max Tegmark", "Technology", "Physical", None, "AI Section", "Being human in the age of AI."),
            ("Superintelligence", "Nick Bostrom", "Technology", "Digital", "https://example.com/super.pdf", None, "Paths, dangers, and strategies for AI."),
            ("The Information", "James Gleick", "Technology", "Physical", None, "History of Tech", "A history, a theory, a flood."),
            ("Why We Sleep", "Matthew Walker", "Science", "Physical", None, "Health Section", "The power of sleep and dreams."),
            ("Lab Girl", "Hope Jahren", "Science", "Digital", "https://example.com/labgirl.pdf", None, "A story of trees and discovery."),
            ("The Gene", "Siddhartha Mukherjee", "Science", "Physical", None, "Genetics Shelf", "An intimate history of the gene."),
            ("Man's Search for Meaning", "Viktor Frankl", "Philosophy", "Physical", None, "Psychology A isle", "Psychologist's experience in camps."),
            ("Beyond Good and Evil", "Friedrich Nietzsche", "Philosophy", "Digital", "https://example.com/evil.pdf", None, "Prelude to a philosophy of the future."),
            ("The Stranger", "Albert Camus", "Philosophy", "Physical", None, "Existentialist Section", "The classic of absurdism.")
        ]
        
        books_objs = []
        for title, author, cat, btype, link, loc, desc in book_list:
            b = Book(title=title, author=author, category=cat, type=btype, file_link=link, owner=get_owner(), location=loc, description=desc)
            books_objs.append(b)
            
        db.session.add_all(books_objs)
        db.session.commit()
        
        # Create Requests
        print("Creating requests...")
        # Randomly create some requests
        for _ in range(5):
            book = random.choice(books_objs)
            borrower = random.choice(users_objs[1:])
            
            # Don't borrow own book
            if book.owner != borrower and book.status == 'Available' and book.type == 'Physical':
                req = BorrowRequest(
                    book=book,
                    borrower=borrower,
                    proposed_date="2026-02-01",
                    proposed_time="10:00",
                    proposed_location="Community Center",
                    request_status="Pending"
                )
                db.session.add(req)
                
        db.session.commit()
        print("Seeding Complete!")

if __name__ == '__main__':
    seed_database(force_reset=True)
