// jest-dom adds custom jest matchers for asserting on DOM nodes.
// allows you to do things like:
// expect(element).toHaveTextContent(/react/i)
// learn more: https://github.com/testing-library/jest-dom
import '@testing-library/jest-dom';

// Test API imports to help debug build issues
test('API module can be imported', () => {
  expect(() => require('../src/api')).not.toThrow();
});
