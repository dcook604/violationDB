# Path Obfuscation in Violation Management System

## Overview

Path obfuscation is a security technique that replaces predictable, descriptive route paths with non-descriptive, hash-based identifiers. This approach helps prevent enumeration attacks and makes it more difficult for unauthorized users to discover and access system endpoints.

## Implementation Details

The path obfuscation system in the Violation Management System uses the following components:

1. **Route Mapper Utility** (`/frontend/src/utils/routeMapper.js`)
   - Maintains a fixed mapping between real routes and their obfuscated versions
   - Provides functions to convert between real and obfuscated routes
   - Uses a predefined dictionary of route mappings for consistent URLs

2. **Obfuscated Router Component** (`/frontend/src/components/ObfuscatedRouter.js`)
   - Intercepts all incoming requests
   - Deobfuscates hashed routes to their actual counterparts
   - Wraps the entire application to ensure all routes are properly handled

3. **Modified App.js**
   - Uses obfuscated paths for all protected routes
   - Keeps authentication routes in clear text for usability
   - Includes a catch-all route for obfuscated paths

## Route Mapping

Real routes are mapped to obfuscated paths using the following format:

| Real Route | Obfuscated Format |
|------------|-------------------|
| /dashboard | /r/d5f8a61b2e4c |
| /violations | /r/7a9c3b5d2f1e |
| /violations/new | /r/e8f2c1d5a6b3 |
| /units | /r/b4d6e8f2a1c3 |
| /units/new | /r/b4d6e8f2a1c3/new |
| /admin/users | /r/c3a5b7d9e1f2 |
| /admin/settings | /r/a1b3c5d7e9f2 |

## Security Considerations

1. **Fixed Route Mapping**
   - The current implementation uses a fixed dictionary of route mappings
   - This ensures consistency across application restarts and deployments
   - For higher security, consider regenerating these values periodically

2. **Authentication Routes**
   - Login, registration, and password reset routes remain in clear text for usability
   - These routes should still validate authentication state appropriately

3. **Limitations**
   - Path obfuscation is primarily a defense-in-depth measure
   - It should be combined with proper authentication and authorization
   - URLs can still be discovered through network monitoring or application exploration

## Usage Guidelines

1. **Internal Navigation**
   - Always use the Link component from react-router-dom for internal navigation
   - Never hardcode obfuscated paths
   - Use the obfuscateRoute() function to generate obfuscated paths
   - For secondary routes (like `/units/new`), use the obfuscated base path (`/r/b4d6e8f2a1c3`) plus the suffix (`/new`)
   - For routes with parameters, use template literals: `` `/r/b4d6e8f2a1c3/${unit.unit_number}` ``

2. **External Links**
   - For generating links to send outside the application, use the full obfuscated URL
   - Consider using public_id fields for sharable resources

3. **Troubleshooting**
   - If routes are not working, check that ObfuscatedRouter is properly implemented
   - Inspect the JavaScript console for any routing errors

## Maintenance

When adding new routes to the application:

1. Add the route mapping in the routeMap dictionary in routeMapper.js
2. Use obfuscateRoute() to generate the path in App.js
3. Update any navigation components to use the obfuscated path

## Browser Compatibility

This implementation is fully compatible with all modern browsers as it:
1. Uses a simple dictionary-based lookup rather than dynamic hash calculation
2. Avoids Node.js-specific modules like crypto
3. Handles route parameters consistently 