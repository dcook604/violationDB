import sqlite3
import os
import sys

def check_current_schema():
    """Check the current schema of the settings table"""
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='settings'")
    schema = cursor.fetchone()[0]
    conn.close()
    
    print(f"Current schema:\n{schema}\n")
    return schema

def test_tls_update(value):
    """Test updating the TLS setting in the database"""
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    
    # First check current value
    cursor.execute("SELECT id, smtp_server, smtp_port, smtp_use_tls FROM settings WHERE id = 1")
    before = cursor.fetchone()
    
    if before:
        print(f"Before update:")
        print(f"  ID: {before[0]}")
        print(f"  SMTP Server: {before[1]}")
        print(f"  SMTP Port: {before[2]}")
        print(f"  SMTP Use TLS: {before[3]}")
    
    # Update the value
    cursor.execute("UPDATE settings SET smtp_use_tls = ? WHERE id = 1", (1 if value else 0,))
    conn.commit()
    
    # Check the updated value
    cursor.execute("SELECT id, smtp_server, smtp_port, smtp_use_tls FROM settings WHERE id = 1")
    after = cursor.fetchone()
    
    if after:
        print(f"\nAfter update (set to {1 if value else 0}):")
        print(f"  ID: {after[0]}")
        print(f"  SMTP Server: {after[1]}")
        print(f"  SMTP Port: {after[2]}")
        print(f"  SMTP Use TLS: {after[3]}")
    
    conn.close()
    
    # Check if update was successful
    if after and after[3] == (1 if value else 0):
        print(f"\n✅ Update successful")
        return True
    else:
        print(f"\n❌ Update failed!")
        return False

def modify_schema():
    """Modify the schema to remove the DEFAULT 1 constraint"""
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    
    # This requires recreating the table without the DEFAULT constraint
    try:
        # Start transaction
        cursor.execute("BEGIN TRANSACTION")
        
        # Create a new table without the DEFAULT constraint
        cursor.execute("""
        CREATE TABLE settings_new (
            id INTEGER PRIMARY KEY,
            smtp_server VARCHAR(255),
            smtp_port INTEGER,
            smtp_username VARCHAR(255),
            smtp_password VARCHAR(255),
            smtp_use_tls BOOLEAN,
            smtp_from_email VARCHAR(255),
            smtp_from_name VARCHAR(255),
            notification_emails TEXT,
            enable_global_notifications BOOLEAN DEFAULT 0,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_by INTEGER,
            FOREIGN KEY (updated_by) REFERENCES users (id)
        )
        """)
        
        # Copy data from old table to new table
        cursor.execute("""
        INSERT INTO settings_new 
        SELECT id, smtp_server, smtp_port, smtp_username, smtp_password, 
               smtp_use_tls, smtp_from_email, smtp_from_name, notification_emails, 
               enable_global_notifications, updated_at, updated_by
        FROM settings
        """)
        
        # Drop old table
        cursor.execute("DROP TABLE settings")
        
        # Rename new table to the original name
        cursor.execute("ALTER TABLE settings_new RENAME TO settings")
        
        # Commit the transaction
        cursor.execute("COMMIT")
        print("✅ Schema successfully modified to remove DEFAULT constraint")
        
    except Exception as e:
        # Rollback on error
        cursor.execute("ROLLBACK")
        print(f"❌ Error modifying schema: {str(e)}")
        conn.close()
        return False
    
    conn.close()
    return True

if __name__ == "__main__":
    print("== Checking Current Schema ==")
    check_current_schema()
    
    print("== Testing TLS Update (Setting to False) ==")
    if not test_tls_update(False):
        print("\nThe DEFAULT 1 constraint appears to be causing the issue.")
        
        if input("\nDo you want to modify the schema to fix this issue? (y/n): ").lower() == 'y':
            print("\n== Modifying Schema ==")
            if modify_schema():
                print("\n== Testing TLS Update After Schema Modification ==")
                test_tls_update(False)
                
                print("\n== Testing Toggle Back to True ==")
                test_tls_update(True)
    else:
        print("\nThe issue might not be with the schema. Additional investigation needed.") 