# Development Configuration

## CORS Settings

During development, CORS is configured with specific allowed origins to facilitate frontend-backend communication. This includes:

- Specific allowed origins (localhost, development servers, etc.)
- All common HTTP methods enabled (GET, POST, PUT, DELETE, OPTIONS)
- Credentials supported
- All necessary headers allowed

```python
CORS(app, 
     resources={r"/*": {
         "origins": ["http://localhost:3001", "http://localhost:3002", "http://172.16.16.6:3001", "http://172.16.16.6:5004", "http://100.75.244.2", "http://100.75.244.2:3001", "http://100.75.244.2:5004"],
         "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         "allow_headers": ["Content-Type", "Authorization", "X-Requested-With", "Accept"],
         "supports_credentials": True,
         "expose_headers": ["Content-Type", "Authorization"]
     }},
     supports_credentials=True)
```

⚠️ **Important**: These settings are for development only. In production:
- Restrict origins to specific domains
- Limit exposed headers
- Configure appropriate security measures

## Database Configuration

The application uses MariaDB as the database both in development and production:

```python
# Development database connection
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://violation:n2hm13i@localhost:3309/violationdb'

# Development connection pooling settings
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 10,
    'max_overflow': 20,
    'pool_timeout': 30,
    'pool_recycle': 1800,
    'pool_pre_ping': True,
}
```

Database connection errors are handled gracefully with custom error pages and detailed logging.

## Session Configuration

For development convenience, session cookies are configured with:
- `SameSite=Lax` to allow cross-site requests
- `Secure=False` to work without HTTPS
- `HttpOnly=True` for security

## Development Server

The backend runs on `http://172.16.16.6:5004` and accepts requests from:
- `http://localhost:3001`
- `http://localhost:3002`
- `http://172.16.16.6:3001`
- `http://172.16.16.6:5004`
- `http://100.75.244.2`
- `http://100.75.244.2:3001`
- `http://100.75.244.2:5004`

## API Endpoints

All API endpoints (`/api/*`) are CORS-enabled with the above settings.

## Environment Configuration

The application uses different configurations based on the `FLASK_ENV` environment variable:
- `development` (or unset): Uses `DevelopmentConfig` (Debug mode ON, MariaDB with generous connection pool, relaxed CORS/cookies).
- `production`: Uses `ProductionConfig` (Debug mode OFF, MariaDB with conservative connection pool, restrictive CORS, secure cookies).

Set `FLASK_ENV=development` for local development.

## Known Development Configurations

1. Frontend development servers:
   - Primary: `http://localhost:3001`
   - Secondary: `http://localhost:3002`

2. Backend development server:
   - URL: `http://172.16.16.6:5004`
   - Debug mode: Enabled
   - Database: MariaDB on port 3309

## Security Notes

The following security measures are relaxed for development:
- CORS restrictions
- Cookie security requirements
- HTTPS requirements

⚠️ **DO NOT USE THESE SETTINGS IN PRODUCTION**

## Branding and Login Logo

- The login page displays the Spectrum 4 logo (`logospectrum.png`) above the sign-in form.
- The logo is loaded from `frontend/public/logospectrum.png`.
- **To update the login logo:** Replace `frontend/public/logospectrum.png` with your desired image and rebuild the frontend. 

## Development Server Management

### Reset Servers Script

The application includes a `reset_servers.sh` script that simplifies the process of restarting both the frontend and backend servers during development. This script:

1. Stops any running instances of the backend and frontend servers
2. Clears any orphaned processes
3. Verifies ports are available
4. Installs/updates Python dependencies from requirements.txt
5. Starts the backend Flask server
6. Starts the frontend React development server
7. Outputs log locations and access URLs

To use the script:
```bash
# Make it executable (first time only)
chmod +x reset_servers.sh

# Run the script
./reset_servers.sh
```

The script creates log files for both servers:
- Backend: `flask.log` in the project root
- Frontend: `frontend/react.log`

### Dependency Management

Python dependencies are managed through the `requirements.txt` file and installed automatically by the reset script. Key dependencies include:

- **Flask-Limiter**: Requires the `limits` package to be installed
- **Flask-Migrate**: Used for database migrations
- **PyMySQL**: Required for MySQL/MariaDB connections

When adding new dependencies:
1. Add them to `requirements.txt` with specific versions
2. Run `pip install -r requirements.txt` to update your environment
3. Test thoroughly before committing changes

#### Common Dependency Issues

- **Flask-Limiter**: If you encounter "No module named 'flask_limiter'" errors, ensure both `Flask-Limiter` and `limits` are installed
- **Database Connections**: For MySQL/MariaDB connections, ensure `pymysql` or `mysqlclient` is installed
- **PDF Generation**: WeasyPrint requires several system dependencies; see WeasyPrint documentation for details 