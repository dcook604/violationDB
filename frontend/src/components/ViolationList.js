import React, { useEffect, useState } from 'react';
import API from '../api';

export default function ViolationList() {
  const [violations, setViolations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    API.get('/api/violations')
      .then(res => {
        setViolations(res.data);
        setLoading(false);
      })
      .catch(err => {
        setError('Failed to load violations');
        setLoading(false);
      });
  }, []);

  if (loading) return <div className="p-8">Loading...</div>;
  if (error) return <div className="p-8 text-red-600">{error}</div>;
  if (!violations.length) return <div className="p-8">No violations found.</div>;

  // Collect all dynamic field names for table headers
  const dynamicFieldNames = Array.from(
    new Set(
      violations.flatMap(v => Object.keys(v.dynamic_fields || {}))
    )
  );

  return (
    <div className="p-8">
      <h2 className="text-2xl font-bold mb-4">Violations</h2>
      <div className="overflow-x-auto">
        <table className="min-w-full bg-white border border-gray-200 rounded-lg">
          <thead>
            <tr>
              <th className="px-4 py-2 border-b">Reference</th>
              <th className="px-4 py-2 border-b">Category</th>
              <th className="px-4 py-2 border-b">Created At</th>
              {dynamicFieldNames.map(name => (
                <th key={name} className="px-4 py-2 border-b">{name}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {violations.map(v => (
              <tr key={v.id} className="hover:bg-gray-50">
                <td className="px-4 py-2 border-b">{v.reference}</td>
                <td className="px-4 py-2 border-b">{v.category}</td>
                <td className="px-4 py-2 border-b">{v.created_at ? new Date(v.created_at).toLocaleString() : ''}</td>
                {dynamicFieldNames.map(name => (
                  <td key={name} className="px-4 py-2 border-b">{v.dynamic_fields?.[name] || ''}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
} 