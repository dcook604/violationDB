import sqlite3
import requests
import json
import sys

# Change this to your app URL if different
BASE_URL = 'http://localhost:5004'

def get_current_setting():
    """Get current TLS setting from database"""
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, smtp_server, smtp_port, smtp_use_tls FROM settings")
    row = cursor.fetchone()
    conn.close()
    
    if row:
        print(f"Current database settings:")
        print(f"  ID: {row[0]}")
        print(f"  SMTP Server: {row[1]}")
        print(f"  SMTP Port: {row[2]}")
        print(f"  SMTP Use TLS: {row[3]}")
        print("")
        return row[3]
    else:
        print("No settings found in database")
        return None

def update_tls_setting(value):
    """Update TLS setting in database directly"""
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE settings SET smtp_use_tls = ? WHERE id = 1", (1 if value else 0,))
    conn.commit()
    changed = cursor.rowcount > 0
    conn.close()
    
    print(f"Direct database update to {'enable' if value else 'disable'} TLS: {'successful' if changed else 'failed'}")
    print("")
    return changed

def test_api_update(session, enable_tls):
    """Test updating TLS via API"""
    # First get current settings
    try:
        response = session.get(f"{BASE_URL}/api/admin/settings")
        response.raise_for_status()
        settings = response.json()
        
        # Update TLS setting
        settings['smtp_use_tls'] = enable_tls
        
        # Send update
        update_response = session.put(
            f"{BASE_URL}/api/admin/settings",
            json=settings
        )
        update_response.raise_for_status()
        
        print(f"API update to {'enable' if enable_tls else 'disable'} TLS: successful")
        print(f"Response: {update_response.json()}")
        print("")
        return True
    except Exception as e:
        print(f"API update failed: {str(e)}")
        return False

def login(session, email, password):
    """Login to get a session cookie"""
    try:
        response = session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": email, "password": password}
        )
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"Login failed: {str(e)}")
        return False

def main():
    # Get current setting
    current = get_current_setting()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--direct':
        # Perform direct database toggle
        new_value = not current
        update_tls_setting(new_value)
        # Verify change
        updated = get_current_setting()
        if updated == new_value:
            print("✅ Direct database update successful and verified")
        else:
            print("❌ Direct database update failed verification")
    else:
        # Ask for credentials
        email = input("Admin email: ")
        password = input("Password: ")
        
        # Create session
        session = requests.Session()
        
        # Login
        if login(session, email, password):
            print("Login successful")
            
            # Toggle current setting
            new_value = not current
            if test_api_update(session, new_value):
                # Verify change in database
                updated = get_current_setting()
                if updated == new_value:
                    print("✅ API update successful and verified in database")
                else:
                    print("❌ API update succeeded but database shows different value")
                    print(f"  Expected: {new_value}, Actual: {updated}")
        else:
            print("Cannot proceed without login")

if __name__ == "__main__":
    main() 