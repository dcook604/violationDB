# Strata Violation Logging App — Architectural & Design Decisions

## 1. Blueprint Separation
- App is split into multiple Flask blueprints:
  - `auth_routes.py` for authentication and user actions (login, logout, register, reset password)
  - `violation_routes.py` for all violation CRUD and viewing
  - `admin_routes.py` for admin-only user management features
- **Rationale:** Modular, maintainable, and scalable codebase

## 2. Template Inheritance
- All templates inherit from `base.html`, which provides:
  - Shared navbar (with user/admin logic)
  - Logo, Bootstrap, and flash message display
- **Rationale:** DRY, consistent UI, easy updates

## 3. WTForms Integration
- All forms (login, registration, reset password, violation submission/edit) use WTForms, defined in `forms.py`
- **Rationale:** Centralized validation, consistent field rendering, easier testing

## 4. Configuration Management
- All configuration is in `config.py`, loaded from environment variables
- **Rationale:** Secure, portable, easy environment switching

## 5. Utilities Module
- `utils.py` contains file upload, PDF generation, and email logic
- **Rationale:** Keeps route logic clean, promotes reuse

## 6. Database Model Enhancements
- `User` model has `is_admin` boolean for role-based access
- SQLAlchemy ORM used for all models
- **Rationale:** Enables permissions, ORM safety and flexibility

## 7. Navigation and UI/UX
- Centralized navigation in base template’s navbar
- Bootstrap for all forms and tables
- Consistent flash messages
- **Rationale:** Modern, accessible, intuitive UI

## 8. File/Static Organization
- Static files in `/static`, user uploads in `/uploads`
- **Rationale:** Security and clarity

## 9. Removal of Monolithic Route File
- All routes moved to blueprints; `routes.py` deprecated
- **Rationale:** Reduces complexity, clear module responsibilities

## 10. Testing and Maintainability
- Refactored code is structured for easy unit/integration testing
- **Rationale:** Ensures long-term maintainability and easier onboarding

---

*For further details, see code comments and per-module docstrings. For questions or future decisions, update this file or create `docs/` as needed.*
