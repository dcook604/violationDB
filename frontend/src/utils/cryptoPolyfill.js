/**
 * Simple crypto polyfill for environments where Node.js crypto is not available
 * This provides a minimal implementation of the createHash functionality
 */

// Using a third-party SHA-256 implementation
import sha256 from 'js-sha256';

// Polyfill for crypto.createHash
export const createHashPolyfill = (algorithm) => {
  if (algorithm !== 'sha256') {
    throw new Error('Only sha256 is supported in this polyfill');
  }

  let data = '';

  return {
    update: function(text) {
      data += text;
      return this; // 'this' now refers to the returned object
    },
    digest: function(format) {
      if (format !== 'hex') {
        throw new Error('Only hex format is supported in this polyfill');
      }
      return sha256(data);
    }
  };
};

// Always use the polyfill in browser environments
// Node.js's crypto module isn't available in browsers
const cryptoImplementation = {
  createHash: createHashPolyfill
};

export const createHash = cryptoImplementation.createHash; 