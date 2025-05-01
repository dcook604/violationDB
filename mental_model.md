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

---

*Update this file as new conceptual insights are discovered or the application's mental model evolves.* 