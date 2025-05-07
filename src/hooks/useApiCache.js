import { useState, useEffect } from 'react';
import { fetchWithCache, invalidateCache } from '../utils/apiCache';

/**
 * Custom hook for fetching API data with caching
 * 
 * @param {string} url - API endpoint URL
 * @param {Object} options - Fetch options
 * @param {number} cacheDuration - Cache duration in milliseconds (default: 5 minutes)
 * @param {boolean} skipCache - Whether to skip the cache and always fetch fresh data
 * @returns {Object} { data, loading, error, refetch }
 */
const useApiCache = (url, options = {}, cacheDuration = 5 * 60 * 1000, skipCache = false) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = async (forceRefresh = false) => {
    setLoading(true);
    try {
      if (forceRefresh) {
        // Invalidate the cache first
        invalidateCache(url, options);
      }
      
      // Use the fetchWithCache utility with the skip cache option if needed
      const fetchFn = skipCache || forceRefresh ? 
        async () => {
          const response = await fetch(url, options);
          if (!response.ok) {
            throw new Error(`API Error: ${response.status} ${response.statusText}`);
          }
          return response.json();
        } : 
        () => fetchWithCache(url, options, cacheDuration);
      
      const result = await fetchFn();
      setData(result);
      setError(null);
    } catch (err) {
      console.error('Error fetching data:', err);
      setError(err.message || 'An error occurred while fetching data');
    } finally {
      setLoading(false);
    }
  };

  // Initial data fetch
  useEffect(() => {
    fetchData();
  }, [url, JSON.stringify(options)]); // Re-fetch when URL or options change

  // Function to manually refetch data
  const refetch = (forceRefresh = true) => fetchData(forceRefresh);

  return { data, loading, error, refetch };
};

export default useApiCache; 