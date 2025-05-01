/******/ (() => { // webpackBootstrap
/******/ 	"use strict";
/*!**************************************************!*\
  !*** ./cypress/e2e/dynamic_violation_form.cy.js ***!
  \**************************************************/


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
/******/ })()
;
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiZHluYW1pY192aW9sYXRpb25fZm9ybS5jeS5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7O0FBQUFBLFFBQVEsQ0FBQyx3QkFBd0IsRUFBRSxNQUFNO0VBQ3ZDQyxVQUFVLENBQUMsTUFBTTtJQUNmO0lBQ0FDLEVBQUUsQ0FBQ0MsS0FBSyxDQUFDLGlCQUFpQixDQUFDO0VBQzdCLENBQUMsQ0FBQztFQUVGQyxFQUFFLENBQUMsc0RBQXNELEVBQUUsTUFBTTtJQUMvREYsRUFBRSxDQUFDRyxHQUFHLENBQUMsTUFBTSxDQUFDLENBQUNDLE1BQU0sQ0FBQyxNQUFNO01BQzFCSixFQUFFLENBQUNHLEdBQUcsQ0FBQyxjQUFjLENBQUMsQ0FBQ0UsSUFBSSxDQUFDQyxHQUFHLElBQUk7UUFDakMsSUFBSUEsR0FBRyxDQUFDQyxJQUFJLENBQUMsVUFBVSxDQUFDLEVBQUU7VUFDeEJQLEVBQUUsQ0FBQ1EsSUFBSSxDQUFDRixHQUFHLENBQUMsQ0FBQ0csS0FBSyxDQUFDLENBQUM7UUFDdEI7TUFDRixDQUFDLENBQUM7TUFDRlQsRUFBRSxDQUFDRyxHQUFHLENBQUMsdUJBQXVCLENBQUMsQ0FBQ08sS0FBSyxDQUFDLENBQUM7SUFDekMsQ0FBQyxDQUFDO0lBQ0ZWLEVBQUUsQ0FBQ0csR0FBRyxDQUFDLDZCQUE2QixDQUFDLENBQUNRLE1BQU0sQ0FBQyxPQUFPLENBQUM7RUFDdkQsQ0FBQyxDQUFDO0VBRUZULEVBQUUsQ0FBQyxrQ0FBa0MsRUFBRSxNQUFNO0lBQzNDRixFQUFFLENBQUNHLEdBQUcsQ0FBQyxNQUFNLENBQUMsQ0FBQ0MsTUFBTSxDQUFDLE1BQU07TUFDMUJKLEVBQUUsQ0FBQ0csR0FBRyxDQUFDLDRCQUE0QixDQUFDLENBQUNTLElBQUksQ0FBQyxRQUFRLENBQUM7TUFDbkQ7TUFDQVosRUFBRSxDQUFDRyxHQUFHLENBQUMsdUJBQXVCLENBQUMsQ0FBQ08sS0FBSyxDQUFDLENBQUM7SUFDekMsQ0FBQyxDQUFDO0lBQ0ZWLEVBQUUsQ0FBQ2EsUUFBUSxDQUFDLHFCQUFxQixDQUFDLENBQUNGLE1BQU0sQ0FBQyxPQUFPLENBQUM7RUFDcEQsQ0FBQyxDQUFDO0FBQ0osQ0FBQyxDQUFDLEMiLCJzb3VyY2VzIjpbIndlYnBhY2s6Ly9mcm9udGVuZC8uL2N5cHJlc3MvZTJlL2R5bmFtaWNfdmlvbGF0aW9uX2Zvcm0uY3kuanMiXSwic291cmNlc0NvbnRlbnQiOlsiZGVzY3JpYmUoJ0R5bmFtaWMgVmlvbGF0aW9uIEZvcm0nLCAoKSA9PiB7XG4gIGJlZm9yZUVhY2goKCkgPT4ge1xuICAgIC8vIEFkanVzdCB0aGUgcGF0aCBpZiB5b3VyIGZvcm0gaXMgYXQgYSBkaWZmZXJlbnQgcm91dGVcbiAgICBjeS52aXNpdCgnL3Zpb2xhdGlvbnMvbmV3Jyk7XG4gIH0pO1xuXG4gIGl0KCdyZW5kZXJzIGR5bmFtaWMgZmllbGRzIGFuZCB2YWxpZGF0ZXMgcmVxdWlyZWQgZmllbGRzJywgKCkgPT4ge1xuICAgIGN5LmdldCgnZm9ybScpLndpdGhpbigoKSA9PiB7XG4gICAgICBjeS5nZXQoJ2lucHV0LHNlbGVjdCcpLmVhY2goJGVsID0+IHtcbiAgICAgICAgaWYgKCRlbC5hdHRyKCdyZXF1aXJlZCcpKSB7XG4gICAgICAgICAgY3kud3JhcCgkZWwpLmNsZWFyKCk7XG4gICAgICAgIH1cbiAgICAgIH0pO1xuICAgICAgY3kuZ2V0KCdidXR0b25bdHlwZT1cInN1Ym1pdFwiXScpLmNsaWNrKCk7XG4gICAgfSk7XG4gICAgY3kuZ2V0KCcudGV4dC1kYW5nZXIsIC5hbGVydC1kYW5nZXInKS5zaG91bGQoJ2V4aXN0Jyk7XG4gIH0pO1xuXG4gIGl0KCdzdWJtaXRzIHRoZSBmb3JtIHdpdGggdmFsaWQgZGF0YScsICgpID0+IHtcbiAgICBjeS5nZXQoJ2Zvcm0nKS53aXRoaW4oKCkgPT4ge1xuICAgICAgY3kuZ2V0KCdpbnB1dFtuYW1lPVwidmVoaWNsZV9tYWtlXCJdJykudHlwZSgnVG95b3RhJyk7XG4gICAgICAvLyBBZGQgbW9yZSBmaWVsZHMgYXMgbmVlZGVkXG4gICAgICBjeS5nZXQoJ2J1dHRvblt0eXBlPVwic3VibWl0XCJdJykuY2xpY2soKTtcbiAgICB9KTtcbiAgICBjeS5jb250YWlucygnVmlvbGF0aW9uIHN1Ym1pdHRlZCcpLnNob3VsZCgnZXhpc3QnKTtcbiAgfSk7XG59KTsgIl0sIm5hbWVzIjpbImRlc2NyaWJlIiwiYmVmb3JlRWFjaCIsImN5IiwidmlzaXQiLCJpdCIsImdldCIsIndpdGhpbiIsImVhY2giLCIkZWwiLCJhdHRyIiwid3JhcCIsImNsZWFyIiwiY2xpY2siLCJzaG91bGQiLCJ0eXBlIiwiY29udGFpbnMiXSwic291cmNlUm9vdCI6IiJ9