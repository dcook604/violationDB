# Quick Reference

This file provides a quick reference for parameters, configurations, and usage examples for the Strata Violation Log application.

## Login Form Fields
- **email**: User's email address (required)
- **password**: User's password (required)
- **remember**: Boolean checkbox for persistent login

## Example Usage
```html
<form method="post">
  {{ form.hidden_tag() }}
  {{ form.email(class="form-control", placeholder="Email") }}
  {{ form.password(class="form-control", placeholder="Password") }}
  {{ form.remember(class="form-check-input") }}
</form>
```

## Configuration
- Static files referenced via `url_for('static', filename='...')`
- Flash messages for error handling

## Dynamic Violation Fields

### Models
- **FieldDefinition**: id, name, label, type, required, options, order, active
- **ViolationFieldValue**: id, violation_id, field_definition_id, value

### API Endpoints
- `GET/POST /api/admin/fields/`: List/create field definitions
- `GET/PUT/DELETE /api/admin/fields/<id>`: Retrieve/update/delete/toggle field
- `POST /api/admin/fields/reorder`: Update order of fields
- `GET/POST /api/violations/`: Accept/return dynamic fields
- `GET/PUT /api/violations/<id>`: Support dynamic field editing

### Example Field Definition (JSON)
```json
{
  "name": "vehicle_make",
  "label": "Vehicle Make",
  "type": "text",
  "required": true,
  "order": 1,
  "active": true
}
```

### Example Violation Submission (JSON)
```json
{
  "date": "2024-06-01",
  "location": "Lot 5",
  "fields": [
    {"field_definition_id": 1, "value": "Toyota"},
    {"field_definition_id": 2, "value": "Red"}
  ]
}
```

## React Component Usage

### AdminFieldManager
```jsx
import AdminFieldManager from './components/AdminFieldManager';
<AdminFieldManager />
```

### DynamicViolationForm
```jsx
import DynamicViolationForm from './components/DynamicViolationForm';
<DynamicViolationForm onSubmit={handleSubmit} initialValues={existingValues} submitLabel="Save" />
```

## API Endpoints (Frontend)
- `GET /api/fields` — List all field definitions
- `POST /api/fields` — Create new field
- `PUT /api/fields/:id` — Update field
- `DELETE /api/fields/:id` — Delete field
- `POST /api/fields/:id/toggle` — Toggle active/inactive
- `POST /api/fields/reorder` — Reorder fields
- `GET /api/violations/:id/fields` — Get field values for a violation

## API: GET /api/violations
- Returns a list of violations.
- Admins: all violations. Users: only their own.
- Each violation: id, reference, category, building, unit_number, incident_date, subject, details, created_at, created_by, dynamic_fields (object).

## React: <ViolationList />
- Fetches and displays violations in a table.
- Shows reference, category, created_at, and all dynamic fields.
- Route: /violations (protected).

## API: GET /api/violations/:id
- Returns details for a single violation (role-protected).
- Admins: any violation. Users: only their own.
- Returns: id, reference, category, building, unit_number, incident_date, subject, details, created_at, created_by, dynamic_fields (object).

## React: <ViolationDetail />
- Fetches and displays details for a single violation.
- Route: /violations/:id (protected).

## API: PUT /api/violations/:id
- Edit a violation (role-protected).
- Body: JSON with any of category, building, unit_number, incident_date, subject, details, dynamic_fields (object).
- Returns: { success: true }

## API: DELETE /api/violations/:id
- Delete a violation (role-protected).
- Returns: { success: true }

## React: <ViolationDetail />
- Edit and delete actions available for admins and owners.
- Edit: Inline form for static and dynamic fields, saves via PUT.
- Delete: Confirms and deletes via DELETE, then redirects.

## React: <Table />
- Reusable table component.
- Props: columns (array of {label, accessor}), data (array), renderCell (optional function).
- Example:
```jsx
<Table columns={[{label: 'Email', accessor: 'email'}]} data={users} />
```

## React: <Modal />
- Reusable modal dialog.
- Props: isOpen, onClose, title, children, actions (optional).
- Example:
```jsx
<Modal isOpen={show} onClose={close} title="Confirm">Are you sure?</Modal>
```

## API: /api/users
- `GET /api/users` — List users (admin only)
- `POST /api/users` — Create user (admin only)
- `PUT /api/users/:id` — Edit user (admin only)
- `DELETE /api/users/:id` — Delete user (admin only, cannot self-delete)
- `POST /api/users/:id/change-password` — Change password (admin or self)

## Quick Reference Guide

## UI Components Quick Reference

### Common Notus React Classes

#### Layout
```css
/* Container */
.container .mx-auto .px-4

/* Card */
.relative .flex .flex-col .min-w-0 .break-words .w-full .mb-6 .shadow-lg .rounded-lg .bg-white .border-0

/* Section */
.px-4 .lg:px-10 .py-10
```

#### Forms
```css
/* Input Field */
.border-0 .px-3 .py-3 .placeholder-blueGray-300 .text-blueGray-600 .bg-white .rounded .text-sm .shadow .focus:outline-none .focus:ring .w-full .ease-linear .transition-all .duration-150

/* Label */
.block .uppercase .text-blueGray-600 .text-xs .font-bold .mb-2

/* Button Primary */
.bg-lightBlue-500 .text-white .active:bg-lightBlue-600 .text-sm .font-bold .uppercase .px-6 .py-3 .rounded .shadow .hover:shadow-lg .outline-none .focus:outline-none .mr-1 .mb-1 .w-full .ease-linear .transition-all .duration-150

/* Button Danger */
.bg-red-500 .text-white .active:bg-red-600 /* Same modifiers as primary */
```

#### Typography
```css
/* Headings */
.text-blueGray-700 .text-xl .font-bold /* Large */
.text-blueGray-600 .text-lg .font-semibold /* Medium */
.text-blueGray-500 .text-sm .font-bold /* Small */

/* Body Text */
.text-blueGray-500 .text-sm /* Regular */
.text-blueGray-400 .text-xs /* Small */
```

#### Navigation
```css
/* Nav Link */
.text-blueGray-700 .hover:text-blueGray-500 .px-3 .py-4 .lg:py-2 .flex .items-center .text-xs .uppercase .font-bold

/* Active Nav Link */
.text-lightBlue-500 .hover:text-lightBlue-600
```

## Error Handling Best Practices

### Database Operations

- **Safe Attribute Access**
  ```python
  # Unsafe
  value = model.attribute
  
  # Safe
  value = getattr(model, 'attribute', default_value)
  ```

- **Attribute Existence Check**
  ```python
  # Check before using
  if hasattr(model, 'attribute'):
      process(model.attribute)
  ```

- **Try/Except for Database Operations**
  ```python
  try:
      result = query.all()
  except Exception as e:
      logger.error(f"Database error: {str(e)}")
      result = []  # Default value
  ```

- **Raw SQL for Schema Stability**
  ```python
  from sqlalchemy import text
  
  # Direct SQL query that only uses known columns
  sql = "SELECT id, name FROM table"
  result = db.session.execute(text(sql))
  ```

### API Response Strategy

- Return sensible defaults instead of errors when possible
- Log errors server-side with sufficient context
- Don't expose internal error details to clients
- Favor empty collections over null values for arrays

---

*Update this file as new parameters, configurations, or usage examples are added or changed.* 