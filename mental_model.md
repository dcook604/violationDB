# Mental Model

This file documents the conceptual understanding of the Strata Violation Log application. It provides high-level insights into the system's purpose, user flows, and core design principles.

## Purpose

The Strata Violation Log is designed to manage, track, and resolve violations within a strata or property management context. It provides interfaces for users to log in, report violations, and manage records.

## Core Concepts
- **User Authentication:** Secure login and session management for users.
- **Violation Logging:** Mechanism for users to report and view violations.
- **Role Management:** Different user roles (e.g., admin, resident) with varying permissions.

## User Flows
- Login via the login page (`login.html`).
- Access violation records based on user role.
- Admins can manage users and resolve violations.

## System Identity Design Philosophy

The system prioritizes human-readable identifiers throughout the interface to enhance usability and reduce errors:

1. **User Identification**: 
   - Email addresses serve as primary user identifiers across the system
   - Violation records display creator email addresses rather than numeric IDs
   - This helps administrators and users quickly recognize the source of violations

2. **Record Traceability**:
   - Each violation is clearly associated with its creator
   - Responses to violations include email identifiers
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

---

*Update this file as new conceptual insights are discovered or the application's mental model evolves.* 