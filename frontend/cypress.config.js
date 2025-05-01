const { defineConfig } = require('cypress');

module.exports = defineConfig({
  e2e: {
    specPattern: 'cypress/e2e/**/*.cy.js',
    baseUrl: 'http://localhost:3000', // Adjust if your React app runs on a different port
    supportFile: false
  }
}); 