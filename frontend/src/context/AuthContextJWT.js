import { createContext, useContext, useState, useEffect, useCallback } from "react";
import { useNavigate } from 'react-router-dom';
import API from '../api';

const AuthContextJWT = createContext();

export function AuthProviderJWT({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  // Function to fetch CSRF token
  const fetchCsrfToken = useCallback(async () => {
    try {
      const response = await API.get('/api/csrf-token');
      API.defaults.headers.common['X-CSRF-TOKEN'] = response.data.token;
      return response.data.token;
    } catch (error) {
      console.error('Failed to fetch CSRF token:', error);
      return null;
    }
  }, []);

  // Check session with JWT
  const checkSession = useCallback(async () => {
    try {
      console.log("Checking JWT session...");
      // Fetch CSRF token first if needed for any subsequent requests
      await fetchCsrfToken();
      
      const response = await API.get('/api/auth/status-jwt');
      console.log("JWT session response:", response.data);
      
      if (response.data.user) {
        setUser(response.data.user);
        if (window.location.pathname === '/login') {
          navigate('/dashboard');
        }
      } else {
        console.log("No user in JWT session response");
        setUser(null);
      }
    } catch (error) {
      console.log('JWT session check failed:', error);
      setUser(null);
      // Only redirect to login if not already there
      if (window.location.pathname !== '/login') {
        navigate('/login');
      }
    } finally {
      setLoading(false);
    }
  }, [navigate, fetchCsrfToken]);

  // Initialize authentication state
  useEffect(() => {
    checkSession();
  }, [checkSession]);

  // Login function using JWT
  const login = async (credentials) => {
    try {
      setError(null);
      console.log("Attempting JWT login with:", credentials.email);
      
      // Fetch CSRF token first
      await fetchCsrfToken();
      
      const response = await API.post('/api/auth/login-jwt', credentials);
      console.log("JWT login response:", response.data);
      
      if (response.data.user) {
        setUser(response.data.user);
        navigate('/dashboard');
        return response.data;
      } else {
        throw new Error("Login response missing user data");
      }
    } catch (error) {
      console.error('JWT login error:', error);
      const errorMessage = error.response?.data?.error || 'Login failed';
      setError(errorMessage);
      throw error;
    }
  };

  // Logout function using JWT
  const logout = async () => {
    try {
      console.log("Logging out with JWT...");
      // Fetch CSRF token first
      await fetchCsrfToken();
      await API.post('/api/auth/logout-jwt');
      setUser(null);
      navigate('/login');
    } catch (error) {
      console.error('JWT logout failed:', error);
    }
  };

  // Function to handle token refresh
  const refreshToken = async () => {
    try {
      console.log("Refreshing JWT token...");
      // Fetch CSRF token first
      await fetchCsrfToken();
      await API.post('/api/auth/refresh-jwt');
      return true;
    } catch (error) {
      console.error('JWT token refresh failed:', error);
      return false;
    }
  };

  // Loading indicator
  if (loading) {
    return <div className="flex justify-center items-center h-screen">
      <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
    </div>;
  }

  return (
    <AuthContextJWT.Provider value={{ 
      user, 
      login, 
      logout, 
      loading, 
      error,
      checkSession,
      refreshToken,
      fetchCsrfToken,
      isAuthenticated: !!user 
    }}>
      {children}
    </AuthContextJWT.Provider>
  );
}

export function useAuthJWT() {
  return useContext(AuthContextJWT);
} 