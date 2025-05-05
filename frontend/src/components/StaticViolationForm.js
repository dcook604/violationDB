/**
 * StaticViolationForm
 *
 * A well-documented, production-ready React component for creating new violations using a static field structure.
 *
 * - All fields, validation, and dropdown options are hardcoded for maintainability and predictability.
 * - Uses existing Input, Button, and Spinner components for consistent UI/UX.
 * - Provides clear inline validation and user feedback.
 * - Designed for extensibility and ease of maintenance.
 *
 * Props:
 *   - onSubmit: function(formData) => Promise (required)
 *   - submitLabel: string (optional, default: 'Submit')
 *
 * Example usage:
 *   <StaticViolationForm onSubmit={handleSubmit} submitLabel="Create Violation" />
 */
import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import Input from './common/Input';
import Button from './common/Button';
import Spinner from './common/Spinner';
import {
  BUILDING_OPTIONS,
  VIOLATION_CATEGORY_OPTIONS,
  WHERE_DID_OPTIONS,
  SECURITY_POLICE_OPTIONS,
  FINE_LEVIED_OPTIONS,
  FILE_ACCEPT,
  MAX_FILES,
  MAX_FILE_SIZE_MB,
  isValidEmail,
  isValidPhone
} from '../utils/violationFormConfig';

// Initial state matching JotForm structure (using more readable names)
const initialFormState = {
  date_of_violation: '', // q33_dateOf
  time: '', // q35_time
  unit_no: '', // q20_unitNo
  building: '', // q34_typeA
  owner_first_name: '', // q53_ownerpropertyManager[first]
  owner_last_name: '', // q53_ownerpropertyManager[last]
  owner_email: '', // q54_ownerpropertyManager54
  owner_telephone: '', // q55_ownerpropertyManager55
  tenant_first_name: '', // q56_tenantName[first]
  tenant_last_name: '', // q56_tenantName[last]
  tenant_email: '', // q57_tenantEmail
  tenant_phone: '', // q59_tenantPhone
  violation_category: '', // q51_violationCategory
  concierge_shift: '', // q38_conciergeShift
  noticed_by: '', // q39_noticedBy
  people_called: '', // q42_peopleCalled
  actioned_by: '', // q43_actionedBy
  people_involved: '', // q41_peopleInvolved
  where_did: '', // q48_whereDid
  was_security_or_police_called: '', // q49_whereDid49
  police_report_no: '', // q50_policeReport
  fine_levied: '', // q47_fineLevied
  incident_details: '', // q44_incidentDetails
  action_taken: '', // q46_actionTaken
  attach_evidence: [], // q52_attachEvidence
  status: 'Open', // Default, not a direct JotForm field but needed by backend
};

