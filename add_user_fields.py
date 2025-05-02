from app import create_app, db
from app.models import User
from sqlalchemy import text

def run_migration():
    app = create_app()
    with app.app_context():
        # Check if the columns already exist
        try:
            result = db.session.execute(text("PRAGMA table_info(users)")).fetchall()
            columns = [r[1] for r in result]
            
            if 'first_name' not in columns:
                print("Adding first_name column to users table...")
                db.session.execute(text("ALTER TABLE users ADD COLUMN first_name VARCHAR(50)"))
            
            if 'last_name' not in columns:
                print("Adding last_name column to users table...")
                db.session.execute(text("ALTER TABLE users ADD COLUMN last_name VARCHAR(50)"))
                
            db.session.commit()
            print("Migration completed successfully!")
        except Exception as e:
            print(f"Error during migration: {e}")

if __name__ == "__main__":
    run_migration() 