import { createContext, useContext, useState, useEffect, useCallback } from "react";
import { useNavigate } from 'react-router-dom';
import API from '../api';

const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const checkSession = useCallback(async () => {
    try {
      console.log("Checking session...");
      const response = await API.get('/api/auth/session');
      console.log("Session response:", response.data);
      
      if (response.data.user) {
        setUser(response.data.user);
        if (window.location.pathname === '/login') {
          navigate('/dashboard');
        }
      } else {
        console.log("No user in session response");
        setUser(null);
      }
    } catch (error) {
      console.log('Session check failed:', error);
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

  const login = async (credentials) => {
    try {
      setError(null);
      console.log("Attempting login with:", credentials.email);
      
      const response = await API.post('/api/auth/login', credentials);
      console.log("Login response:", response.data);
      
      if (response.data.user) {
        setUser(response.data.user);
        navigate('/dashboard');
        return response.data;
      } else {
        throw new Error("Login response missing user data");
      }
    } catch (error) {
      console.error('Login error:', error);
      const errorMessage = error.response?.data?.error || 'Login failed';
      setError(errorMessage);
      throw error;
    }
  };

  const logout = async () => {
    try {
      console.log("Logging out...");
      await API.post('/api/auth/logout');
      setUser(null);
      navigate('/login');
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  if (loading) {
    return <div className="flex justify-center items-center h-screen">
      <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
    </div>;
  }

  return (
    <AuthContext.Provider value={{ 
      user, 
      login, 
      logout, 
      loading, 
      error,
      checkSession,
      isAuthenticated: !!user 
    }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
} 