export default function StaticViolationForm({ onSubmit, submitLabel = 'Submit' }) {
  const [form, setForm] = useState(initialFormState);
  const [errors, setErrors] = useState({});
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState('');
  const formRef = useRef(null);
  const navigate = useNavigate();

  // Simple combined handler for most inputs
  const handleChange = (e) => {
    const { name, value, type, files } = e.target;
    if (type === 'file') {
      handleFileChange(e);
    } else {
      setForm(prev => ({ ...prev, [name]: value }));
      // Clear validation error on change
      if (errors[name]) {
        setErrors(prev => ({ ...prev, [name]: null }));
      }
    }
  };

  const handleFileChange = (e) => {
    const files = Array.from(e.target.files);
    let fileError = null;

    if (files.length > MAX_FILES) {
      fileError = `Max ${MAX_FILES} files allowed.`;
    } else {
      for (const file of files) {
        if (file.size > MAX_FILE_SIZE_MB * 1024 * 1024) {
          fileError = `Each file must be <= ${MAX_FILE_SIZE_MB}MB.`;
          break;
        }
      }
    }

    setErrors(prev => ({ ...prev, attach_evidence: fileError }));
    if (!fileError) {
      setForm(prev => ({ ...prev, attach_evidence: files }));
    } else {
       setForm(prev => ({ ...prev, attach_evidence: [] })); // Clear files if validation fails
       e.target.value = null; // Reset the file input visually
    }
  };

  // Validation based on JotForm required fields
  const validate = () => {
    const errs = {};
    const f = form;

    if (!f.date_of_violation) errs.date_of_violation = 'Date is required.';
    if (!f.time) errs.time = 'Time is required.';
    if (!f.unit_no) errs.unit_no = 'Unit No. is required.';
    if (!f.building) errs.building = 'Building is required.';
    if (!f.owner_first_name) errs.owner_first_name = 'First name required.';
    if (!f.owner_last_name) errs.owner_last_name = 'Last name required.';
    if (!f.owner_email) errs.owner_email = 'Email is required.';
    else if (!isValidEmail(f.owner_email)) errs.owner_email = 'Invalid email.';
    if (!f.owner_telephone) errs.owner_telephone = 'Telephone is required.';
    else if (!isValidPhone(f.owner_telephone)) errs.owner_telephone = 'Format: (000) 000-0000 or 000-000-0000';
    if (!f.violation_category) errs.violation_category = 'Category is required.';
    if (!f.where_did) errs.where_did = 'Location is required.';
    if (!f.was_security_or_police_called) errs.was_security_or_police_called = 'This field is required.';
    if (!f.fine_levied) errs.fine_levied = 'Fine Levied is required.';
    if (!f.incident_details) errs.incident_details = 'Incident Details are required.';
    if (!f.action_taken) errs.action_taken = 'Action Taken is required.';

    // Optional fields format validation
    if (f.tenant_email && !isValidEmail(f.tenant_email)) errs.tenant_email = 'Invalid email.';
    if (f.tenant_phone && !isValidPhone(f.tenant_phone)) errs.tenant_phone = 'Format: (000) 000-0000 or 000-000-0000';

    // File validation handled in handleFileChange, just check if an error exists
    if (errors.attach_evidence) errs.attach_evidence = errors.attach_evidence;

    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitError('');
    if (!validate()) {
      // Find first error and scroll to it
      const firstErrorKey = Object.keys(errors).find(key => errors[key]);
       if (firstErrorKey) {
           // Attempt to find by name, then maybe by label text if name fails
           let el = formRef.current.querySelector(`[name='${firstErrorKey}']`);
           if (!el && firstErrorKey === 'owner_first_name') el = formRef.current.querySelector(`[name='owner_first_name']`); // Adjust for specific names if needed
           // Add similar checks for other composite names if needed
           if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
       }
      return;
    }
    setSubmitting(true);
    try {
       // Map state to the expected backend structure if different
       const payload = {
           ...form,
           // Combine name fields if backend expects structure like { first: '...', last: '...' }
           owner_property_manager_name: {
               first: form.owner_first_name,
               last: form.owner_last_name
           },
           tenant_name: {
               first: form.tenant_first_name,
               last: form.tenant_last_name
           },
           owner_property_manager_email: form.owner_email,
           owner_property_manager_telephone: form.owner_telephone,
           // Remove individual name fields if combined above
           owner_first_name: undefined,
           owner_last_name: undefined,
           tenant_first_name: undefined,
           tenant_last_name: undefined,
           // Ensure attach_evidence is handled correctly (passed as array of files)
           attach_evidence: form.attach_evidence.length > 0 ? form.attach_evidence : []
       };
       // Remove undefined keys before submitting
       Object.keys(payload).forEach(key => payload[key] === undefined && delete payload[key]);

      await onSubmit(payload);
      // Optionally reset form on success: setForm(initialFormState);
    } catch (err) {
      setSubmitError(err.message || 'Failed to submit form');
    }
    setSubmitting(false);
  };

  // Helper to render standard form field group
  const renderFormGroup = (label, name, isRequired, children, error) => (
    <div className="mb-4">
      <label className="block font-semibold mb-1" htmlFor={name}>
        {label}{isRequired && <span className="text-red-500 ml-1">*</span>}
      </label>
      {children}
      {error && <div className="text-red-500 text-xs mt-1">{error}</div>}
    </div>
  );

  // Helper to render select dropdown
  const renderSelect = (label, name, options, isRequired, error) => (
     renderFormGroup(label, name, isRequired, (
       <select
         id={name}
         name={name}
         value={form[name]}
         onChange={handleChange}
         className={`border p-2 rounded w-full ${error ? 'border-red-500' : 'border-gray-300'}`}
         required={isRequired}
       >
         <option value="">Please Select</option>
         {options.map(opt => (
           <option key={opt} value={opt}>{opt}</option>
         ))}
       </select>
     ), error)
   );

   // Helper to render textarea
   const renderTextarea = (label, name, isRequired, subLabel, error, props = {}) => (
     renderFormGroup(label, name, isRequired, (
       <>
         <textarea
           id={name}
           name={name}
           value={form[name]}
           onChange={handleChange}
           className={`border p-2 rounded w-full ${error ? 'border-red-500' : 'border-gray-300'}`}
           required={isRequired}
           rows="4" // Default rows
           {...props}
         />
         {subLabel && <label className="form-sub-label text-xs text-gray-500 mt-1">{subLabel}</label>}
       </>
     ), error)
   );


  return (
    <div className="relative flex flex-col min-w-0 break-words w-full mb-6 shadow-lg rounded-lg bg-white border-0">
      <div className="flex-auto px-4 lg:px-10 py-10">
        {/* Form Title (from JotForm) */}
        <div className="mb-6 text-left"> {/* Adjusted alignment */}
          <h1 className="text-2xl font-bold text-gray-700">Create New Violation</h1>
        </div>

        <form ref={formRef} onSubmit={handleSubmit} noValidate>

          {/* --- Row 1: Date & Time --- */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
             {renderFormGroup('Date of Violation', 'date_of_violation', true,
               <input type="date" id="date_of_violation" name="date_of_violation" value={form.date_of_violation} onChange={handleChange} className={`border p-2 rounded w-full ${errors.date_of_violation ? 'border-red-500' : 'border-gray-300'}`} required placeholder="MM-DD-YYYY" />,
               errors.date_of_violation
             )}
             {renderFormGroup('Time', 'time', true,
               <input type="time" id="time" name="time" value={form.time} onChange={handleChange} className={`border p-2 rounded w-full ${errors.time ? 'border-red-500' : 'border-gray-300'}`} required placeholder="HH:MM" />,
               errors.time
             )}
          </div>

          {/* --- Row 2: Unit & Building --- */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
             {renderFormGroup('Unit No.', 'unit_no', true,
               <input type="number" id="unit_no" name="unit_no" value={form.unit_no} onChange={handleChange} className={`border p-2 rounded w-full ${errors.unit_no ? 'border-red-500' : 'border-gray-300'}`} required placeholder="ex: 23" />,
               errors.unit_no
             )}
             {renderSelect('Building', 'building', BUILDING_OPTIONS, true, errors.building)}
          </div>

          {/* --- Owner/Property Manager --- */}
          <hr className="my-6 border-t border-gray-300" />
          <h6 className="text-gray-500 text-sm mb-4 font-bold uppercase">Owner / Property Manager Information</h6>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
             {renderFormGroup('First Name', 'owner_first_name', true,
               <input type="text" id="owner_first_name" name="owner_first_name" value={form.owner_first_name} onChange={handleChange} className={`border p-2 rounded w-full ${errors.owner_first_name ? 'border-red-500' : 'border-gray-300'}`} required />,
               errors.owner_first_name
             )}
             {renderFormGroup('Last Name', 'owner_last_name', true,
               <input type="text" id="owner_last_name" name="owner_last_name" value={form.owner_last_name} onChange={handleChange} className={`border p-2 rounded w-full ${errors.owner_last_name ? 'border-red-500' : 'border-gray-300'}`} required />,
               errors.owner_last_name
             )}
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            {renderFormGroup('Email', 'owner_email', true,
               <input type="email" id="owner_email" name="owner_email" value={form.owner_email} onChange={handleChange} className={`border p-2 rounded w-full ${errors.owner_email ? 'border-red-500' : 'border-gray-300'}`} required placeholder="example@example.com" />,
               errors.owner_email
            )}
            {renderFormGroup('Telephone', 'owner_telephone', true,
               <input type="tel" id="owner_telephone" name="owner_telephone" value={form.owner_telephone} onChange={handleChange} className={`border p-2 rounded w-full ${errors.owner_telephone ? 'border-red-500' : 'border-gray-300'}`} required placeholder="(000) 000-0000" />,
               errors.owner_telephone
            )}
          </div>

          {/* --- Tenant (Optional) --- */}
          <hr className="my-6 border-t border-gray-300" />
          <h6 className="text-gray-500 text-sm mb-4 font-bold uppercase">Tenant Information (Optional)</h6>
           <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
             {renderFormGroup('First Name', 'tenant_first_name', false,
               <input type="text" id="tenant_first_name" name="tenant_first_name" value={form.tenant_first_name} onChange={handleChange} className={`border p-2 rounded w-full ${errors.tenant_first_name ? 'border-red-500' : 'border-gray-300'}`} />,
               errors.tenant_first_name
             )}
             {renderFormGroup('Last Name', 'tenant_last_name', false,
               <input type="text" id="tenant_last_name" name="tenant_last_name" value={form.tenant_last_name} onChange={handleChange} className={`border p-2 rounded w-full ${errors.tenant_last_name ? 'border-red-500' : 'border-gray-300'}`} />,
               errors.tenant_last_name
             )}
           </div>
           <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
             {renderFormGroup('Email', 'tenant_email', false,
                <input type="email" id="tenant_email" name="tenant_email" value={form.tenant_email} onChange={handleChange} className={`border p-2 rounded w-full ${errors.tenant_email ? 'border-red-500' : 'border-gray-300'}`} placeholder="example@example.com" />,
                errors.tenant_email
             )}
             {renderFormGroup('Phone', 'tenant_phone', false,
                <input type="tel" id="tenant_phone" name="tenant_phone" value={form.tenant_phone} onChange={handleChange} className={`border p-2 rounded w-full ${errors.tenant_phone ? 'border-red-500' : 'border-gray-300'}`} placeholder="(000) 000-0000" />,
                errors.tenant_phone
             )}
           </div>

          {/* --- Violation Category --- */}
           <hr className="my-6 border-t border-gray-300" />
           {renderSelect('Violation Category', 'violation_category', VIOLATION_CATEGORY_OPTIONS, true, errors.violation_category)}

          {/* --- Other Details --- */}
          <hr className="my-6 border-t border-gray-300" />
           <h6 className="text-gray-500 text-sm mb-4 font-bold uppercase">Other Details</h6>
           <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
             {renderFormGroup('Concierge Shift', 'concierge_shift', false,
                <input type="text" id="concierge_shift" name="concierge_shift" value={form.concierge_shift} onChange={handleChange} className={`border p-2 rounded w-full ${errors.concierge_shift ? 'border-red-500' : 'border-gray-300'}`} />,
                errors.concierge_shift
             )}
             {renderFormGroup('Noticed By', 'noticed_by', false,
                 <input type="text" id="noticed_by" name="noticed_by" value={form.noticed_by} onChange={handleChange} className={`border p-2 rounded w-full ${errors.noticed_by ? 'border-red-500' : 'border-gray-300'}`} />,
                 errors.noticed_by
             )}
           </div>
           <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
             {renderFormGroup('People Called', 'people_called', false,
                 <input type="text" id="people_called" name="people_called" value={form.people_called} onChange={handleChange} className={`border p-2 rounded w-full ${errors.people_called ? 'border-red-500' : 'border-gray-300'}`} />,
                 errors.people_called
             )}
             {renderFormGroup('Actioned By', 'actioned_by', false,
                 <input type="text" id="actioned_by" name="actioned_by" value={form.actioned_by} onChange={handleChange} className={`border p-2 rounded w-full ${errors.actioned_by ? 'border-red-500' : 'border-gray-300'}`} />,
                 errors.actioned_by
             )}
           </div>
           {renderTextarea('People Involved', 'people_involved', false, null, errors.people_involved, {rows: 4})}

          {/* --- More Violation Details --- */}
          <hr className="my-6 border-t border-gray-300" />
           <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              {renderSelect('Where did this violation happen?', 'where_did', WHERE_DID_OPTIONS, true, errors.where_did)}
              {renderSelect('Was Security or Police called?', 'was_security_or_police_called', SECURITY_POLICE_OPTIONS, true, errors.was_security_or_police_called)}
              {renderFormGroup('Police Report No.', 'police_report_no', false,
                  <input type="text" id="police_report_no" name="police_report_no" value={form.police_report_no} onChange={handleChange} className={`border p-2 rounded w-full ${errors.police_report_no ? 'border-red-500' : 'border-gray-300'}`} />,
                  errors.police_report_no
              )}
              {renderSelect('Fine Levied', 'fine_levied', FINE_LEVIED_OPTIONS, true, errors.fine_levied)}
           </div>

          {/* --- Narrative & Action --- */}
           <hr className="my-6 border-t border-gray-300" />
           {renderTextarea('Incident Details', 'incident_details', true, null, errors.incident_details, {rows: 6})}
           {renderTextarea('Action Taken', 'action_taken', true, null, errors.action_taken, {rows: 6})}

          {/* --- Attach Evidence --- */}
           <hr className="my-6 border-t border-gray-300" />
           {renderFormGroup('Attach Evidence', 'attach_evidence', false,
             <>
               <input
                 type="file"
                 id="attach_evidence"
                 name="attach_evidence"
                 multiple
                 accept={FILE_ACCEPT}
                 onChange={handleFileChange} // Use the dedicated file handler
                 className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
               />
               <div className="text-xs text-gray-500 mt-1">
                 Max {MAX_FILES} files, each ≤ {MAX_FILE_SIZE_MB}MB.
               </div>
               {form.attach_evidence && form.attach_evidence.length > 0 && (
                 <ul className="mt-2 text-xs text-gray-700 list-disc list-inside">
                   {Array.from(form.attach_evidence).map((file, idx) => (
                     <li key={idx}>{file.name} ({(file.size / 1024 / 1024).toFixed(2)} MB)</li>
                   ))}
                 </ul>
               )}
             </>,
             errors.attach_evidence // Display file-specific errors here
           )}

          {/* --- Submission --- */}
           <hr className="my-6 border-t border-gray-300" />
           <div className="text-center mt-6 flex justify-center items-center gap-4">
              {submitError && <p className="text-red-500 text-sm mb-4">{submitError}</p>}
             <Button
               type="submit"
               color="lightBlue" // Match theme or use specific JotForm style if needed
               disabled={submitting}
               className="bg-[#18BD5B] hover:bg-[#16AA52]" // Example: Match JotForm green button
             >
               {submitting ? <Spinner size="sm" /> : submitLabel}
             </Button>
             <Button
               type="button"
               onClick={() => navigate('/dashboard')} // Navigate back to dashboard
               color="red" // Use a red color utility or class
               className="bg-red-500 hover:bg-red-600 text-white"
             >
               Cancel
             </Button>
           </div>
        </form>
      </div>
    </div>
  );
} 