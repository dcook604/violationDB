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

## System Workflows

### User Creation Flow
1. Admin creates user with email and role
2. System generates temporary password
3. User logs in with temporary password
4. User must set permanent password

### Password Reset Flow
1. Admin initiates password reset
2. System generates new temporary password
3. User logs in with temporary password
4. User sets new permanent password

### Role Management
- Role changes automatically update admin status
- Admin role always includes active status
- Role changes preserve existing user data 