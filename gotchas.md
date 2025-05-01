# Gotchas & Edge Cases

This file documents known issues, edge cases, and warnings for the Strata Violation Log application.

## Known Issues
- None documented yet.

## Edge Cases
- Login form: If the user submits an invalid email or password, the first error is displayed using flash messages or inline feedback.
- CSRF: All forms must include CSRF tokens to prevent cross-site request forgery.
- Dynamic fields: If a field definition is changed (e.g., type or required status), existing violation records may have incompatible or missing values. UI and API should handle such cases gracefully.
- Deleting field definitions: Deleting a field definition should either cascade to field values or mark the field as inactive to preserve data integrity.
- Field order: Reordering fields must be reflected consistently in both admin and user forms.
- Validation: Ensure both backend and frontend enforce field validation rules to prevent inconsistent data.

## Warnings
- Ensure that all static assets are correctly referenced using `url_for('static', ...)` to avoid broken links.

## Additional Notes
- If running React and Flask on different ports during development, ensure CORS is enabled on Flask (`flask-cors` or manual headers).
- For session/cookie authentication, set `withCredentials: true` in Axios and ensure Flask sends cookies with CORS responses.
- If field definitions are changed while a user is filling a form, validation errors may occur; handle gracefully in the UI.
- Drag-and-drop reordering requires unique field IDs and correct API ordering.
- The /api/violations endpoint is required for the React SPA ViolationList page. If not present, the list will not load.
- If user roles are not set up correctly, regular users may see no violations or too many. Ensure current_user.is_admin is reliable.
- Dynamic fields are returned as a nested object; if field definitions change, frontend may need to handle missing/extra columns.
- The /api/violations/:id endpoint is role-protected. Only admins or the creator can edit or delete a violation.
- When editing, ensure dynamic field names match backend definitions; missing fields may be lost if not included in the update.

## Database Schema Inconsistencies

### Issue: Model-Database Column Mismatch
The SQLAlchemy models define columns that don't exist in the actual database schema. This causes 500 errors when the application tries to query these non-existent columns.

Specific issues:
- The `Violation` model includes fields like `resolved_at` and `resolved_by` that don't exist in the database
- This affects routes that query these columns, particularly the dashboard statistics and violation listing endpoints

### Solution Approaches

1. **ORM-Safe Attribute Access**
   - Use `getattr(model, 'attribute', default_value)` instead of direct attribute access
   - Add `hasattr()` checks before accessing attributes that might not exist
   - Wrap operations in try-except blocks to gracefully handle missing column errors

2. **Raw SQL Queries**
   - For critical routes, use raw SQL queries with `db.session.execute(text(sql))` that only reference columns known to exist
   - This bypasses ORM mapping issues when there's a mismatch between models and schema

3. **Graceful Error Handling**
   - Return sensible defaults instead of 500 errors when database inconsistencies occur
   - Log detailed error information for debugging while providing a functional UI

### Lessons Learned
- Always ensure database migrations are in sync with model changes
- Test on a development database before deploying model changes
- Include robust error handling for database operations, especially in API endpoints
- Consider versioning APIs to handle schema evolution more gracefully

### Long-term Solutions
- Run database migrations to add missing columns
- Use Alembic to properly track schema changes
- Implement proper database versioning
- Consider soft schema validation on application startup

---

*Update this file immediately when new issues, bugs, or edge cases are discovered.* 