import React from 'react';

export default function PaginationControls({ page, totalPages, handlePageChange }) {
  if (totalPages <= 1) return null;
  return (
    <div className="flex justify-center mt-4 gap-2">
      <button
        onClick={() => handlePageChange(1)}
        disabled={page === 1}
        className={`inline-flex items-center px-3 py-1 border rounded-md text-sm ${page === 1 ? 'text-gray-400 border-gray-200' : 'text-gray-700 border-gray-300 hover:bg-gray-50'}`}
      >
        First
      </button>
      <button
        onClick={() => handlePageChange(page - 1)}
        disabled={page === 1}
        className={`inline-flex items-center px-3 py-1 border rounded-md text-sm ${page === 1 ? 'text-gray-400 border-gray-200' : 'text-gray-700 border-gray-300 hover:bg-gray-50'}`}
      >
        Previous
      </button>
      <span className="inline-flex items-center px-3 py-1 text-sm text-gray-700">
        Page {page} of {totalPages}
      </span>
      <button
        onClick={() => handlePageChange(page + 1)}
        disabled={page === totalPages}
        className={`inline-flex items-center px-3 py-1 border rounded-md text-sm ${page === totalPages ? 'text-gray-400 border-gray-200' : 'text-gray-700 border-gray-300 hover:bg-gray-50'}`}
      >
        Next
      </button>
      <button
        onClick={() => handlePageChange(totalPages)}
        disabled={page === totalPages}
        className={`inline-flex items-center px-3 py-1 border rounded-md text-sm ${page === totalPages ? 'text-gray-400 border-gray-200' : 'text-gray-700 border-gray-300 hover:bg-gray-50'}`}
      >
        Last
      </button>
    </div>
  );
} 