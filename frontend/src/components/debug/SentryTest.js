import React, { useState } from 'react';
import * as Sentry from "@sentry/react";
import { captureMessage, captureException } from '../../utils/sentry';

const SentryTest = () => {
  const [message, setMessage] = useState('');
  const [messageLevel, setMessageLevel] = useState('info');
  
  const handleCaptureMessage = () => {
    if (!message) return;
    
    captureMessage(message, messageLevel, {
      source: 'SentryTest',
      timestamp: new Date().toISOString()
    });
    
    alert(`Message "${message}" captured with level ${messageLevel}`);
  };
  
  const handleTestError = () => {
    try {
      // Generate a test error
      throw new Error('This is a test error from SentryTest component');
    } catch (error) {
      captureException(error, {
        source: 'SentryTest',
        timestamp: new Date().toISOString()
      });
      
      alert(`Test error captured: ${error.message}`);
    }
  };
  
  const handleApiError = () => {
    // Trigger a fetch to a non-existent endpoint to test API error handling
    fetch('/api/non-existent-endpoint')
      .then(response => {
        if (!response.ok) {
          throw new Error(`API error with status ${response.status}`);
        }
        return response.json();
      })
      .catch(error => {
        captureException(error, {
          source: 'SentryTest',
          test_type: 'api_error',
          timestamp: new Date().toISOString()
        });
        
        alert(`API error captured: ${error.message}`);
      });
  };
  
  const handleComponentError = () => {
    // This will trigger the ErrorBoundary
    const obj = null;
    obj.nonExistentMethod(); // This will throw a TypeError
  };
  
  return (
    <div className="bg-white shadow-md rounded-lg p-6 max-w-lg mx-auto my-8">
      <h2 className="text-2xl font-bold mb-4">Sentry Integration Test</h2>
      
      <div className="mb-6">
        <h3 className="text-lg font-semibold mb-2">Capture Message</h3>
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-1">Message</label>
          <input
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md"
            placeholder="Enter a test message"
          />
        </div>
        
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-1">Level</label>
          <select
            value={messageLevel}
            onChange={(e) => setMessageLevel(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md"
          >
            <option value="info">Info</option>
            <option value="warning">Warning</option>
            <option value="error">Error</option>
          </select>
        </div>
        
        <button
          onClick={handleCaptureMessage}
          className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600"
        >
          Capture Message
        </button>
      </div>
      
      <div className="mb-6">
        <h3 className="text-lg font-semibold mb-2">Test Errors</h3>
        <div className="flex flex-col gap-2">
          <button
            onClick={handleTestError}
            className="px-4 py-2 bg-yellow-500 text-white rounded-md hover:bg-yellow-600"
          >
            Trigger Test Error
          </button>
          
          <button
            onClick={handleApiError}
            className="px-4 py-2 bg-orange-500 text-white rounded-md hover:bg-orange-600"
          >
            Trigger API Error
          </button>
          
          <button
            onClick={handleComponentError}
            className="px-4 py-2 bg-red-500 text-white rounded-md hover:bg-red-600"
          >
            Trigger Component Error (ErrorBoundary)
          </button>
        </div>
      </div>
      
      <div className="bg-gray-100 p-4 rounded-md">
        <p className="text-sm text-gray-700">
          Note: Ensure you have set the <code>REACT_APP_SENTRY_DSN</code> environment variable for the frontend and <code>SENTRY_DSN</code> for the backend.
        </p>
        <p className="text-sm text-gray-700 mt-2">
          Check your Sentry dashboard to see captured events.
        </p>
      </div>
    </div>
  );
};

export default SentryTest; 