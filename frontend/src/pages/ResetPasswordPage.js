import React, { useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import API from '../utils/api';
import InputField from '../components/common/InputField';
import Button from '../components/common/Button';
import LoadingOverlay from '../components/common/LoadingOverlay'; // Assuming you have this

function ResetPasswordPage() {
    const { token } = useParams();
    const navigate = useNavigate();
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [message, setMessage] = useState('');
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (password !== confirmPassword) {
            setError('Passwords do not match.');
            return;
        }
        if (password.length < 8) { // Basic validation
             setError('Password must be at least 8 characters long.');
             return;
        }

        setIsLoading(true);
        setMessage('');
        setError('');

        try {
            const response = await API.post(`/api/auth/reset-password/${token}`, { password });
            setMessage(response.data.message + ' Redirecting to login...');
            setTimeout(() => {
                navigate('/login');
            }, 3000); // Redirect after 3 seconds
        } catch (err) {
            setError(err.response?.data?.error || 'Failed to reset password. The link might be invalid or expired.');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-100">
            <LoadingOverlay isLoading={isLoading} message="Resetting password..." />
            <div className="bg-white p-8 rounded-lg shadow-md w-full max-w-md">
                <h2 className="text-2xl font-bold mb-6 text-center text-gray-800">Reset Your Password</h2>
                {message && <p className="text-green-600 bg-green-100 border border-green-300 p-3 rounded text-center mb-4">{message}</p>}
                {error && <p className="text-red-600 bg-red-100 border border-red-300 p-3 rounded text-center mb-4">{error}</p>}

                {!message && ( // Hide form after success
                    <form onSubmit={handleSubmit}>
                        <InputField
                            label="New Password"
                            id="password"
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                            placeholder="Enter new password (min. 8 characters)"
                        />
                        <InputField
                            label="Confirm New Password"
                            id="confirmPassword"
                            type="password"
                            value={confirmPassword}
                            onChange={(e) => setConfirmPassword(e.target.value)}
                            required
                            placeholder="Confirm new password"
                            className="mt-4"
                        />
                        <Button type="submit" variant="primary" fullWidth disabled={isLoading} className="mt-6">
                            {isLoading ? 'Saving...' : 'Reset Password'}
                        </Button>
                    </form>
                )}
                 {message && ( // Show login link after success
                    <div className="text-center mt-6">
                        <Link to="/login" className="font-medium text-blue-600 hover:text-blue-500">
                            Go to Login
                        </Link>
                    </div>
                 )}
            </div>
        </div>
    );
}

export default ResetPasswordPage; 