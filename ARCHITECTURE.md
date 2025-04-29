# Strata Violation Logging App — Architectural, Design & Product Decisions

## Product Design

### Product Goals
- Provide a secure, modern platform for logging, tracking, and managing strata violations.
- Support both regular users (residents, staff) and administrators (property managers, council).
- Ensure data privacy, auditability, and a clear workflow for violation resolution.

### User Roles
- **Regular User:** Can log in, submit new violations, view their own violations, and receive notifications.
- **Admin User:** Can view all violations, manage users (promote/demote admin), and edit/delete any violation.

### Key User Stories
- As a resident, I want to submit a violation report with supporting files so that issues can be addressed promptly.
- As an admin, I want to manage user roles and review all violation reports to ensure proper follow-up.
- As any user, I want a clear, modern dashboard with easy access to my relevant actions.
- As an admin, I want to generate and send PDF reports for official records.

### Product Rationale
- **Role-based access** ensures sensitive data is only visible to authorized users.
- **Modular blueprints** enable future extensibility (e.g., adding analytics, notifications).
- **Modern UI/UX** (Bootstrap, flash messages, responsive design) increases adoption and reduces training needs.
- **Test exclusion from VCS**: Tests are not included in production deployments for security and size reasons, but are required for local/dev quality assurance.

---

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
