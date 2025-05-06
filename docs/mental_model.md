# User Management System - Mental Model

## Core Concepts

### User Roles and Permissions
- **User**: Basic access level for standard users
- **Manager**: Intermediate access level with additional privileges
- **Admin**: Full system access with user management capabilities

### User States
- **Active/Inactive**: Controls whether a user can log in
- **Temporary Password**: Facilitates secure initial access and password resets
  - Auto-expires after 24 hours
  - One-time use for security

### Password Management
- **Regular Password**: Standard user authentication
- **Temporary Password**: Used for:
  - New user onboarding
  - Password resets
  - Time-limited access

## Violation System Core Concepts

### Dynamic Fields
- **Dynamic Field System**: Replaces static fields with configurable dynamic fields
- **Field Types**: Supports text, number, date, and file upload field types
- **Field Configuration**: Fields can be created, edited, and ordered by administrators
- **Field Validation**: Validation rules can be applied based on field type

### PDF Generation
- **Multi-layer Approach**: Multiple generation methods with fallbacks
- **Reliability First**: System prioritizes reliable PDF delivery over performance
- **Error Recovery**: Automatic fallback to alternative methods on failure

### Violation List Management
- **Pagination**: Efficient handling of large datasets with server-side pagination
- **Date Filtering**: Contextual filtering to focus on relevant time periods
- **User Experience**: Balance between information density and readability

## System Workflows

### User Creation Flow
1. Admin creates user with email and role
2. System generates temporary password
3. User logs in with temporary password
4. User must set permanent password

### Password Reset Flow (User Initiated)
1. User clicks "Forgot Password?" on the login page.
2. User enters their registered email address.
3. System sends a password reset email (if the email exists in the system).
    - Contains a secure, time-limited (24hr) link.
    - User is shown a generic confirmation message regardless of email existence.
4. User clicks the link in the email.
5. User is taken to a page to enter and confirm a new password.
6. User submits the new password.
7. System validates the reset link (token), updates the password, invalidates the link, and terminates all other active sessions for the user.
8. User is redirected to the login page with a success message.

### Role Management
- Role changes automatically update admin status
- Admin role always includes active status
- Role changes preserve existing user data 

### Dynamic Fields Workflow
1. Admin configures fields for violation forms
2. System stores field configurations and types
3. Violation form dynamically renders configured fields
4. User inputs are validated according to field types
5. Data is stored in dynamic_fields structure

### PDF Generation Workflow
1. System generates HTML representation of violation
2. Primary PDF generation method attempts conversion
3. If primary method fails, system tries fallback methods
4. Successful PDF is delivered to user
5. All generation attempts are logged for monitoring 

## Loading State Management

### Component-Based Loading States
- **Spinner Component**: Atomic loading indicator with configurable properties
- **LoadingOverlay Component**: Full-screen overlay that blocks interaction during processing
- **Context-Sensitive Messages**: Dynamic loading messages based on current operation

### Multi-Phase Operations
- **Two-Phase Form Submission**: Form data submission followed by file uploads
- **Global State Tracking**: Window properties track operation progress across components
- **Operation Completion**: Callbacks notify parent components when operations complete

### User Experience Principles
- **Immediate Feedback**: Loading indicators appear instantly when operations start
- **Clear Progress Communication**: Different messages for different operation phases
- **Error Recovery**: Loading states are always reset after errors to prevent UI lockup

### Loading State Workflow
1. User initiates form submission
2. System shows "Creating violation" loading overlay
3. Form data is submitted to backend
4. If file uploads exist:
   - System updates to "Uploading files" message
   - Files are uploaded sequentially
   - Global tracking flags monitor upload progress
5. On completion or error:
   - Loading state is reset
   - Success: User is navigated to new violation
   - Error: Error message is displayed with form preserved 

## Unit Profiles

The Unit Profile feature provides a centralized repository for unit-specific information within the building. Each unit has a single profile that stores:

1. **Basic Information** - Unit number and strata lot number
2. **Owner Information** - Name, contact details, and mailing address
3. **Storage Details** - Parking stall numbers and bike storage numbers
4. **Pet Information** - Whether dogs or cats are present in the unit
5. **Tenant Information** - For rented units, contact details for the current tenants

Unit Profiles connect to the Violation system by providing a consistent reference for unit numbers. This allows the system to maintain proper records even when tenant information changes over time.

The Unit Profile system maintains audit trails for all changes, tracking who made updates and when they occurred. This helps with governance and compliance requirements for the property management team.

# Security Model (Updated)

## CSRF Protection
- As of [date], explicit CSRF tokens and the /api/csrf-token endpoint have been removed.
- CSRF is now mitigated by browser-enforced SameSite cookie policy:
  - All authentication cookies are set with `SameSite=Lax`, `HttpOnly=True`, and `Secure=True` (in production).
  - Browsers will not send cookies on cross-origin POSTs, preventing CSRF by design.
- All state-changing requests are protected by cookie policy, not by explicit tokens.
- **For production, always set `JWT_COOKIE_SECURE = True`. Only set to `False` for local development.**

## Migration Note
- If you ever need to allow cross-origin POSTs, you must reintroduce CSRF tokens for those endpoints. 