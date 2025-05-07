/**
 * Caching utility for API responses to reduce requests and avoid rate limits
 */

// In-memory cache storage
const cache = new Map();

// Default cache duration in milliseconds (5 minutes)
const DEFAULT_CACHE_DURATION = 5 * 60 * 1000;

/**
 * Gets data from cache or fetches it from API if not available
 * 
 * @param {string} url - API endpoint URL
 * @param {Object} options - Fetch options
 * @param {number} cacheDuration - Cache duration in milliseconds (default: 5 minutes)
 * @returns {Promise<any>} Resolved with the response data
 */
export const fetchWithCache = async (url, options = {}, cacheDuration = DEFAULT_CACHE_DURATION) => {
  const cacheKey = `${url}-${JSON.stringify(options)}`;
  const now = Date.now();
  
  // Check if we have a valid cached response
  if (cache.has(cacheKey)) {
    const cachedData = cache.get(cacheKey);
    if (now - cachedData.timestamp < cacheDuration) {
      console.log(`[Cache] Using cached data for ${url}`);
      return cachedData.data;
    } else {
      // Cache expired, remove it
      cache.delete(cacheKey);
    }
  }
  
  // Fetch fresh data
  try {
    console.log(`[Cache] Fetching fresh data for ${url}`);
    const response = await fetch(url, options);
    
    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`);
    }
    
    const data = await response.json();
    
    // Store in cache
    cache.set(cacheKey, {
      data,
      timestamp: now
    });
    
    return data;
  } catch (error) {
    console.error(`[Cache] Error fetching ${url}:`, error);
    throw error;
  }
};

/**
 * Invalidates cache for a specific URL
 * 
 * @param {string} url - URL to invalidate
 * @param {Object} options - Fetch options
 */
export const invalidateCache = (url, options = {}) => {
  const cacheKey = `${url}-${JSON.stringify(options)}`;
  if (cache.has(cacheKey)) {
    console.log(`[Cache] Invalidated cache for ${url}`);
    cache.delete(cacheKey);
  }
};

/**
 * Clears the entire cache
 */
export const clearCache = () => {
  console.log('[Cache] Cleared entire cache');
  cache.clear();
};

/**
 * Prefetches data into cache
 * 
 * @param {string} url - URL to prefetch
 * @param {Object} options - Fetch options
 * @param {number} cacheDuration - Cache duration in milliseconds
 */
export const prefetchToCache = async (url, options = {}, cacheDuration = DEFAULT_CACHE_DURATION) => {
  try {
    await fetchWithCache(url, options, cacheDuration);
    console.log(`[Cache] Prefetched ${url}`);
  } catch (error) {
    console.error(`[Cache] Error prefetching ${url}:`, error);
  }
}; 