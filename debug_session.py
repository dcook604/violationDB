#!/usr/bin/env python
import requests
import json
import sys

def test_login_flow():
    """
    Test the full login flow with detailed debugging
    """
    # Settings
    base_url = "http://localhost:5004"  # Flask backend
    login_endpoint = f"{base_url}/api/auth/login"
    session_endpoint = f"{base_url}/api/auth/session"
    test_endpoint = f"{base_url}/api/auth/debug"
    
    # Credentials - replace with valid user
    credentials = {
        "email": "admin@example.com",
        "password": "admin123"  # Updated password
    }
    
    # Create a session that preserves cookies
    s = requests.Session()
    
    # Set default headers to simulate browser
    s.headers.update({
        "Origin": "http://172.16.16.6:3001",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"
    })
    
    # 1. Check current session state before login
    print("\n[1] Checking initial session state...")
    try:
        r = s.get(test_endpoint)
        print(f"Status: {r.status_code}")
        print(f"Cookies: {s.cookies.get_dict()}")
        print(f"Response (truncated): {r.text[:200]}...")
    except Exception as e:
        print(f"Error: {str(e)}")
    
    # 2. Attempt login
    print("\n[2] Attempting login...")
    try:
        r = s.post(login_endpoint, json=credentials)
        print(f"Status: {r.status_code}")
        print(f"Response Headers: {dict(r.headers)}")
        print(f"Set-Cookie Header: {r.headers.get('Set-Cookie', 'None')}")
        print(f"Cookies after login: {s.cookies.get_dict()}")
        print(f"Response (truncated): {r.text[:200]}...")
    except Exception as e:
        print(f"Error: {str(e)}")
    
    # 3. Check session state after login
    print("\n[3] Checking session state after login...")
    try:
        r = s.get(session_endpoint)
        print(f"Status: {r.status_code}")
        print(f"Response Headers: {dict(r.headers)}")
        print(f"Cookies: {s.cookies.get_dict()}")
        print(f"Response (truncated): {r.text[:200]}...")
    except Exception as e:
        print(f"Error: {str(e)}")
        
    # 4. Check debug endpoint after login
    print("\n[4] Checking debug endpoint after login...")
    try:
        r = s.get(test_endpoint)
        print(f"Status: {r.status_code}")
        print(f"Response Headers: {dict(r.headers)}")
        print(f"Cookies: {s.cookies.get_dict()}")
        print(f"Response (truncated): {r.text[:200]}...")
    except Exception as e:
        print(f"Error: {str(e)}")
    
    # 5. Try direct access with explicit cookies
    print("\n[5] Testing direct access with manual cookies...")
    cookies = s.cookies.get_dict()
    if 'session_token' in cookies:
        try:
            headers = {
                'Cookie': f"session_token={cookies['session_token']}; test_auth={cookies.get('test_auth', '')}"
            }
            r = requests.get(session_endpoint, headers=headers)
            print(f"Status: {r.status_code}")
            print(f"Response Headers: {dict(r.headers)}")
            print(f"Response (truncated): {r.text[:200]}...")
        except Exception as e:
            print(f"Error: {str(e)}")
    else:
        print("No session_token cookie found to use")
    
    # Summary
    print("\n[Summary]")
    print(f"Final cookie jar: {s.cookies.get_dict()}")
    
    if 'session_token' in s.cookies.get_dict():
        print("✅ session_token cookie is present")
    else:
        print("❌ session_token cookie is missing!")
        
    if 'test_auth' in s.cookies.get_dict():
        print("✅ test_auth cookie is present")
    else:
        print("❌ test_auth cookie is missing!")

if __name__ == "__main__":
    test_login_flow() 