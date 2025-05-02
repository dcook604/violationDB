import sqlite3
import uuid

def update_public_ids():
    # Connect to the database
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    
    try:
        # Get all violations that don't have a public_id
        cursor.execute('SELECT id FROM violations')
        rows = cursor.fetchall()
        
        print(f"Found {len(rows)} violations to update")
        
        # Update each violation with a unique UUID
        for row in rows:
            vid = row[0]
            public_id = str(uuid.uuid4())
            cursor.execute('UPDATE violations SET public_id = ? WHERE id = ?', (public_id, vid))
            print(f"Updated violation {vid} with public_id {public_id}")
        
        # Commit the changes
        conn.commit()
        print("All violations updated with unique UUIDs")
    
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    update_public_ids() 