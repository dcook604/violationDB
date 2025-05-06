# JWT Authentication in Violation Management System

## Overview

JWT (JSON Web Token) authentication provides a secure, stateless method for authenticating users and validating permissions. This implementation uses HttpOnly cookies to securely store tokens, preventing JavaScript access and mitigating XSS attacks.

## Implementation Details

### Components

1. **JWT Configuration** (`/app/jwt_config.py`)
   - Configures JWT settings (expiration, cookie options)
   - Sets up JWTManager with the Flask app
   - Includes helper functions for JWT identity and claims

2. **JWT Auth Decorators** (`/app/jwt_auth.py`)
   - `jwt_required_api`: Protects routes requiring authentication
   - `admin_required_api`: Protects routes requiring admin access
   - `role_required_api`: Protects routes requiring specific roles

3. **Authentication Routes** (`/app/auth_routes.py`)
   - `/api/auth/login-jwt`: Login endpoint generating JWT tokens
   - `/api/auth/logout-jwt`: Logout endpoint clearing JWT cookies
   - `/api/auth/refresh-jwt`: Endpoint to refresh access tokens
   - `/api/auth/status-jwt`: Endpoint to check authentication status

4. **CSRF Protection** (`/app/csrf_routes.py`)
   - `/api/csrf-token`: Endpoint to get CSRF tokens for protected requests
   - CSRF exemption for critical authentication endpoints

### Token Types

1. **Access Token**
   - Contains user identity and claims (role, admin status)
   - Short expiration (30 minutes)
   - Used for API access authorization

2. **Refresh Token**
   - Longer expiration (7 days)
   - Used to obtain new access tokens without re-authentication

### Token Storage

Tokens are stored in HTTP-only, Secure cookies with SameSite protection:

- `access_token_cookie`: Contains the access token
- `refresh_token_cookie`: Contains the refresh token
- `csrf_access_token`: CSRF token for access token (when using CSRF protection)
- `csrf_refresh_token`: CSRF token for refresh token (when using CSRF protection)

## Security Considerations

1. **Token Payload**
   - Minimal data included in tokens (user ID, role, admin status)
   - No sensitive information stored in tokens

2. **Cookie Security**
   - HttpOnly: Prevents JavaScript access
   - Secure: Restricts to HTTPS (in production)
   - SameSite: Prevents CSRF attacks

3. **CSRF Protection**
   - CSRF tokens required for state-changing operations
   - `/api/csrf-token` endpoint provides tokens for API requests
   - `X-CSRF-TOKEN` header must be included in all POST, PUT, PATCH, and DELETE requests
   - API client automatically fetches and includes CSRF tokens
   - Critical auth endpoints use CSRF exemption for reliability

4. **Token Expiration**
   - Access tokens expire after 30 minutes
   - Refresh tokens expire after 7 days
   - Automatic token refresh mechanism

## Usage Guide

### Frontend Implementation

1. **Authentication Flow**
   ```javascript
   // Login
   const response = await API.post('/api/auth/login-jwt', credentials);
   // Cookies are automatically stored by the browser
   
   // Status check
   const response = await API.get('/api/auth/status-jwt');
   // Use the user data from the response
   
   // Logout
   await API.post('/api/auth/logout-jwt');
   ```

2. **CSRF Protection**
   ```javascript
   // The API client automatically handles CSRF tokens
   // No manual token management is required for most use cases
   
   // If needed, you can manually get a CSRF token
   const csrfResponse = await API.get('/api/csrf-token');
   const token = csrfResponse.data.token;
   
   // Include token in request headers for a custom request
   API.defaults.headers.common['X-CSRF-TOKEN'] = token;
   ```

3. **Token Refresh**
   ```javascript
   // Automatically handle token refresh on 401 responses
   API.interceptors.response.use(
     response => response,
     async error => {
       if (error.response?.status === 401) {
         try {
           await API.post('/api/auth/refresh-jwt');
           // Retry the original request
           return API(error.config);
         } catch (refreshError) {
           // Redirect to login if refresh fails
           window.location.href = '/login';
         }
       }
       return Promise.reject(error);
     }
   );
   ```

### API Client Configuration

The frontend API client (`frontend/src/api.js`) includes automatic handling for both JWT authentication and CSRF protection:

1. **CSRF Token Management**
   - Automatically fetches CSRF tokens on initialization
   - Includes CSRF tokens in all state-changing requests (POST, PUT, PATCH, DELETE)
   - Handles token refresh when tokens expire
   - Retries requests that fail due to CSRF issues
   - Provides graceful fallbacks when CSRF token fetch fails
   - Supports multiple header formats (`X-CSRF-TOKEN`, `X-CSRFToken`, `x-csrf-token`)

