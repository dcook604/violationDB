import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import API from '../api';
import UnitList from '../components/units/UnitList'; // Component to display the list
import Spinner from '../components/common/Spinner';
import Button from '../components/common/Button';
import { useAuth } from '../context/AuthContext'; // Corrected path
import { obfuscateRoute } from '../utils/routeMapper'; // Import for route mapping

export default function UnitListPage() {
  const [units, setUnits] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const { user } = useAuth(); // Get current user info

  useEffect(() => {
    const fetchUnits = async () => {
      setLoading(true);
      setError('');
      try {
        console.log('Fetching units from API...');
        const response = await API.get('/api/units');
        console.log('Units API response:', response);
        setUnits(response.data || []);
      } catch (err) {
        console.error('Error fetching units:', err);
        const errorMessage = err.response?.data?.error || err.message || 'An unexpected error occurred';
        const detailedMessage = err.response?.data?.message ? ` - ${err.response.data.message}` : '';
        setError(`Failed to load unit list. ${errorMessage}${detailedMessage}`);
        setUnits([]); // Clear units on error
      }
      setLoading(false);
    };

    fetchUnits();
  }, []);

  return (
    <div className="p-4 md:p-8">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800">Unit Profiles</h2>
        {user?.role === 'admin' && (
          <Link to="/r/b4d6e8f2a1c3/new"> {/* Using the obfuscated units path with /new */}
            <Button color="lightBlue">
               <i className="fas fa-plus mr-2"></i> Create New Unit
            </Button>
          </Link>
        )}
      </div>

      {loading ? (
        <div className="text-center py-10">
          <Spinner /> Loading units...
        </div>
      ) : error ? (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
          <strong className="font-bold">Error:</strong>
          <span className="block sm:inline"> {error}</span>
        </div>
      ) : (
        <UnitList units={units} />
      )}
    </div>
  );
} 