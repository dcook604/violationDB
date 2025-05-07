import * as Sentry from "@sentry/react";

/**
 * Set user information for Sentry error tracking
 * @param {Object} user - The user object
 */
export const setSentryUser = (user) => {
  if (!user) {
    Sentry.setUser(null);
    return;
  }

  Sentry.setUser({
    id: user.id,
    email: user.email, 
    role: user.role || 'user',
    isAdmin: user.is_admin || false
  });
};

/**
 * Add tags to the current Sentry scope
 * @param {Object} tags - Object with key-value pairs to add as tags
 */
export const addSentryTags = (tags) => {
  if (!tags || typeof tags !== 'object') return;
  
  Object.entries(tags).forEach(([key, value]) => {
    Sentry.setTag(key, value);
  });
};

/**
 * Add extra context to the current Sentry scope
 * @param {Object} context - Context information to add
 */
export const addSentryContext = (context) => {
  if (!context || typeof context !== 'object') return;
  
  Object.entries(context).forEach(([key, value]) => {
    Sentry.setContext(key, value);
  });
};

/**
 * Capture exception with Sentry
 * @param {Error} error - The error to capture
 * @param {Object} context - Additional context to include
 */
export const captureException = (error, context = {}) => {
  if (context && Object.keys(context).length > 0) {
    // Set additional context before capturing
    Object.entries(context).forEach(([key, value]) => {
      Sentry.setContext(key, value);
    });
  }
  
  Sentry.captureException(error);
};

/**
 * Capture a message with Sentry
 * @param {string} message - The message to capture
 * @param {string} level - The level (info, warning, error)
 * @param {Object} context - Additional context to include
 */
export const captureMessage = (message, level = 'info', context = {}) => {
  if (context && Object.keys(context).length > 0) {
    // Set additional context before capturing
    Object.entries(context).forEach(([key, value]) => {
      Sentry.setContext(key, value);
    });
  }
  
  Sentry.captureMessage(message, level);
};

export default {
  setSentryUser,
  addSentryTags,
  addSentryContext,
  captureException,
  captureMessage
}; 