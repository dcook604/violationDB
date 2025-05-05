import React, { useState, useContext } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import API from '../api';
import Input from '../components/common/Input';
import Button from '../components/common/Button';
import LoadingOverlay from '../components/common/LoadingOverlay';

function LoginPage() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const navigate = useNavigate();
    const { login } = useContext(AuthContext);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');

    const handleLogin = async (e) => {
        e.preventDefault();
        setIsLoading(true);
        setError('');
        try {
            const response = await API.post('/api/auth/login', { email, password });
            if (response.data.user) {
                login(response.data.user);
                navigate('/dashboard');
            } else {
                setError('Login failed. Please check your credentials.');
            }
        } catch (err) {
             console.error("Login error response:", err.response);
             const errorMsg = err.response?.data?.error || 'Login failed. Please check your credentials or try again later.';
             setError(errorMsg);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-100">
            <LoadingOverlay isLoading={isLoading} message="Logging in..." />
            <div className="bg-white p-8 rounded-lg shadow-md w-full max-w-md">
                <h2 className="text-2xl font-bold mb-6 text-center text-gray-800">Login</h2>
                {error && <p className="text-red-500 text-center mb-4">{error}</p>}
                <form onSubmit={handleLogin}>
                     <Input
                         label="Email Address"
                         id="email"
                         type="email"
                         value={email}
                         onChange={(e) => setEmail(e.target.value)}
                         required
                         placeholder="you@example.com"
                     />
                     <Input
                         label="Password"
                         id="password"
                         type="password"
                         value={password}
                         onChange={(e) => setPassword(e.target.value)}
                         required
                         placeholder="Enter your password"
                         className="mt-4"
                     />
                    <div className="text-sm text-center mt-4 mb-6">
                        <Link
                            to="/forgot-password"
                            className="font-medium text-blue-600 hover:text-blue-500"
                        >
                            Forgot password?
                        </Link>
                    </div>
                    <Button type="submit" variant="primary" fullWidth disabled={isLoading}>
                        {isLoading ? 'Logging in...' : 'Login'}
                    </Button>
                </form>
            </div>
        </div>
    );
}

export default LoginPage; 