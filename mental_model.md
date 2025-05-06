# Mental Model

This document describes the high-level conceptual model and architecture of the system.

This file documents the conceptual understanding of the Strata Violation Log application. It provides high-level insights into the system's purpose, user flows, and core design principles.

## Purpose

The Strata Violation Log is designed to manage, track, and resolve violations within a strata or property management context. It provides interfaces for users to log in, report violations, and manage records.

## Core Concepts
- **User Authentication:** Secure login and session management for users.
- **Violation Logging:** Mechanism for users to report and view violations.
- **Role Management:** Different user roles (e.g., admin, resident) with varying permissions.

## User Flows
- Login via the login page, now implemented as a React SPA component (`frontend/src/views/auth/Login.js`). The login form uses a logo with a base64 fallback for improved reliability and branding.
- Access violation records based on user role.
- Admins can manage users and resolve violations.

## System Identity Design Philosophy

The system prioritizes human-readable identifiers throughout the interface to enhance usability and reduce errors:

1. **User Identification**: 
   - Email addresses serve as primary user identifiers for authentication
   - Full names (first name + last name) are used for display and user interface elements
   - Violation records display creator full names and email addresses for clear attribution
   - This helps administrators and users quickly recognize the source of violations

2. **Record Traceability**:
   - Each violation is clearly associated with its creator's full name and email
   - Responses to violations include name and email identifiers
   - This creates accountability and clear communication channels

3. **Communication Clarity**:
   - All notifications include human-readable identifiers
   - System responses show who created or modified records
   - This ensures users can easily understand the context of each record

## Violation Status Workflow

Violations follow a defined lifecycle managed through the "Status" dynamic field:

1. **Active Statuses**:
   - **Open**: Initial status for new violations requiring attention
   - **Pending Owner Response**: Awaiting response from the property owner
   - **Pending Council Response**: Awaiting response from the strata council

2. **Resolution Path**:
   - Violations move through different statuses as they progress toward resolution
   - The dashboard distinguishes between active and resolved violations
   - Statistics provide visibility into the current system state

3. **Status-based Metrics**:
   - The dashboard counts violations by status category
   - Active violations (Open, Pending Owner Response, Pending Council Response)
   - Resolved violations (any other status value)
   - This provides clear progress tracking for violation management

## Migration from Dynamic to Static Violation Forms

### Overview
The violation creation process has transitioned from a dynamic, backend-driven field model to a static, hardcoded form. This change was made to improve maintainability, user experience, and validation reliability.

### Rationale
- **Simplicity:** Static forms are easier to reason about and maintain.
- **Predictability:** All fields, validation, and options are known at build time.
- **UX:** Users interact with a consistent, well-validated form.

### Legacy Data
- Existing violation records created with dynamic fields remain viewable and accessible.
- The system preserves backward compatibility for legacy data display, but new violations use only the static field set.

## Static Violation Field Expansion (2024)

## Overview
In June 2024, the system migrated from dynamic violation fields to a fully static, hardcoded field structure for all new violations. This change was made to improve maintainability, data integrity, and user experience. All static fields are now first-class columns in the `Violation` model and database.

## New Static Fields Added
The following fields are now directly stored in the `Violation` model:
- owner_property_manager_first_name
- owner_property_manager_last_name
- owner_property_manager_email
- owner_property_manager_telephone
- where_did
- was_security_or_police_called
- fine_levied
- action_taken
- tenant_first_name
- tenant_last_name
- tenant_email
- tenant_phone
- concierge_shift
- noticed_by
- people_called
- actioned_by
- people_involved
- incident_details
- attach_evidence (file metadata/paths)

## Conceptual Impact
- All violation data is now stored in a predictable, queryable schema.
- Legacy violations created with dynamic fields remain accessible, but new violations use only the static field set.
- The system is now easier to maintain, audit, and extend for future requirements.
- API payloads and frontend forms are now tightly coupled to the static schema, improving validation and reliability.

## Dynamic Violation Fields (Extension)

To support evolving requirements, the system allows admin users to define custom fields for violations. These fields are dynamic and can be managed (added, edited, reordered, toggled) via an admin interface. Each violation record can store values for these custom fields, enabling flexible data capture without code changes.

- **Field Definitions:** Admins create and manage field metadata (type, label, required, etc.).
- **Dynamic Form Rendering:** Violation forms are generated based on current field definitions.
- **Backward Compatibility:** Existing violations remain valid; new fields are additive.

- The React SPA is a pure frontend, consuming all data via REST API endpoints provided by Flask.
- Role-based access (admin vs. user) is enforced on the backend for all sensitive endpoints, including /api/violations.
- Dynamic violation fields are defined and managed by admins, and both the form and list views in React are driven by backend data.
- All violation detail access is enforced via backend role checks (admin or owner), and the React SPA consumes this via REST.

- Edit and delete actions for violations are only available to admins or the creator, enforced on both backend (API) and frontend (UI logic).

## User Interface Design Philosophy

### Theme Structure
The application follows the Notus React theme design system, which is built on these core principles:
1. Professional and modern appearance
2. Consistent visual hierarchy
3. Clear user feedback and interactions
4. Responsive design for all devices

