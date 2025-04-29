# Memory Bank — Strata Violation Logging App

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

---

*For updates, add new memories or key decisions below this line:*
