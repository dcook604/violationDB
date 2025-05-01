import axios from 'axios';

const API = axios.create({
  baseURL: 'http://localhost:5004',  // Direct to backend server instead of using proxy
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
});

// Add request interceptor to handle request configuration
API.interceptors.request.use(
  (config) => {
    // Ensure withCredentials is set for all requests
    config.withCredentials = true;
    console.log(`API Request: ${config.method.toUpperCase()} ${config.url}`);
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
    return response;
  },
  (error) => {
    // Handle network errors
    if (!error.response) {
      console.error('Network Error:', error);
      return Promise.reject({
        response: {
          data: {
            error: 'Network error. Please check your connection and try again.'
          }
        }
      });
    }

    // Handle 401 Unauthorized
    if (error.response.status === 401) {
      console.log('Unauthorized response received');
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }

    // Handle other error responses
    const errorMessage = error.response.data?.error || 'An error occurred';
    error.message = errorMessage;
    return Promise.reject(error);
  }
);

export default API; 