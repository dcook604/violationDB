import React from 'react';
import { useLocation } from 'react-router-dom';

/**
 * Component that handles route obfuscation/deobfuscation
 * Sits at the root route level to intercept all requests
 * Now just passes through to children as we're using obfuscated paths directly
 */
const ObfuscatedRouter = ({ children }) => {
  const location = useLocation();
  const currentPath = location.pathname;
  
  // We don't need to deobfuscate paths anymore since we're using the obfuscated paths directly in our routes
  // This component now just passes through to its children
  return <>{children}</>;
};

export default ObfuscatedRouter; 