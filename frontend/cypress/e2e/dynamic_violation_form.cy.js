describe('Dynamic Violation Form', () => {
  beforeEach(() => {
    // Adjust the path if your form is at a different route
    cy.visit('/violations/new');
  });

  it('renders dynamic fields and validates required fields', () => {
    cy.get('form').within(() => {
      cy.get('input,select').each($el => {
        if ($el.attr('required')) {
          cy.wrap($el).clear();
        }
      });
      cy.get('button[type="submit"]').click();
    });
    cy.get('.text-danger, .alert-danger').should('exist');
  });

  it('submits the form with valid data', () => {
    cy.get('form').within(() => {
      cy.get('input[name="vehicle_make"]').type('Toyota');
      // Add more fields as needed
      cy.get('button[type="submit"]').click();
    });
    cy.contains('Violation submitted').should('exist');
  });
}); 