2. **JWT Token Management**
   - Automatically refreshes JWT tokens when they expire
   - Queues requests during token refresh to avoid race conditions
   - Redirects to login page when refresh token expires

3. **Error Handling**
   - Comprehensive error detection for CSRF-related issues
   - Automatic retry mechanisms for network errors
   - Graceful degradation when server is unavailable

### Backend Implementation

1. **Protecting Routes**
   ```python
   from app.jwt_auth import jwt_required_api, admin_required_api, role_required_api
   
   @app.route('/api/protected')
   @jwt_required_api
   def protected_route():
       return jsonify({'data': 'protected'})
   
   @app.route('/api/admin')
   @admin_required_api
   def admin_route():
       return jsonify({'data': 'admin only'})
   
   @app.route('/api/manager')
   @role_required_api('manager', 'admin')
   def manager_route():
       return jsonify({'data': 'manager or admin'})
   ```

2. **CSRF Exemption for Critical Routes**
   ```python
   # Define the disable_csrf decorator
   def disable_csrf(view_function):
       """Disable CSRF protection for a specific view function."""
       @wraps(view_function)
       def decorated_function(*args, **kwargs):
           # Store original value
           original_value = current_app.config.get('WTF_CSRF_ENABLED', True)
           # Disable CSRF for this request
           current_app.config['WTF_CSRF_ENABLED'] = False
           try:
               # Call the view function
               response = view_function(*args, **kwargs)
               return response
           finally:
               # Restore original value
               current_app.config['WTF_CSRF_ENABLED'] = original_value
       return decorated_function
   
   @app.route('/api/auth/login-jwt', methods=['POST', 'OPTIONS'])
   @cors_preflight
   @disable_csrf
   def login_jwt():
       # Login implementation
   ```

3. **Accessing User Information**
   ```python
   from flask_jwt_extended import get_jwt_identity, get_jwt, current_user
   
   @app.route('/api/user')
   @jwt_required_api
   def user_route():
       # Get user ID
       user_id = get_jwt_identity()
       
       # Get claims
       claims = get_jwt()
       role = claims.get('role')
       is_admin = claims.get('is_admin')
       
       # Get current user from database (if configured)
       user = current_user
       
       return jsonify({'user_id': user_id, 'role': role})
   ```

## Configuration Options

The following JWT settings can be configured in `jwt_config.py`:

| Setting | Default | Description |
|---------|---------|-------------|
| JWT_SECRET_KEY | Generated | Secret key for signing tokens |
| JWT_ACCESS_TOKEN_EXPIRES | 30 minutes | Access token expiration time |
| JWT_REFRESH_TOKEN_EXPIRES | 7 days | Refresh token expiration time |
| JWT_COOKIE_SECURE | False (Dev), True (Prod) | Restrict cookies to HTTPS |
| JWT_COOKIE_HTTPONLY | True | Prevent JavaScript access to cookies |
| JWT_COOKIE_SAMESITE | Lax | SameSite cookie setting |
| JWT_CSRF_IN_COOKIES | True | Store CSRF tokens in cookies |
| JWT_CSRF_METHODS | POST, PUT, PATCH, DELETE | Methods requiring CSRF protection |

## Troubleshooting

### Common Issues

1. **CSRF Token Issues**
   - Error: "The CSRF token is missing" or "The CSRF session token is missing"
   - Solution: Ensure the API client is properly fetching and including CSRF tokens in requests
   - Check that cookies are being properly set and maintained across requests
   - For auth endpoints, CSRF protection is disabled to prevent authentication issues

2. **JWT Token Issues**
   - Error: "Token has expired" or "Missing cookie 'access_token_cookie'"
   - Solution: Ensure that token refresh is properly implemented
   - Verify that cookies are not being blocked by browser settings

3. **Cross-Origin Issues**
   - Error: "Cross-Origin Request Blocked" or cookies not being set
   - Solution: Ensure CORS is properly configured with `credentials: true` and proper origin settings
   - Verify that SameSite cookie settings are appropriate for your deployment
   - Headers must include all variants of the CSRF token header name (`X-CSRF-TOKEN`, `X-CSRFToken`, `x-csrf-token`)

4. **Network Connection Issues**
   - Error: "Network Error" or "ERR_CONNECTION_REFUSED"
   - Solution: Verify that the Flask server is running and accessible at the configured address
   - The API client will attempt to continue without CSRF tokens for auth endpoints in case of connection issues

## Migration from Session-Based Auth

This implementation exists alongside the current session-based authentication to allow for gradual migration.

Steps to migrate endpoints:
1. Update frontend code to use JWT endpoints
2. Replace `@login_required` with `@jwt_required_api`
3. Replace `@admin_required_api` (session) with `@admin_required_api` (JWT)
4. Update user identification from `current_user` to `get_jwt_identity()` 