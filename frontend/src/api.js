import axios from 'axios';

const API = axios.create({
  baseURL: 'http://172.16.16.6:5004',  // Ensure this matches your backend server IP
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
});

// Keep track of refresh attempts to prevent infinite loops
let isRefreshing = false;
let failedQueue = [];

// Process the queue of failed requests
const processQueue = (error) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve();
    }
  });
  
  failedQueue = [];
};

// Add request interceptor to handle request configuration
API.interceptors.request.use(
  (config) => {
    config.withCredentials = true;
    
    // Add cache control headers for GET requests to prevent caching
    if (config.method === 'get') {
      config.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate';
      config.headers['Pragma'] = 'no-cache';
      config.headers['Expires'] = '0';
    }
    
    // Log the request for debugging
    console.log(`API Request: ${config.method.toUpperCase()} ${config.url}`);
    
    // Check if there's a token in localStorage that we can use as a fallback
    const token = localStorage.getItem('access_token');
    if (token && !config.headers.Authorization) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor to handle responses and errors
API.interceptors.response.use(
  (response) => {
    console.log(`API Response: ${response.status} for ${response.config.url}`);
    // Handle redirect responses
    if (response.data && response.data.redirect) {
      window.location.href = response.data.location;
      return Promise.reject('Redirect');
    }
    
    // If response includes a token, store it
    if (response.headers && response.headers.authorization) {
      const token = response.headers.authorization.replace('Bearer ', '');
      localStorage.setItem('access_token', token);
    }
    
    return response;
  },
  async (error) => {
    // Get the original request configuration
    const originalRequest = error.config;
    
    // Handle network errors
    if (!error.response) {
      console.error('Network Error:', error);
      
      return Promise.reject({
        response: {
          data: {
            error: 'Network error. Server may be unavailable or not accessible at this address. Please check your connection and try again.'
          }
        }
      });
    }
    
    // Handle 401 Unauthorized with token refresh
    if (error.response.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        // If a refresh is already in progress, queue this request
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        })
          .then(() => {
            // Retry the request when the token has been refreshed
            return API(originalRequest);
          })
          .catch(err => {
            // Handle refresh failure
            return Promise.reject(err);
          });
      }

      // Mark this request as retried to prevent infinite loop
      originalRequest._retry = true;
      isRefreshing = true;

      try {
        // Try to refresh the token
        const refreshResponse = await API.post('/api/auth/refresh-jwt');
        
        // If the token was refreshed successfully, store the new token
        if (refreshResponse.data && refreshResponse.data.access_token) {
          localStorage.setItem('access_token', refreshResponse.data.access_token);
        }
        
        // Refresh successful, mark refresh as complete
        isRefreshing = false;
        
        // Process any queued requests
        processQueue(null);
        
        // Retry the original request
        return API(originalRequest);
      } catch (refreshError) {
        // Refresh failed
        isRefreshing = false;
        
        // Clear stored token if refresh failed
        localStorage.removeItem('access_token');
        
        // Process queued requests with error
        processQueue(refreshError);
        
        // If refresh failed and we're not on the login page, redirect to login
        if (window.location.pathname !== '/login') {
          console.log('Token refresh failed, redirecting to login');
          window.location.href = '/login';
        }
        
        return Promise.reject(refreshError);
      }
    }

    // Handle other error responses
    const errorMessage = error.response.data?.error || error.response.data?.message || 'An error occurred';
    error.message = errorMessage;
    console.error(`API Error (${error.response.status}):`, errorMessage);
    return Promise.reject(error);
  }
);

export default API; 