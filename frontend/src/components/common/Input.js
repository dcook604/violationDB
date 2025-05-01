import React from 'react';

export default function Input({ name, value, onChange, type = 'text', placeholder = '', className = '', ...rest }) {
  return (
    <input
      name={name}
      value={value}
      onChange={onChange}
      type={type}
      placeholder={placeholder}
      className={`border p-2 rounded w-full focus:outline-none focus:ring-2 focus:ring-blue-500 ${className}`}
      {...rest}
    />
  );
} 