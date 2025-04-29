from app import create_app, db
import MySQLdb
from flask import current_app
import re

def update_database():
    app = create_app()
    with app.app_context():
        try:
            # Get database connection details from app config
            db_uri = app.config['SQLALCHEMY_DATABASE_URI']
            
            # Parse connection string using regex
            match = re.match(r'mariadb://([^:]+):([^@]+)@([^:]+):\d+/(.+)', db_uri)
            if not match:
                raise ValueError(f"Invalid database URI format: {db_uri}")
                
            db_user, db_pass, db_host, db_name = match.groups()

            print(f"Connecting to database {db_name} on {db_host} as {db_user}")

            # Connect directly to MySQL
            conn = MySQLdb.connect(
                host=db_host,
                user=db_user,
                passwd=db_pass,
                db=db_name
            )
            cursor = conn.cursor()

            # Add new columns one by one with error handling
            columns = [
                ("role", "VARCHAR(50) DEFAULT 'user'"),
                ("temp_password", "VARCHAR(128)"),
                ("temp_password_expiry", "DATETIME"),
                ("created_at", "DATETIME DEFAULT CURRENT_TIMESTAMP"),
                ("last_login", "DATETIME")
            ]

            for column, definition in columns:
                try:
                    cursor.execute(f"ALTER TABLE users ADD COLUMN {column} {definition};")
                    print(f"Added column {column}")
                except MySQLdb.OperationalError as e:
                    if "Duplicate column name" in str(e):
                        print(f"Column {column} already exists")
                    else:
                        print(f"Error adding column {column}: {e}")

            conn.commit()
            print("Database update completed successfully")

        except Exception as e:
            print(f"Error updating database: {e}")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

if __name__ == "__main__":
    update_database() 