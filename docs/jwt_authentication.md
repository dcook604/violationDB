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
   // Get CSRF token
   const csrfResponse = await API.get('/api/csrf-token');
   const token = csrfResponse.data.token;
   
   // Include token in request headers
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

2. **Accessing User Information**
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

## Migration from Session-Based Auth

This implementation exists alongside the current session-based authentication to allow for gradual migration.

Steps to migrate endpoints:
1. Update frontend code to use JWT endpoints
2. Replace `@login_required` with `@jwt_required_api`
3. Replace `@admin_required_api` (session) with `@admin_required_api` (JWT)
4. Update user identification from `current_user` to `get_jwt_identity()` 