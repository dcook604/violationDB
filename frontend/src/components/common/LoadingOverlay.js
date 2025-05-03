import React from 'react';
import Spinner from './Spinner';

function LoadingOverlay({ isLoading, message = 'Processing...', opacity = 80 }) {
  if (!isLoading) return null;

  return (
    <div 
      className={`fixed inset-0 flex flex-col items-center justify-center z-50 bg-black bg-opacity-${opacity}`}
      style={{ backdropFilter: 'blur(2px)' }}
    >
      <Spinner size="xl" color="white" className="mb-4" />
      <div className="text-white text-lg font-semibold">{message}</div>
    </div>
  );
}

export default LoadingOverlay; 