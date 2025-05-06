# Strata Violation Logging App

A modern, modular web application for logging, managing, and reporting strata violations. Built with Flask, SQLAlchemy, WTForms, Bootstrap, and more. Designed for maintainability, extensibility, and a great user/admin experience.

---

## Branding Update

- The application is now branded as **Spectrum 4 Violation Tracking**.
- The login page displays the Spectrum 4 logo (`logospectrum.png`) above the sign-in form for a professional, branded experience.

---

## Changelog

2025-04-29: Fixed login, register, and reset password templates to display forms correctly by moving content from block 'container' to block 'content' as per base.html structure.
2025-04-29: Added missing 'remember' BooleanField to LoginForm so login page renders correctly.

## Table of Contents
- [Features](#features)
- [Project Structure](#project-structure)
- [Setup & Installation](#setup--installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [User Roles](#user-roles)
- [Development Guidelines](#development-guidelines)
- [Architecture Decisions](#architecture-decisions)
- [Contact](#contact)

---

## Features
- User authentication (login, registration, password reset)
- **Branded login page with Spectrum 4 logo**
- Dashboard with quick access to violation logging and records
- Submit violation reports with file uploads (photos, PDFs)
- PDF generation for each violation (WeasyPrint)
- Email notifications with PDF attachments (Flask-Mail)
- Admin panel for user management (promote/demote admin)
- Modular blueprints: admin features in admin_routes.py, authentication in auth_routes.py, violations in violation_routes.py
- Searchable/filterable violations table
- Role-based access control (admin vs. regular user)
- Clean, modern UI (Bootstrap, logo, responsive)
- Modular codebase (blueprints, WTForms, config, utils)
- Tests are excluded from version control by .gitignore for production deployments

---

## Project Structure
```
app/
  __init__.py         # App factory, blueprint registration
  models.py           # SQLAlchemy ORM models
  forms.py            # WTForms classes for all forms
  config.py           # Configuration (env vars, secrets, DB, mail)
  utils.py            # File uploads, PDF, email helpers
  admin_routes.py     # Admin panel routes (user management)
  auth_routes.py      # Authentication routes (login, registration, reset)
  violation_routes.py # Violation reporting and management
  templates/          # Jinja2 templates (all inherit from base.html)
  static/             # Logo, CSS, JS
  uploads/            # User-uploaded files (photos, PDFs)
ARCHITECTURE.md       # Architectural/design decisions
README.md             # This file
requirements.txt      # Python dependencies
```

---

## Setup & Installation

### Requirements
- All dependencies are listed in requirements.txt, including Flask-WTF and pytest for forms and testing.
1. **Clone the repo:**
   ```bash
   git clone <repo-url>
   cd violation
   ```
2. **Create a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Set environment variables:**
   - Copy `.env.example` to `.env` and fill in secrets (see [Configuration](#configuration))
5. **Initialize the database:**
   ```bash
   flask shell
   >>> from app import db, create_app
   >>> app = create_app()
   >>> app.app_context().push()
   >>> db.create_all()
   >>> exit()
   ```
6. **Run the app:**
   ```bash
   flask run
   ```

---

## Configuration
All sensitive settings are managed via environment variables (see `.env.example`).
- `SECRET_KEY`, `DATABASE_URL`, `MAIL_SERVER`, `MAIL_PORT`, `MAIL_USERNAME`, `MAIL_PASSWORD`, `MAIL_DEFAULT_SENDER`, `UPLOAD_FOLDER`
- See `app/config.py` for all options.

---

## Usage
- **Login/Register:** `/login`, `/register`
- **Dashboard:** `/` (after login)
- **Log Violation:** `/violations/new`
- **View Violations:** `/violations`
- **Admin User Management:** `/admin/users` (admin only)
- **Reset Password:** `/reset_password`
- **Logout:** `/logout`

---

## User Roles
- **Admin:** Can view/manage all users, promote/demote admins, edit/delete any violation
- **Regular User:** Can submit violations and edit/delete their own

---

## Development Guidelines
- Follow blueprint/module structure for new features
- Use WTForms for all forms
- Add new config to `config.py`, not directly in code
- Update `ARCHITECTURE.md` with major decisions
- Write docstrings for all new functions/classes

---

## Architecture Decisions
See [ARCHITECTURE.md](./ARCHITECTURE.md) for all major design and architectural choices, including rationale for:
- Blueprint separation
- Template inheritance
- WTForms
- Config/utility structure
- Role-based access
- UI/UX conventions

---

## Contact
For questions, suggestions, or onboarding help, see project maintainers or open an issue.

## Running the Application

### Development Setup (Recommended)

The easiest way to run the application is using the provided server management script:

```bash
# Make the script executable
chmod +x reset_servers.sh

# Run the script to start both backend and frontend
./reset_servers.sh
```

This script will:
1. Kill any existing processes on ports 5004 (backend) and 3001 (frontend)
2. Start the Flask backend on port 5004
3. Start the React frontend on port 3001
4. Verify that both servers are running
5. Create log files for both servers

You can then access:
- Frontend: http://localhost:3001
- Backend API: http://localhost:5004

### Manual Setup

If you prefer to start the servers manually:

**Backend (Flask)**
```bash
source .venv/bin/activate
python run.py  # Runs on port 5004
```

**Frontend (React)**
```bash
cd frontend
npm start  # Runs on port 3001
```

### Troubleshooting

If you encounter issues with the servers:
- Check `flask.log` for backend errors
- Check `frontend/react.log` for frontend errors
- Run `lsof -i -P -n | grep LISTEN` to see what's running on which ports
- Use the reset script to stop and restart everything

## Production Deployment

This application is designed to be deployed using a production-grade WSGI server (like Gunicorn) behind a reverse proxy (like Nginx).

**Key Components:**

*   **Configuration:** Production settings are managed via the `ProductionConfig` class in `app/config.py`, primarily loaded using environment variables (set in `.env` on the server or via systemd). Set `FLASK_ENV=production`.
*   **WSGI Server:** Use Gunicorn to run the application. A configuration file `gunicorn.conf.py` is provided.
*   **Reverse Proxy:** Use Nginx as a reverse proxy. A sample configuration template `nginx_violation.spectrum4.ca.conf` is provided. Adapt it for your domain and SSL setup (Cloudpanel/Let's Encrypt).
*   **Process Management:** Use systemd to manage the Gunicorn process. A service file template `violation.service` is provided.

**General Steps (Ubuntu 22.04 Example):**

1.  **Clone Repository:** Clone the code onto your production server.
2.  **Install Dependencies:** Set up Python venv, install OS packages (`python3-venv`, `nginx`, `libmysqlclient-dev`, etc.), and install Python requirements (`pip install -r requirements.txt`).
3.  **Configure Environment:** Create a `.env` file in the project root with production secrets (`SECRET_KEY`, `DATABASE_URL`, `MAIL_*`). **Do not commit this file.**
4.  **Database Setup:** Ensure your production database (e.g., MySQL) is running and accessible. Create the necessary database and user.
5.  **Run Migrations:** Apply database migrations: `export FLASK_APP=run.py && export FLASK_ENV=production && flask db upgrade`.
6.  **Configure Gunicorn:** Ensure `gunicorn.conf.py` points to the correct application object (e.g., `run:app`).
7.  **Configure systemd:**
    *   Copy `violation.service` to `/etc/systemd/system/`.
    *   Modify the `User`, `Group`, `WorkingDirectory`, `EnvironmentFile`, and `ExecStart` paths in the service file to match your server setup.
    *   Reload systemd: `sudo systemctl daemon-reload`
    *   Enable the service: `sudo systemctl enable violation.service`
    *   Start the service: `sudo systemctl start violation.service`
    *   Check status: `sudo systemctl status violation.service` and logs `sudo journalctl -u violation.service`.
8.  **Configure Nginx:**
    *   Copy `nginx_violation.spectrum4.ca.conf` to `/etc/nginx/sites-available/`. Rename if needed.
    *   Adapt the `server_name`, SSL paths (if not handled by Cloudpanel), and `alias` paths for static/uploads.
    *   Ensure the socket path in `proxy_pass` matches the `bind` directive in `gunicorn.conf.py` and the `RuntimeDirectory` in the systemd file.
    *   Create a symlink: `sudo ln -s /etc/nginx/sites-available/your-config-file /etc/nginx/sites-enabled/`
    *   Test Nginx config: `sudo nginx -t`
    *   Reload Nginx: `sudo systemctl reload nginx`
9.  **DNS & Firewall:** Ensure your DNS points to the server IP and firewall rules allow traffic on ports 80 and 443.

Refer to the specific configuration files (`gunicorn.conf.py`, `nginx_violation.spectrum4.ca.conf`, `violation.service`, `app/config.py`) for detailed settings.

## Database

This project uses MariaDB as the database. The configuration is in `app/config.py` with proper connection pooling 
and error handling. Database connections are managed by SQLAlchemy with the following features:

- Connection pooling to efficiently manage database connections
- Connection recycling to prevent stale connections
- Connection validation with pre-ping
- Comprehensive error handling for database operations
- Graceful error recovery for common database issues

### Database Connection Parameters

The application uses the following MariaDB connection parameters:

```python
# Development
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 10,          # Default number of database connections in the pool
    'max_overflow': 20,       # Maximum number of connections to create above pool_size
    'pool_timeout': 30,       # Seconds to wait before giving up on getting a connection
    'pool_recycle': 1800,     # Recycle connections after 30 minutes to avoid stale connections
    'pool_pre_ping': True,    # Issue a test query on the connection to check if it's still valid
}

# Production (more conservative)
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 5,           # Start with fewer connections for better server resource management
    'max_overflow': 10,       # Allow fewer overflow connections
    'pool_timeout': 60,       # Wait longer in production before giving up
    'pool_recycle': 1800,     # Recycle connections after 30 minutes
    'pool_pre_ping': True,    # Always verify connection is valid before using it
}
```
