import React from 'react';
import Spinner from './Spinner';

function LoadingOverlay({ isLoading, message = 'Processing...', opacity = 50 }) {
  if (!isLoading) return null;

  return (
    <div 
      className="fixed inset-0 flex flex-col items-center justify-center z-50"
      style={{ 
        backgroundColor: 'rgba(0, 0, 0, 0.5)',
        backdropFilter: 'blur(2px)'
      }}
    >
      <div className="bg-white bg-opacity-90 rounded-lg shadow-xl p-6 max-w-md mx-auto flex flex-col items-center">
        <Spinner size="lg" color="blue" className="mb-3" />
        <div className="text-gray-800 text-md font-medium text-center">{message}</div>
      </div>
    </div>
  );
}

export default LoadingOverlay; 