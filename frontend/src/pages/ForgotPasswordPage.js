import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import API from '../utils/api';
import InputField from '../components/common/InputField';
import Button from '../components/common/Button';
import LoadingOverlay from '../components/common/LoadingOverlay'; // Assuming you have this

function ForgotPasswordPage() {
    const [email, setEmail] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [message, setMessage] = useState('');
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsLoading(true);
        setMessage('');
        setError('');
        try {
            const response = await API.post('/api/auth/request-password-reset', { email });
            setMessage(response.data.message);
        } catch (err) {
            setError(err.response?.data?.error || 'An unexpected error occurred.');
            setMessage(''); // Clear any previous success message
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-100">
             <LoadingOverlay isLoading={isLoading} message="Requesting reset..." />
            <div className="bg-white p-8 rounded-lg shadow-md w-full max-w-md">
                <h2 className="text-2xl font-bold mb-6 text-center text-gray-800">Forgot Password</h2>
                <p className="text-center text-gray-600 mb-6">
                    Enter your email address below, and we'll send you a link to reset your password if an account exists.
                </p>
                {message && <p className="text-green-600 bg-green-100 border border-green-300 p-3 rounded text-center mb-4">{message}</p>}
                {error && <p className="text-red-600 bg-red-100 border border-red-300 p-3 rounded text-center mb-4">{error}</p>}
                {!message && ( // Hide form after success message is shown
                    <form onSubmit={handleSubmit}>
                        <InputField
                            label="Email Address"
                            id="email"
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                            placeholder="you@example.com"
                        />
                        <Button type="submit" variant="primary" fullWidth disabled={isLoading} className="mt-4">
                            {isLoading ? 'Sending...' : 'Send Reset Link'}
                        </Button>
                    </form>
                )}
                 <div className="text-center mt-6">
                    <Link to="/login" className="font-medium text-blue-600 hover:text-blue-500">
                        Back to Login
                    </Link>
                </div>
            </div>
        </div>
    );
}

export default ForgotPasswordPage; 