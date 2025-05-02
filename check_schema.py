import sqlite3

def check_schema():
    # Connect to the database
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    
    try:
        # Get schema information for the violations table
        cursor.execute('PRAGMA table_info(violations)')
        columns = cursor.fetchall()
        
        print("Violations table schema:")
        for col in columns:
            print(f"  {col[1]} ({col[2]}) {'PRIMARY KEY' if col[5] else ''}")
        
        # Check if public_id column exists
        public_id_exists = any(col[1] == 'public_id' for col in columns)
        print(f"\nPublic ID column exists: {public_id_exists}")
        
        # If public_id exists, check if any violations have NULL values
        if public_id_exists:
            cursor.execute('SELECT COUNT(*) FROM violations WHERE public_id IS NULL')
            null_count = cursor.fetchone()[0]
            print(f"Violations with NULL public_id: {null_count}")
            
            cursor.execute('SELECT id, public_id FROM violations LIMIT 3')
            sample = cursor.fetchall()
            print("\nSample violation IDs and public_ids:")
            for row in sample:
                print(f"  ID: {row[0]}, public_id: {row[1]}")
    
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_schema() 