import React from 'react';

// Define base styles and color variants
const baseStyle = "text-sm font-bold uppercase px-6 py-3 rounded shadow hover:shadow-lg outline-none focus:outline-none mr-1 mb-1 ease-linear transition-all duration-150";

const colorStyles = {
  lightBlue: "bg-lightBlue-500 text-white active:bg-lightBlue-600",
  green: "bg-green-500 text-white active:bg-green-600",
  yellow: "bg-yellow-500 text-white active:bg-yellow-600",
  red: "bg-red-500 text-white active:bg-red-600",
  gray: "bg-gray-500 text-white active:bg-gray-600",
  // Add other Notus colors as needed (e.g., emerald, amber, etc.)
  default: "bg-blueGray-500 text-white active:bg-blueGray-600", // Default or secondary style
};

export default function Button({ 
  children, 
  onClick, 
  type = 'button', 
  disabled = false, 
  className = '', 
  color = 'default' // Add color prop with a default
}) {
  
  // Determine button classes based on color and disabled state
  const colorClass = colorStyles[color] || colorStyles.default;
  const disabledClass = disabled ? "opacity-50 cursor-not-allowed" : "";

  // By placing className at the end, it can override the predefined styles
  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={`${baseStyle} ${colorClass} ${disabledClass} ${className}`}
    >
      {children}
    </button>
  );
} 