# Strata Violation Logging App

A modern, modular web application for logging, managing, and reporting strata violations. Built with Flask, SQLAlchemy, WTForms, Bootstrap, and more. Designed for maintainability, extensibility, and a great user/admin experience.

---

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
- Dashboard with quick access to violation logging and records
- Submit violation reports with file uploads (photos, PDFs)
- PDF generation for each violation (WeasyPrint)
- Email notifications with PDF attachments (Flask-Mail)
- Admin panel for user management (promote/demote admin)
- Searchable/filterable violations table
- Role-based access control (admin vs. regular user)
- Clean, modern UI (Bootstrap, logo, responsive)
- Modular codebase (blueprints, WTForms, config, utils)

---

## Project Structure
```
app/
  __init__.py         # App factory, blueprint registration
  models.py           # SQLAlchemy ORM models
  forms.py            # WTForms classes for all forms
  config.py           # Configuration (env vars, secrets, DB, mail)
  utils.py            # File uploads, PDF, email helpers
  auth_routes.py      # Auth (login, logout, register, reset)
  violation_routes.py # Violation CRUD and viewing
  admin_routes.py     # Admin user management
  templates/          # Jinja2 templates (all inherit from base.html)
  static/             # Logo, CSS, JS
  uploads/            # User-uploaded files (photos, PDFs)
ARCHITECTURE.md       # Architectural/design decisions
README.md             # This file
requirements.txt      # Python dependencies
```

---

## Setup & Installation
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
