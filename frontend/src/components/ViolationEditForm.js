import React from 'react';
import Input from './common/Input';

export default function ViolationEditForm({ form, setForm, saving, handleSave, handleCancel, errors }) {
  const handleChange = (e) => {
    const { name, value } = e.target;
    if (name.startsWith('dynamic_')) {
      setForm(f => ({ ...f, dynamic_fields: { ...f.dynamic_fields, [name.replace('dynamic_', '')]: value } }));
    } else {
      setForm(f => ({ ...f, [name]: value }));
    }
  };

  return (
    <div className="p-8 max-w-xl mx-auto">
      <h2 className="text-2xl font-bold mb-4">Edit Violation</h2>
      <div className="bg-white shadow rounded-lg p-6">
        <div className="mb-4">
          <label className="font-semibold">Reference:</label>
          <span className="ml-2">{form.reference}</span>
        </div>
        <div className="mt-3 p-3 bg-gray-100 rounded-md">
          <div className="mb-3">
            <label className="font-semibold">Category:</label>
            <Input 
              name="dynamic_Category" 
              value={form.dynamic_fields?.Category || ''} 
              onChange={handleChange} 
              className="border p-1 ml-2 w-full mt-1" 
            />
          </div>
          <div className="mb-2">
            <label className="font-semibold">Details:</label>
            <textarea
              name="dynamic_Incident Details"
              value={form.dynamic_fields?.['Incident Details'] || ''}
              onChange={handleChange}
              className="border p-1 ml-2 w-full mt-1 h-24"
            />
          </div>
        </div>
        <div className="mt-4">
          <div className="font-semibold mb-2">Additional Information:</div>
          <ul className="list-disc list-inside">
            {Object.entries(form.dynamic_fields || {}).map(([key, value]) => {
              if (key === 'Category' || key === 'Incident Details') return null;
              return (
                <li key={key} className="mb-1">
                  <label className="font-semibold mr-2">{key}:</label>
                  <Input
                    name={`dynamic_${key}`}
                    value={value}
                    onChange={handleChange}
                    className="border p-1 ml-2 w-64"
                  />
                </li>
              );
            })}
          </ul>
        </div>
        <div className="flex gap-2 mt-6">
          <button onClick={handleSave} className="bg-blue-600 text-white px-4 py-2 rounded" disabled={saving}>
            {saving ? 'Saving...' : 'Save'}
          </button>
          <button onClick={handleCancel} className="bg-gray-300 px-4 py-2 rounded" disabled={saving}>
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
} 