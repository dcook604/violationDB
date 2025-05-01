import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import API from '../api';
import { useAuth } from '../context/AuthContext';
import Button from './common/Button';
import Input from './common/Input';

export default function ViolationDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [violation, setViolation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [editing, setEditing] = useState(false);
  const [form, setForm] = useState(null);
  const [saving, setSaving] = useState(false);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    API.get(`/api/violations/${id}`)
      .then(res => {
        setViolation(res.data);
        setForm({
          ...res.data,
          dynamic_fields: { ...res.data.dynamic_fields }
        });
        setLoading(false);
      })
      .catch(err => {
        if (err.response && err.response.status === 403) {
          setError('You do not have permission to view this violation.');
        } else {
          setError('Failed to load violation details.');
        }
        setLoading(false);
      });
  }, [id]);

  const canEditOrDelete = violation && user && (user.role === 'admin' || user.email === violation.created_by || user.id === violation.created_by);

  const handleEdit = () => setEditing(true);
  const handleCancel = () => setEditing(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    if (name.startsWith('dynamic_')) {
      setForm(f => ({ ...f, dynamic_fields: { ...f.dynamic_fields, [name.replace('dynamic_', '')]: value } }));
    } else {
      setForm(f => ({ ...f, [name]: value }));
    }
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      await API.put(`/api/violations/${id}`, {
        ...form,
        dynamic_fields: form.dynamic_fields
      });
      setEditing(false);
      // Refresh
      const res = await API.get(`/api/violations/${id}`);
      setViolation(res.data);
      setForm({ ...res.data, dynamic_fields: { ...res.data.dynamic_fields } });
    } catch (err) {
      setError('Failed to save changes.');
    }
    setSaving(false);
  };

  const handleDelete = async () => {
    if (!window.confirm('Are you sure you want to delete this violation?')) return;
    setDeleting(true);
    try {
      await API.delete(`/api/violations/${id}`);
      navigate('/violations');
    } catch (err) {
      setError('Failed to delete violation.');
    }
    setDeleting(false);
  };

  if (loading) return <div className="p-8">Loading...</div>;
  if (error) return <div className="p-8 text-red-600">{error}</div>;
  if (!violation) return <div className="p-8">Violation not found.</div>;

  if (editing && form) {
    return (
      <div className="p-8 max-w-xl mx-auto">
        <h2 className="text-2xl font-bold mb-4">Edit Violation</h2>
        <div className="bg-white shadow rounded-lg p-6">
          <div className="mb-2">
            <label className="font-semibold">Category:</label>
            <Input name="category" value={form.category || ''} onChange={handleChange} className="border p-1 ml-2" />
          </div>
          <div className="mb-2">
            <label className="font-semibold">Building:</label>
            <Input name="building" value={form.building || ''} onChange={handleChange} className="border p-1 ml-2" />
          </div>
          <div className="mb-2">
            <label className="font-semibold">Unit Number:</label>
            <Input name="unit_number" value={form.unit_number || ''} onChange={handleChange} className="border p-1 ml-2" />
          </div>
          <div className="mb-2">
            <label className="font-semibold">Incident Date:</label>
            <Input name="incident_date" type="date" value={form.incident_date ? form.incident_date.substring(0,10) : ''} onChange={handleChange} className="border p-1 ml-2" />
          </div>
          <div className="mb-2">
            <label className="font-semibold">Subject:</label>
            <Input name="subject" value={form.subject || ''} onChange={handleChange} className="border p-1 ml-2" />
          </div>
          <div className="mb-2">
            <label className="font-semibold">Details:</label>
            <textarea name="details" value={form.details || ''} onChange={handleChange} className="border p-1 ml-2 w-full" />
          </div>
          <div className="mt-4">
            <div className="font-semibold mb-2">Dynamic Fields:</div>
            <ul className="list-disc list-inside">
              {Object.entries(form.dynamic_fields || {}).map(([key, value]) => (
                <li key={key} className="mb-1">
                  <span className="font-medium">{key}:</span>
                  <Input name={`dynamic_${key}`} value={value || ''} onChange={handleChange} className="border p-1 ml-2" />
                </li>
              ))}
            </ul>
          </div>
          <div className="mt-4 flex gap-2">
            <Button onClick={handleSave} disabled={saving} className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">Save</Button>
            <Button onClick={handleCancel} className="bg-gray-300 px-4 py-2 rounded hover:bg-gray-400">Cancel</Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8 max-w-xl mx-auto">
      <h2 className="text-2xl font-bold mb-4">Violation Details</h2>
      <div className="bg-white shadow rounded-lg p-6">
        <div className="mb-2"><span className="font-semibold">Reference:</span> {violation.reference}</div>
        <div className="mb-2"><span className="font-semibold">Category:</span> {violation.category}</div>
        <div className="mb-2"><span className="font-semibold">Building:</span> {violation.building}</div>
        <div className="mb-2"><span className="font-semibold">Unit Number:</span> {violation.unit_number}</div>
        <div className="mb-2"><span className="font-semibold">Incident Date:</span> {violation.incident_date ? new Date(violation.incident_date).toLocaleDateString() : ''}</div>
        <div className="mb-2"><span className="font-semibold">Subject:</span> {violation.subject}</div>
        <div className="mb-2"><span className="font-semibold">Details:</span> {violation.details}</div>
        <div className="mb-2"><span className="font-semibold">Created At:</span> {violation.created_at ? new Date(violation.created_at).toLocaleString() : ''}</div>
        <div className="mb-2"><span className="font-semibold">Created By:</span> {violation.created_by}</div>
        <div className="mt-4">
          <div className="font-semibold mb-2">Dynamic Fields:</div>
          <ul className="list-disc list-inside">
            {Object.entries(violation.dynamic_fields || {}).map(([key, value]) => (
              <li key={key}><span className="font-medium">{key}:</span> {value}</li>
            ))}
          </ul>
        </div>
        {canEditOrDelete && (
          <div className="mt-4 flex gap-2">
            <Button onClick={handleEdit} className="bg-yellow-500 text-white px-4 py-2 rounded hover:bg-yellow-600">Edit</Button>
            <Button onClick={handleDelete} disabled={deleting} className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700">Delete</Button>
          </div>
        )}
      </div>
    </div>
  );
} 