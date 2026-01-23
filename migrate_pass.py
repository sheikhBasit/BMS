from app import app, db
from sqlalchemy import text

def migrate_password_hash():
    with app.app_context():
        print("Altering user table to increase password_hash length...")
        try:
            # Check if we are on Postgres or SQLite
            uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
            if 'postgresql' in uri or 'postgres' in uri:
                db.session.execute(text('ALTER TABLE "user" ALTER COLUMN password_hash TYPE VARCHAR(512)'))
            else:
                # SQLite doesn't support ALTER COLUMN TYPE easily, 
                # but usually it doesn't enforce length limits anyway
                print("SQLite detected, skipping ALTER COLUMN (not needed for length).")
            
            db.session.commit()
            print("Migration successful!")
        except Exception as e:
            db.session.rollback()
            print(f"Migration failed: {e}")

if __name__ == '__main__':
    migrate_password_hash()
