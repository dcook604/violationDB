import requests
import json
import sys
from urllib.parse import urlparse

# Base URL
BASE_URL = 'http://172.16.16.6:5004'

# Endpoints
LOGIN_URL = f'{BASE_URL}/api/auth/login-jwt'
TEST_JWT_URL = f'{BASE_URL}/api/test/jwt'
CSRF_TOKEN_URL = f'{BASE_URL}/api/csrf-token'
LOGOUT_URL = f'{BASE_URL}/api/auth/logout-jwt'
REFRESH_URL = f'{BASE_URL}/api/auth/refresh-jwt'
STATUS_URL = f'{BASE_URL}/api/auth/status-jwt'

# Session to maintain cookies
session = requests.Session()

def pretty_print_json(data):
    """Pretty print JSON data
    
    Args:
        data: JSON data to print
    """
    print(json.dumps(data, indent=2))

def get_csrf_token():
    """Get CSRF token
    
    Returns:
        CSRF token
    """
    response = session.get(CSRF_TOKEN_URL)
    if response.status_code == 200:
        token = response.json().get('token')
        print(f"CSRF Token: {token[:10]}... (truncated)")
        session.headers.update({'X-CSRF-TOKEN': token})
        return token
    else:
        print(f"Failed to get CSRF token: {response.status_code}")
        return None

def login(email, password):
    """Login with JWT
    
    Args:
        email: User email
        password: User password
    
    Returns:
        True if login successful, False otherwise
    """
    # Get CSRF token first
    get_csrf_token()
    
    # Login
    data = {
        'email': email,
        'password': password
    }
    response = session.post(LOGIN_URL, json=data)
    
    if response.status_code == 200:
        print("Login successful!")
        print("Cookies received:")
        for cookie in session.cookies:
            print(f"  {cookie.name}: {cookie.value[:10]}... (truncated)")
        pretty_print_json(response.json())
        return True
    else:
        print(f"Login failed: {response.status_code}")
        if response.text:
            try:
                pretty_print_json(response.json())
            except:
                print(response.text)
        return False

def test_jwt_authentication():
    """Test JWT authentication endpoint
    
    Returns:
        True if test successful, False otherwise
    """
    # Get CSRF token first
    get_csrf_token()
    
    # Test JWT authentication
    response = session.get(TEST_JWT_URL)
    
    if response.status_code == 200:
        print("JWT authentication test successful!")
        pretty_print_json(response.json())
        return True
    else:
        print(f"JWT authentication test failed: {response.status_code}")
        if response.text:
            try:
                pretty_print_json(response.json())
            except:
                print(response.text)
        return False

def check_status():
    """Check authentication status
    
    Returns:
        True if authenticated, False otherwise
    """
    # Get CSRF token first
    get_csrf_token()
    
    # Check status
    response = session.get(STATUS_URL)
    
    if response.status_code == 200:
        print("Status check successful!")
        pretty_print_json(response.json())
        return True
    else:
        print(f"Status check failed: {response.status_code}")
        if response.text:
            try:
                pretty_print_json(response.json())
            except:
                print(response.text)
        return False

def refresh_token():
    """Refresh JWT token
    
    Returns:
        True if refresh successful, False otherwise
    """
    # Get CSRF token first
    get_csrf_token()
    
    # Refresh token
    response = session.post(REFRESH_URL)
    
    if response.status_code == 200:
        print("Token refresh successful!")
        pretty_print_json(response.json())
        print("Updated cookies:")
        for cookie in session.cookies:
            print(f"  {cookie.name}: {cookie.value[:10]}... (truncated)")
        return True
    else:
        print(f"Token refresh failed: {response.status_code}")
        if response.text:
            try:
                pretty_print_json(response.json())
            except:
                print(response.text)
        return False

def logout():
    """Logout
    
    Returns:
        True if logout successful, False otherwise
    """
    # Get CSRF token first
    get_csrf_token()
    
    # Logout
    response = session.post(LOGOUT_URL)
    
    if response.status_code == 200:
        print("Logout successful!")
        pretty_print_json(response.json())
        print("Remaining cookies:")
        for cookie in session.cookies:
            print(f"  {cookie.name}: {cookie.value}")
        return True
    else:
        print(f"Logout failed: {response.status_code}")
        if response.text:
            try:
                pretty_print_json(response.json())
            except:
                print(response.text)
        return False

def main():
    """Main function"""
    if len(sys.argv) < 3:
        print("Usage: python test_jwt.py <email> <password>")
        return
    
    email = sys.argv[1]
    password = sys.argv[2]
    
    # Step 1: Login
    print("\n=== Step 1: Login ===")
    if not login(email, password):
        return
    
    # Step 2: Test JWT authentication
    print("\n=== Step 2: Test JWT Authentication ===")
    test_jwt_authentication()
    
    # Step 3: Check status
    print("\n=== Step 3: Check Status ===")
    check_status()
    
    # Step 4: Refresh token
    print("\n=== Step 4: Refresh Token ===")
    refresh_token()
    
    # Step 5: Test JWT authentication again
    print("\n=== Step 5: Test JWT Authentication Again ===")
    test_jwt_authentication()
    
    # Step 6: Logout
    print("\n=== Step 6: Logout ===")
    logout()
    
    # Step 7: Test JWT authentication after logout
    print("\n=== Step 7: Test JWT Authentication After Logout ===")
    test_jwt_authentication()  # This should fail

if __name__ == '__main__':
    main() 