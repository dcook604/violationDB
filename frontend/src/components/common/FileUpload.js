import React from 'react';

export default function FileUpload({ value, error, onChange, accept, maxFiles, maxFileSizeMB }) {
  return (
    <div className="mb-4">
      <label className="block font-semibold mb-1">Attach Evidence</label>
      <input
        type="file"
        multiple
        accept={accept}
        onChange={onChange}
        className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
      />
      <div className="text-xs text-gray-500 mt-1">
        Max {maxFiles} files, each ≤ {maxFileSizeMB}MB
      </div>
      {value && value.length > 0 && (
        <ul className="mt-2 text-xs text-gray-700">
          {Array.from(value).map((file, idx) => (
            <li key={idx}>{file.name} ({(file.size / 1024 / 1024).toFixed(2)} MB)</li>
          ))}
        </ul>
      )}
      {error && <div className="text-red-500 text-xs mt-1">{error}</div>}
    </div>
  );
} 