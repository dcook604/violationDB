import { useState, useEffect } from 'react';
import API from '../api';

export default function useViolationDetail(id, user) {
  const [violation, setViolation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [editing, setEditing] = useState(false);
  const [form, setForm] = useState(null);
  const [saving, setSaving] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [fields, setFields] = useState([]);
  const [replies, setReplies] = useState([]);
  const [loadingReplies, setLoadingReplies] = useState(false);

  useEffect(() => {
    API.get(`/api/violations/${id}`)
      .then(res => {
        setViolation(res.data);
        setForm({
          ...res.data,
          dynamic_fields: { ...res.data.dynamic_fields }
        });
        setLoading(false);
        fetchReplies();
      })
      .catch(err => {
        if (err.response && err.response.status === 403) {
          setError('You do not have permission to view this violation.');
        } else {
          setError('Failed to load violation details.');
        }
        setLoading(false);
      });
    // eslint-disable-next-line
  }, [id]);

  const fetchReplies = () => {
    setLoadingReplies(true);
    API.get(`/api/violations/${id}/replies`)
      .then(res => {
        setReplies(res.data);
        setLoadingReplies(false);
      })
      .catch(() => {
        setLoadingReplies(false);
      });
  };

  const canEditOrDelete = violation && user && (user.role === 'admin' || user.email === violation.created_by || user.id === violation.created_by);

  return {
    violation,
    loading,
    error,
    editing,
    setEditing,
    form,
    setForm,
    saving,
    setSaving,
    deleting,
    setDeleting,
    fields,
    setFields,
    replies,
    loadingReplies,
    fetchReplies,
    canEditOrDelete
  };
} 