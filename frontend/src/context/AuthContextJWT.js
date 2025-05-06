import { createContext, useContext, useState, useEffect, useCallback } from "react";
import { useNavigate } from 'react-router-dom';
import API from '../api';
import axios from 'axios';

const AuthContextJWT = createContext();

export function AuthProviderJWT({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  // Check session with JWT
  const checkSession = useCallback(async () => {
    try {
      console.log("Checking JWT session...");
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
      if (window.location.pathname !== '/login') {
        navigate('/login');
      }
    } finally {
      setLoading(false);
    }
  }, [navigate]);

  useEffect(() => {
    checkSession();
  }, [checkSession]);

  // Login function using JWT
  const login = async (credentials) => {
    try {
      setError(null);
      console.log("Attempting JWT login with:", credentials.email);
      
      // Use the API client instead of direct axios call
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
      await API.post('/api/auth/refresh-jwt');
      return true;
    } catch (error) {
      console.error('JWT token refresh failed:', error);
      return false;
    }
  };

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
      isAuthenticated: !!user 
    }}>
      {children}
    </AuthContextJWT.Provider>
  );
}

export function useAuthJWT() {
  return useContext(AuthContextJWT);
} 