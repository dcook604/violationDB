import React, { useState, useEffect, useCallback } from 'react';
import API from '../api';
import { useParams, Link } from 'react-router-dom';
import UnitProfileDisplay from '../components/UnitProfileDisplay';
import UnitProfileForm from '../components/UnitProfileForm';
import Spinner from '../components/common/Spinner';
import Button from '../components/common/Button';
import { useAuth } from '../context/AuthContext';

export default function UnitProfileDetailPage() {
  const { unitNumber } = useParams();
  const { user } = useAuth(); // Get user for permission checks
  const [unitData, setUnitData] = useState(null);
  const [violationSummary, setViolationSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const [unitRes, summaryRes] = await Promise.all([
        API.get(`/api/units/${unitNumber}`),
        API.get(`/api/units/${unitNumber}/violation_summary`)
      ]);
      setUnitData(unitRes.data);
      setViolationSummary(summaryRes.data);
    } catch (err) {
      setError('Failed to load unit profile data. ' + (err.response?.data?.error || err.message));
    }
    setLoading(false);
  }, [unitNumber]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleSave = async (formData) => {
    setIsSaving(true);
    setError('');
    try {
      const response = await API.put(`/api/units/${unitNumber}`, formData);
      setUnitData(response.data); // Update local state with saved data
      setIsEditing(false);
      // Potentially refetch violation summary if needed, though unlikely to change on profile update
      // fetchData(); 
    } catch (err) {
      setError('Failed to save unit profile. ' + (err.response?.data?.error || err.message));
      // Keep editing mode open on error
    }
    setIsSaving(false);
  };

  const handleCancel = () => {
    setIsEditing(false);
    setError(''); // Clear any previous save errors
    // No need to refetch, just toggle the view
  };

  // Determine if the current user can edit (e.g., is admin)
  const canEdit = user?.role === 'admin';

  if (loading) return <div className="p-4 text-center"><Spinner /> Loading unit profile...</div>;
  
  // Separate error display for better layout
  if (error && !unitData) return (
     <div className="p-4 md:p-8">
        <Link to="/units" className="text-blue-600 hover:underline text-sm mb-4 inline-block"> &larr; Back to Unit List</Link>
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
          <strong className="font-bold">Error:</strong>
          <span className="block sm:inline"> {error}</span>
        </div>
      </div>
  );

  if (!unitData) return <div className="p-4 text-center">Unit profile not found.</div>;

  return (
    <div className="p-4 md:p-8">
       <div className="flex justify-between items-center mb-6">
           <div>
             <Link to="/units" className="text-blue-600 hover:underline text-sm mb-1 inline-block"> &larr; Back to Unit List</Link>
             <h2 className="text-2xl font-bold text-gray-800">Unit Profile: {unitNumber}</h2>
           </div>
            {/* Show Edit button only when not editing and user has permission */}
            {!isEditing && canEdit && (
                <Button color="lightBlue" onClick={() => setIsEditing(true)}>
                    <i className="fas fa-pencil-alt mr-2"></i> Edit Unit
                </Button>
            )}
       </div>
        
        {/* Display error during editing if save fails */} 
        {error && isEditing && (
           <div className="mb-4 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
             <strong className="font-bold">Save Error:</strong>
             <span className="block sm:inline"> {error}</span>
           </div>
        )}

        {isEditing ? (
            <UnitProfileForm 
                initialData={unitData} 
                onSubmit={handleSave} 
                onCancel={handleCancel} 
                isSaving={isSaving} 
            />
        ) : (
            <UnitProfileDisplay 
                unitData={unitData} 
                violationSummary={violationSummary} 
            />
        )}
    </div>
  );
} 