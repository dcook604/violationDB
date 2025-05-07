import { createContext, useContext, useState, useEffect, useCallback } from "react";
import { useNavigate } from 'react-router-dom';
import API from '../api';
import { setSentryUser } from '../utils/sentry';

const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isRemembered, setIsRemembered] = useState(
    localStorage.getItem('auth_remember') === 'true'
  );
  const navigate = useNavigate();

  // Update Sentry user context when user state changes
  useEffect(() => {
    setSentryUser(user);
  }, [user]);

  const checkSession = useCallback(async () => {
    try {
      console.log("Checking session...");
      const response = await API.get('/api/auth/status-jwt');
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
      if (window.location.pathname !== '/login' && 
          !window.location.pathname.includes('/violations/public/') &&
          !window.location.pathname.includes('/forgot-password') &&
          !window.location.pathname.includes('/reset-password/')) {
        navigate('/login');
      }
    } finally {
      setLoading(false);
    }
  }, [navigate]);

  // Function to refresh the token
  const refreshToken = useCallback(async () => {
    try {
      console.log("Refreshing token...");
      await API.post('/api/auth/refresh-jwt');
      return true;
    } catch (error) {
      console.error('Token refresh failed:', error);
      return false;
    }
  }, []);

  useEffect(() => {
    // Failsafe: set loading to false after 5 seconds no matter what
    const timeout = setTimeout(() => setLoading(false), 5000);
    checkSession();
    
    // Set up automatic refresh based on remember me status
    const refreshInterval = setInterval(() => {
      if (user) {
        refreshToken().catch(() => {
          // If refresh fails, check session again
          checkSession();
        });
      }
    }, isRemembered ? 6 * 60 * 60 * 1000 : 25 * 60 * 1000); // 6 hours if remembered, 25 minutes otherwise
    
    return () => {
      clearTimeout(timeout);
      clearInterval(refreshInterval);
    };
  }, [checkSession, refreshToken, user, isRemembered]);

  const login = async (credentials, remember = false) => {
    try {
      setError(null);
      console.log("Attempting login with:", credentials.email);
      
      // Store remember me preference
      setIsRemembered(remember);
      localStorage.setItem('auth_remember', remember ? 'true' : 'false');
      
      // Use JWT login endpoint which has CSRF exemption
      const response = await API.post('/api/auth/login-jwt', {
        ...credentials,
        remember: remember
      });
      
      console.log("Login response:", response.data);
      
      // JWT login returns user differently
      if (response.data.user) {
        setUser(response.data.user);
        navigate('/dashboard');
        return response.data;
      } else if (response.data.login === true && response.data.user) {
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
      await API.post('/api/auth/logout-jwt');
      setUser(null);
      // Clear the remember me flag on logout
      localStorage.removeItem('auth_remember');
      setIsRemembered(false);
      navigate('/login');
    } catch (error) {
      console.error('Logout failed:', error);
      // Still clear user data on client side even if server logout fails
      setUser(null);
      localStorage.removeItem('auth_remember');
      setIsRemembered(false);
      navigate('/login');
    }
  };

  if (loading) {
    console.log("AuthProvider loading:", loading, "user:", user);
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
      refreshToken,
      isAuthenticated: !!user,
      isAdmin: user?.is_admin || false,
      isRemembered 
    }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
} 