describe('User Management E2E', () => {
  beforeEach(() => {
    // Assume cy.loginAsAdmin() is a custom command for admin login
    cy.loginAsAdmin();
    cy.visit('/admin/users');
  });

  it('can add a user', () => {
    cy.contains('Add User').click();
    cy.get('input[name="first_name"]').type('Test');
    cy.get('input[name="last_name"]').type('User');
    cy.get('input[name="email"]').type('testuser@example.com');
    cy.get('select[name="role"]').select('User');
    cy.get('select[name="position"]').select('Caretaker');
    cy.get('input[name="defaultPassword"]').type('changeme123');
    cy.get('input[name="is_active"]').check();
    cy.contains('Add').click();
    cy.contains('testuser@example.com');
  });

  it('can search for a user', () => {
    cy.get('input[placeholder*="Search"]').type('testuser');
    cy.contains('testuser@example.com');
  });

  it('can edit a user', () => {
    cy.contains('testuser@example.com').parent().contains('Edit').click();
    cy.get('input[name="email"]').clear().type('editeduser@example.com');
    cy.get('select[name="role"]').select('admin');
    cy.contains('Save').click();
    cy.contains('editeduser@example.com');
  });

  it('can change a user password', () => {
    cy.contains('editeduser@example.com').parent().contains('Change Password').click();
    cy.get('input[name="password"]').type('newpassword123');
    cy.contains('Change').click();
    cy.contains('User Management'); // Modal closes
  });

  it('can delete a user', () => {
    cy.contains('editeduser@example.com').parent().contains('Delete').click();
    cy.contains('Delete').click();
    cy.contains('editeduser@example.com').should('not.exist');
  });
}); 