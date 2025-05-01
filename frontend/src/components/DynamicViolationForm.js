import React, { useEffect, useState } from 'react';
import API from '../api';
import Button from './common/Button';
import Input from './common/Input';

function DynamicViolationForm({ onSubmit, initialValues = {}, submitLabel = 'Submit' }) {
  const [fields, setFields] = useState([]);
  const [values, setValues] = useState(initialValues);
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchFields = async () => {
      setLoading(true);
      try {
        const res = await API.get('/api/fields');
        setFields(res.data);
        // Set initial values for new fields if not present
        const newVals = { ...initialValues };
        res.data.forEach(f => {
          if (!(f.name in newVals)) newVals[f.name] = '';
        });
        setValues(newVals);
      } catch (err) {
        setErrors({ global: 'Failed to load fields' });
      }
      setLoading(false);
    };
    fetchFields();
  }, [initialValues]);

  const handleChange = e => {
    const { name, value, type, checked } = e.target;
    setValues(v => ({ ...v, [name]: type === 'checkbox' ? checked : value }));
  };

  const validate = () => {
    const errs = {};
    fields.forEach(f => {
      if (f.required && !values[f.name]) {
        errs[f.name] = `${f.label} is required.`;
      }
      // Add more type/validation logic as needed
    });
    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleSubmit = e => {
    e.preventDefault();
    if (!validate()) return;
    onSubmit(values);
  };

  if (loading) return <div>Loading fields...</div>;

  return (
    <form onSubmit={handleSubmit}>
      {fields.map(field => (
        <div key={field.id} className="mb-3">
          <label className="block font-semibold mb-1">{field.label}{field.required && ' *'}</label>
          {field.type === 'text' && (
            <Input name={field.name} value={values[field.name] || ''} onChange={handleChange} />
          )}
          {field.type === 'number' && (
            <Input type="number" name={field.name} value={values[field.name] || ''} onChange={handleChange} />
          )}
          {field.type === 'date' && (
            <Input type="date" name={field.name} value={values[field.name] || ''} onChange={handleChange} />
          )}
          {field.type === 'select' && (
            <select className="border p-2 rounded w-full focus:outline-none focus:ring-2 focus:ring-blue-500" name={field.name} value={values[field.name] || ''} onChange={handleChange}>
              <option value="">Select...</option>
              {(field.options ? field.options.split(',') : []).map(opt => (
                <option key={opt.trim()} value={opt.trim()}>{opt.trim()}</option>
              ))}
            </select>
          )}
          {errors[field.name] && <div className="text-red-600 text-sm mt-1">{errors[field.name]}</div>}
        </div>
      ))}
      {errors.global && <div className="text-red-600 text-sm mb-2">{errors.global}</div>}
      <Button type="submit" className="bg-blue-600 text-white hover:bg-blue-700">{submitLabel}</Button>
    </form>
  );
}

export default DynamicViolationForm; 