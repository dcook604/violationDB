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
- `development` (or unset): Uses `DevelopmentConfig` (Debug mode ON, SQLite default, relaxed CORS/cookies).
- `production`: Uses `ProductionConfig` (Debug mode OFF, expects `DATABASE_URL`, `SECRET_KEY` etc. from environment, restrictive CORS, secure cookies).

Set `FLASK_ENV=development` for local development.

## Known Development Configurations

1. Frontend development servers:
   - Primary: `http://localhost:3001`
   - Secondary: `http://localhost:3002`

2. Backend development server:
   - URL: `http://172.16.16.6:5004`
   - Debug mode: Enabled

## Security Notes

The following security measures are relaxed for development:
- CORS restrictions
- Cookie security requirements
- HTTPS requirements

⚠️ **DO NOT USE THESE SETTINGS IN PRODUCTION** 