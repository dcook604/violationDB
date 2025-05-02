Œ!# Memory Bank ‚Äî Strata Violation Logging App

This file serves as a persistent, human-readable memory bank for the project. It summarizes project context, architecture, major decisions, and conventions for onboarding and future reference.

---

## Project Overview
- **Name:** Strata Violation Logging App
- **Stack:** Flask, SQLAlchemy, WTForms, Flask-Login, Flask-Mail, WeasyPrint, Bootstrap
- **Purpose:** Log, manage, and report strata violations with robust user/admin controls and modern UI

## Architecture & Decisions
- **Blueprints:** Modular separation for authentication (`auth_routes.py`), violations (`violation_routes.py`), and admin (`admin_routes.py`)
- **Forms:** WTForms for all user input
- **Templates:** All inherit from `base.html` for DRY, consistent UI
- **Config:** Centralized in `config.py`, loaded from environment variables
- **Utilities:** File upload, PDF, email logic in `utils.py`
- **Role-based Access:** `User.is_admin` controls admin privileges
- **Documentation:** Major decisions in `ARCHITECTURE.md`, usage/setup in `README.md`
- **Login Redirect:** Setting `login_manager.login_view = 'auth.login'` fixed the 401/302 redirect test issue, ensuring unauthenticated users are redirected to the login page
- **Test Isolation:** Updated pytest fixture to reset the database between tests using an in-memory SQLite DB. Each test now starts with a clean database state.

## Conventions & Guidelines
- Use blueprints for all new feature modules
- WTForms for all forms and validation
- Update `ARCHITECTURE.md` and this file with major changes
- Write docstrings and comments for all new code

## Persistent Context
- This project is refactored for maintainability, extensibility, and robust access control
- All new developers should review this file, `ARCHITECTURE.md`, and `README.md` before making changes
- Note: Registration test still fails, likely due to duplicate email or test DB state not being reset between tests
- 2025-04-29: Changed Flask development server to run on port 5003 for local testing (previously 5001, originally 5000).
- 2025-04-29: Fixed login, register, and reset password templates by moving form content from block 'container' to block 'content', ensuring forms render as intended.

---

*For updates, add new memories or key decisions below this line:*

---

## [2025-04-29] Application Structure & Implementation Review

### Blueprints
- **auth_routes.py**: Handles authentication (login, logout, registration, password reset).
- **violation_routes.py**: Handles violation CRUD, custom fields, and related admin actions.
- **admin_routes.py**: Handles user management (promote/demote admin).
- **routes.py**: Main dashboard, registration, and password reset (some overlap with auth_routes).

### Models
- **User**: `id`, `email`, `password_hash`, `is_admin` (role-based access).
- **Violation**: Rich schema for violations, including `reference`, `category`, `details`, `extra_fields` (JSON), and metadata for incident and reporting.

### Forms
- **LoginForm, RegisterForm, ResetPasswordForm**: WTForms for authentication.
- **ViolationForm**: WTForms for violation entry, supports dynamic/custom fields.

### Utilities
- **utils.py**: File upload, PDF generation (WeasyPrint), and email (Flask-Mail) helpers.

### Templates
- All templates inherit from `base.html` for consistent UI.
- Custom fields for violations are managed via JSON file and rendered dynamically in forms.

### Other Notes
- Uses Flask-Login for authentication and role-based access control.
- Uses SQLAlchemy ORM for persistence.
- **Production database is MariaDB (see `SQLALCHEMY_DATABASE_URI` in `config.py`). Project was migrated from SQLite to MariaDB for better scalability and production reliability.**
- Admin users can manage custom violation fields and promote/demote users.
- Project is modular and follows best practices for maintainability and extensibility.

### Persistent Context (Update)
- The actual implementation matches the architectural intent described above.
- No evidence of a separate "memory bank" feature for user notes or logs; all persistent data is related to users and violations.
- Custom violation fields are managed via a JSON file and admin interface.
- Test isolation is handled via in-memory SQLite in pytest fixtures.

---
≠ ≠˝

˝
¥ ¥®®»
»ê 
êÙ Ù®
®Œ! 2%file:///home/violation/MEMORY_BANK.md