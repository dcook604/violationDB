describe('Admin Field Manager', () => {
  beforeEach(() => {
    // Adjust the path if your admin UI is at a different route
    cy.visit('/admin');
  });

  it('can add a new field', () => {
    cy.get('input[name="name"]').type('vehicle_make');
    cy.get('input[name="label"]').type('Vehicle Make');
    cy.get('select[name="type"]').select('Text');
    cy.get('button[type="submit"]').click();
    cy.contains('Vehicle Make');
  });

  it('can edit a field', () => {
    cy.contains('Vehicle Make').parent().find('button').contains('Edit').click();
    cy.get('input[name="label"]').clear().type('Car Make');
    cy.get('button[type="submit"]').click();
    cy.contains('Car Make');
  });

  it('can delete a field', () => {
    cy.contains('Car Make').parent().find('button').contains('Delete').click();
    cy.on('window:confirm', () => true);
    cy.contains('Car Make').should('not.exist');
  });
}); 