### Component Hierarchy
- Layout (Navigation + Content Container)
  - Navigation Bar (Fixed position, contains main navigation)
  - Main Content Area (Responsive padding and width)
  - Forms (Consistent styling and behavior)
  - Cards (For content organization)
  - Buttons (Clear hierarchy and states)

### User Experience Flow
1. Authentication
   - Clean, centered login form
   - Clear error feedback
   - Smooth transitions
   - React SPA implementation with logo and base64 fallback for branding and reliability

2. Navigation
   - Fixed top navigation
   - Clear active states
   - Responsive mobile menu

3. Content Pages
   - Consistent padding and spacing
   - Card-based content organization
   - Clear action buttons
   - Proper form layouts

### Visual Hierarchy
1. Primary Actions
   - Blue theme (lightBlue-500)
   - Prominent positioning
   - Clear hover/active states

2. Secondary Actions
   - Subtle styling
   - Supporting positions
   - Clear but not dominant

3. Destructive Actions
   - Red theme
   - Confirmation required
   - Clear warning states

## Secure Access Model

The system follows a security-first approach for providing access to violation information:

### Basic Security Principles

1. **Least Privilege**: Users only see what they are authorized to view
2. **Defense in Depth**: Multiple layers of protection (authentication, tokens, access logs)
3. **Data Privacy**: Personal information is protected throughout the system
4. **Secure By Default**: All access routes require proper authorization

### Secure URL Architecture

Rather than using predictable, sequential URLs that could be enumerated, the system uses a secure token-based approach:

1. **Internal ID vs Public ID**: Each violation has an internal sequential ID for database operations and a UUID-based public ID for external references

2. **Token-Based Access**:
   - All public URLs use cryptographically signed tokens
   - Tokens contain the violation ID and a timestamp
   - Tokens expire after 24 hours automatically

3. **Access Workflow**:
   ```
   [User] <- Email with secure token URL <- [System]
   [User] -> Request with token -> [System]
   [System] -> Validate token, log access -> [Display Violation]
   ```

4. **Comprehensive Logging**:
   - All access attempts are recorded (IP, user agent, timestamp)
   - Invalid tokens are logged as security warnings
   - Access logs can be reviewed for suspicious activity

This approach ensures that even when sharing violation information with external parties via email, the system maintains high security standards while providing a seamless user experience.

### User Experience with Secure URLs

The secure URL system is designed to be transparent to end users while providing enhanced security:

1. **Intuitive URL Structure**:
   - Violations are referenced with `/violations/public/{uuid}` format
   - Links maintain consistent appearance throughout the application
   - UUIDs are automatically generated and managed by the system

2. **Seamless Navigation**:
   - Users navigate using reference numbers and links, not raw UUIDs
   - Table views present familiar interfaces while using secure URLs underneath
   - PDFs and HTML exports use secure URLs for sharing

3. **Backward Compatibility**:
   - Legacy URLs with sequential IDs continue to function
   - Bookmarks and shared links remain valid
   - System gradually transitions to secure URLs as new content is created

4. **Email Notifications**:
   - All email notifications use secure, time-limited URLs
   - Recipients click naturally presented links without exposure to implementation details
   - System tracks access through these secure links for audit purposes

The mental model for users remains focused on violation reference numbers (e.g., "VIO-20250502-C8A424") as the primary identifier in the UI, while the system uses secure UUIDs for all technical operations and URLs.

## User Experience and First Impressions

- The login page is branded with the Spectrum 4 logo for consistency and professionalism.
- Branding is loaded from `frontend/public/logospectrum.png` and is visible above the sign-in form.

# Recent Enhancements (June 2024)

## CORS and Authentication Updates
- CORS configuration updated to allow correct origins (including 172.16.16.6 and 172.16.16.26) to resolve cross-origin issues.
- All sensitive API endpoints now enforce JWT authentication, replacing session-based `login_required` with `jwt_required_api` for improved security and SPA compatibility.
- User identity in API routes is now accessed via `get_jwt_identity()` instead of `current_user.id` to align with JWT best practices.

## UI/UX Improvements
- User Management: Button color conventions updated for clarity (Add User: blue, Edit: yellow, Delete: red, Change Password: gray).
- Unit Profiles: Building column removed; First Name, Last Name, Rented, Has Dog, Has Cat indicators added; Edit button (yellow) now appears next to View.
- Unit detail page supports `edit=true` query parameter for direct edit mode.
- Tenant information: "Phone" field renamed to "Telephone"; validation now enforces 10-digit numbers with format guidance.
- Unit number field is now enabled when creating new units.

## Architectural Rationale
- These changes improve security, maintainability, and user experience while preserving backward compatibility. The shift to JWT and SPA-friendly endpoints supports modern frontend patterns and robust session management. UI changes enhance clarity and usability for property management workflows.

## User Identity and Position (June 2024)
- User creation now requires First Name, Last Name, and Position (Council, Property Manager, Caretaker, Cleaner, Concierge).
- This ensures all users are uniquely identified and their role in the organization is clear for communication, reporting, and permissions.
- These fields are required for all new users and are displayed in user management interfaces.

---

*Update this file as new conceptual insights are discovered or the application's mental model evolves.* 