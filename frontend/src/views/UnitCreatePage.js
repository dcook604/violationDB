import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import UnitProfileForm from '../components/UnitProfileForm';
import API from '../api';
import LoadingOverlay from '../components/common/LoadingOverlay';

export default function UnitCreatePage() {
  const navigate = useNavigate();
  const [isSaving, setIsSaving] = useState(false);
  const [saveMessage, setSaveMessage] = useState('Creating unit...');

  // Initial empty form data
  const initialData = {
    unit_number: '',
    strata_lot_number: '',
    owner_first_name: '',
    owner_last_name: '',
    owner_email: '',
    owner_telephone: '',
    owner_mailing_address: '',
    parking_stall_numbers: '',
    bike_storage_numbers: '',
    has_dog: false,
    has_cat: false,
    is_rented: false,
    tenant_first_name: '',
    tenant_last_name: '',
    tenant_email: '',
    tenant_telephone: ''
  };

  const handleSubmit = async (formData) => {
    setIsSaving(true);
    setSaveMessage('Creating new unit profile...');
    
    try {
      // Send creation request to API
      const response = await API.post('/api/units', formData);
      
      // On success, navigate to the new unit's detail page
      setIsSaving(false);
      
      if (response.data && response.data.unit_number) {
        navigate(`/r/b4d6e8f2a1c3/${response.data.unit_number}`);
      } else {
        // Fallback if unit_number is not returned
        navigate('/r/b4d6e8f2a1c3');
      }
    } catch (error) {
      setIsSaving(false);
      console.error('Error creating unit:', error);
      const errorMessage = error.response?.data?.error || error.message || 'An unexpected error occurred';
      alert(`Failed to create unit profile: ${errorMessage}`);
    }
  };

  const handleCancel = () => {
    navigate('/r/b4d6e8f2a1c3');
  };

  return (
    <div className="p-4 md:p-8">
      <LoadingOverlay isLoading={isSaving} message={saveMessage} />
      
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-800">Create New Unit Profile</h2>
        <p className="text-gray-600">Enter the details for the new unit profile.</p>
      </div>
      
      <UnitProfileForm
        initialData={initialData}
        onSubmit={handleSubmit}
        onCancel={handleCancel}
        isSaving={isSaving}
      />
    </div>
  );
} 