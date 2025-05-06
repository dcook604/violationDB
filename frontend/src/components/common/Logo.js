import React, { useState, useEffect } from 'react';

export default function Logo({ src, alt, base64Fallback, containerClassName = '' }) {
  const [logoError, setLogoError] = useState(false);

  useEffect(() => {
    setLogoError(false);
    if (!src) return;
    const img = new window.Image();
    img.onerror = () => setLogoError(true);
    img.onload = () => setLogoError(false);
    img.src = src;
  }, [src]);

  const logoStyles = {
    maxWidth: '100%',
    width: 'auto',
    height: 'auto',
    display: 'block',
    objectFit: 'contain',
    minWidth: '150px',
  };

  return (
    <div className={`flex justify-center items-center mb-5 min-h-[80px] bg-white p-2 rounded shadow ${containerClassName}`}>
      <img
        src={logoError ? base64Fallback : src}
        alt={alt}
        style={logoStyles}
        onError={() => setLogoError(true)}
      />
      {logoError && (
        <div className="text-red-500 text-xs mt-2 ml-2">Logo could not be loaded from path.</div>
      )}
    </div>
  );
} 