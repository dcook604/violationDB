import React, { useState, useEffect } from 'react';
import Button from './common/Button';
import Spinner from './common/Spinner';

// Simple email validation
const isValidEmail = (email) => /^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$/.test(email);

export default function UnitProfileForm({ initialData, onSubmit, onCancel, isSaving }) {
  const [formData, setFormData] = useState(initialData || {});
  const [errors, setErrors] = useState({});
  
  // Check if we're creating a new unit (no unit_number) or editing existing one
  const isNewUnit = !initialData?.unit_number;

  // Update form data if initialData changes (e.g., after save)
  useEffect(() => {
    setFormData(initialData || {});
  }, [initialData]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    const val = type === 'checkbox' ? checked : value;
    setFormData(prev => ({ ...prev, [name]: val }));
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: null }));
    }
    
    // If toggling off rented, clear tenant fields in state
    if (name === 'is_rented' && !checked) {
        setFormData(prev => ({
            ...prev,
            tenant_first_name: '',
            tenant_last_name: '',
            tenant_email: '',
            tenant_telephone: ''
        }));
        // Also clear any tenant errors
        setErrors(prev => ({
            ...prev,
            tenant_first_name: null,
            tenant_last_name: null,
            tenant_email: null,
            tenant_telephone: null
        }));
    }
  };

  const validate = () => {
    const newErrors = {};
    // Required fields
    if (isNewUnit && !formData.unit_number) newErrors.unit_number = 'Unit number is required.';
    if (!formData.owner_first_name) newErrors.owner_first_name = 'Owner first name is required.';
    if (!formData.owner_last_name) newErrors.owner_last_name = 'Owner last name is required.';
    if (!formData.owner_email) newErrors.owner_email = 'Owner email is required.';
    else if (!isValidEmail(formData.owner_email)) newErrors.owner_email = 'Invalid owner email format.';
    if (!formData.owner_telephone) newErrors.owner_telephone = 'Owner telephone is required.';
    
    // Conditional tenant validation
    if (formData.is_rented) {
        if (!formData.tenant_first_name) newErrors.tenant_first_name = 'Tenant first name is required when rented.';
        if (!formData.tenant_last_name) newErrors.tenant_last_name = 'Tenant last name is required when rented.';
        if (!formData.tenant_email) newErrors.tenant_email = 'Tenant email is required when rented.';
        else if (!isValidEmail(formData.tenant_email)) newErrors.tenant_email = 'Invalid tenant email format.';
        if (!formData.tenant_telephone) newErrors.tenant_telephone = 'Tenant telephone is required when rented.';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (validate()) {
      // Prepare data for submission (e.g., ensure tenant fields are null if not rented)
      const submissionData = { ...formData };
      if (!submissionData.is_rented) {
        submissionData.tenant_first_name = null;
        submissionData.tenant_last_name = null;
        submissionData.tenant_email = null;
        submissionData.tenant_telephone = null;
      }
      onSubmit(submissionData);
    }
  };

  const renderInput = (label, name, type = 'text', required = false, props = {}) => (
    <div className="mb-4">
      <label htmlFor={name} className="block text-sm font-medium text-gray-700 mb-1">
        {label}{required && <span className="text-red-500">*</span>}
      </label>
      <input
        type={type}
        id={name}
        name={name}
        value={formData[name] || ''}
        onChange={handleChange}
        className={`block w-full px-3 py-2 border rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm ${errors[name] ? 'border-red-500' : 'border-gray-300'}`}
        {...props}
      />
      {errors[name] && <p className="mt-1 text-xs text-red-600">{errors[name]}</p>}
    </div>
  );
  
   const renderTextarea = (label, name, required = false, props = {}) => (
     <div className="mb-4">
       <label htmlFor={name} className="block text-sm font-medium text-gray-700 mb-1">
         {label}{required && <span className="text-red-500">*</span>}
       </label>
       <textarea
         id={name}
         name={name}
         value={formData[name] || ''}
         onChange={handleChange}
         rows="3"
         className={`block w-full px-3 py-2 border rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm ${errors[name] ? 'border-red-500' : 'border-gray-300'}`}
         {...props}
       />
       {errors[name] && <p className="mt-1 text-xs text-red-600">{errors[name]}</p>}
     </div>
   );

  const renderCheckbox = (label, name) => (
    <div className="flex items-center mb-4">
      <input
        id={name}
        name={name}
        type="checkbox"
        checked={!!formData[name]}
        onChange={handleChange}
        className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
      />
      <label htmlFor={name} className="ml-2 block text-sm text-gray-900">
        {label}
      </label>
    </div>
  );

  return (
    <form onSubmit={handleSubmit} className="bg-white shadow-md rounded-lg p-6 space-y-6">
      
       {/* Unit & Strata Info */}
       <section>
          <h3 className="text-lg font-medium text-gray-900 mb-3">Unit Identification</h3>
           <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
               {renderInput('Unit Number', 'unit_number', 'text', true, isNewUnit ? 
                  {} : { disabled: true, className: 'bg-gray-100 cursor-not-allowed' }
               )} 
               {renderInput('Strata Lot Number', 'strata_lot_number')}
           </div>
       </section>

      {/* Owner Info */}
      <section className="border-t pt-4">
        <h3 className="text-lg font-medium text-gray-900 mb-3">Owner Information</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {renderInput('First Name', 'owner_first_name', 'text', true)}
          {renderInput('Last Name', 'owner_last_name', 'text', true)}
          {renderInput('Email', 'owner_email', 'email', true)}
          {renderInput('Telephone', 'owner_telephone', 'tel', true)}
        </div>
         {renderTextarea('Mailing Address', 'owner_mailing_address')}
      </section>

      {/* Storage & Pets */}
      <section className="border-t pt-4">
         <h3 className="text-lg font-medium text-gray-900 mb-3">Storage & Pets</h3>
         <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {renderInput('Parking Stall(s)', 'parking_stall_numbers')}
            {renderInput('Bike Storage Number(s)', 'bike_storage_numbers')}
            {renderCheckbox('Has Dog', 'has_dog')}
            {renderCheckbox('Has Cat', 'has_cat')}
         </div>
      </section>

      {/* Rental Info */}
      <section className="border-t pt-4">
        <h3 className="text-lg font-medium text-gray-900 mb-3">Rental Information</h3>
        {renderCheckbox('Unit is Rented', 'is_rented')}
        {formData.is_rented && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4 pl-4 border-l-2 border-indigo-200">
            {renderInput('Tenant First Name', 'tenant_first_name', 'text', true)}
            {renderInput('Tenant Last Name', 'tenant_last_name', 'text', true)}
            {renderInput('Tenant Email', 'tenant_email', 'email', true)}
            {renderInput('Tenant Telephone', 'tenant_telephone', 'tel', true)}
          </div>
        )}
      </section>

      {/* Actions */}
      <div className="border-t pt-5 mt-6 flex justify-end gap-3">
        <Button type="button" onClick={onCancel} color="gray" disabled={isSaving}>
          Cancel
        </Button>
        <Button type="submit" color="lightBlue" disabled={isSaving}>
          {isSaving ? <Spinner size="sm" /> : 'Save Changes'}
        </Button>
      </div>
    </form>
  );
} 