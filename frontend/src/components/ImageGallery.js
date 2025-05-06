import React from 'react';

export default function ImageGallery({ imageUrls }) {
  if (!imageUrls || imageUrls.length === 0) return null;
  return (
    <div className="mt-2">
      <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
        {imageUrls.map((url, index) => (
          <div key={index} className="relative">
            <a href={url} target="_blank" rel="noopener noreferrer">
              <img 
                src={url}
                alt={`Upload ${index + 1}`}
                className="w-full h-auto rounded object-cover aspect-square"
              />
            </a>
          </div>
        ))}
      </div>
    </div>
  );
} 