import sqlite3
import sys

def add_grid_column_field():
    """Add the grid_column field to the field_definitions table"""
    print("Adding grid_column field to field_definitions table...")
    
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    
    # Check if the column already exists
    cursor.execute("PRAGMA table_info(field_definitions)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'grid_column' in columns:
        print("grid_column field already exists.")
        conn.close()
        return
    
    # Add the column with a default value of 0 (full width)
    try:
        cursor.execute("ALTER TABLE field_definitions ADD COLUMN grid_column INTEGER DEFAULT 0")
        conn.commit()
        print("✅ Successfully added grid_column field to field_definitions table.")
    except Exception as e:
        print(f"❌ Error adding grid_column field: {str(e)}")
    finally:
        conn.close()

if __name__ == "__main__":
    add_grid_column_field()
    print("Done.") 