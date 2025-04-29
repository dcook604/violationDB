# User Management System - Gotchas and Edge Cases

## Password Management

### Temporary Password Issues
1. **Expiration Timing**
   - Temporary passwords expire after 24 hours
   - Server timezone affects expiration calculation
   - Use UTC consistently for all datetime operations

2. **Password Reset Conflicts**
   - Multiple temporary passwords may cause confusion
   - Always clear existing temporary password before setting new one
   - Ensure proper error handling during password updates

3. **Session Management**
   - User sessions should be invalidated after password changes
   - Temporary password login should force immediate password change
   - Handle concurrent login attempts appropriately

## Role Management

### Role Change Effects
1. **Admin Role**
   - Setting role to 'admin' automatically sets `is_admin=True`
   - Changing from 'admin' role doesn't automatically remove admin status
   - Use `set_role()` method to ensure proper role transitions

2. **Active Status**
   - Admin users are always active
   - Deactivating an admin requires role change first
   - Role changes don't affect active status unless becoming admin

## Database Operations

### Common Issues
1. **Unique Email Constraint**
   - Email uniqueness is enforced at database level
   - Handle IntegrityError for duplicate email addresses
   - Provide clear user feedback for email conflicts

2. **Session Management**
   - Always use try/except blocks with session operations
   - Implement proper session rollback on errors
   - Commit changes only after all operations succeed

## Security Considerations

### Password Security
1. **Password Hashing**
   - Never store plain-text passwords
   - Use werkzeug's password hashing functions
   - Handle hash generation errors gracefully

2. **Temporary Password Display**
   - Only show temporary password once during creation
   - Log temporary password generation attempts
   - Consider implementing secure password delivery mechanism

### Access Control
1. **Route Protection**
   - Always apply @login_required decorator
   - Check user permissions in route handlers
   - Handle unauthorized access attempts gracefully

2. **Form Validation**
   - Validate all form inputs server-side
   - Handle malformed data gracefully
   - Prevent role escalation attacks 