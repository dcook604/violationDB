import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import API from '../api';
import Button from './common/Button';
import Spinner from './common/Spinner';
// Import the edit form if it's separate or handle editing inline
// import ViolationEditForm from './ViolationEditForm';

const ViolationDetail = ({ usePublicId = false }) => {
  const { id, publicId } = useParams();
  const navigate = useNavigate();
  const [violation, setViolation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [isEditing, setIsEditing] = useState(false);
  const [replies, setReplies] = useState([]);
  const [replyLoading, setReplyLoading] = useState(false);
  // Assuming authentication context provides user info
  // const { user } = useAuth(); 

  // Check if we're trying to use an undefined publicId and redirect if needed
  useEffect(() => {
    if (usePublicId && (publicId === 'undefined' || publicId === undefined)) {
      console.error('Invalid public ID: undefined');
      navigate('/r/7a9c3b5d2f1e'); // Redirect to violations list
      return;
    }
  }, [usePublicId, publicId, navigate]);

  const fetchViolation = useCallback(async () => {
    // Skip fetching if we have an undefined publicId
    if (usePublicId && (publicId === 'undefined' || publicId === undefined)) {
      return;
    }
    
    setLoading(true);
    setError('');
    const identifier = usePublicId ? publicId : id;
    const endpoint = usePublicId ? `/api/violations/public/${identifier}` : `/api/violations/${identifier}`;
    
    try {
      console.log(`Fetching violation details from endpoint: ${endpoint}`);
      const res = await API.get(endpoint);
      console.log('Violation data received:', res.data);
      setViolation(res.data);
    } catch (err) {
      console.error('Error fetching violation:', err);
      const errorMessage = err.response?.data?.error || err.response?.data?.message || 'Failed to load violation details';
      setError(errorMessage);
      
      // If authentication error, might need to redirect to login
      if (err.response?.status === 401) {
        setError('Authentication error: Please log in again to view this violation');
      }
    }
    setLoading(false);
  }, [id, publicId, usePublicId]);

  const fetchReplies = useCallback(async () => {
    if (!violation?.id) return;
    setReplyLoading(true);
    try {
      const res = await API.get(`/api/violations/${violation.id}/replies`);
      setReplies(res.data);
    } catch (err) {
      // Non-critical error, log or show small message
      console.error("Failed to load replies:", err);
    }
    setReplyLoading(false);
  }, [violation?.id]);

  useEffect(() => {
    fetchViolation();
  }, [fetchViolation]);

  useEffect(() => {
    if (violation) {
      fetchReplies();
    }
  }, [violation, fetchReplies]);

  const handleDelete = async () => {
    if (window.confirm('Are you sure you want to delete this violation?')) {
      try {
        await API.delete(`/api/violations/${violation.id}`);
        navigate('/r/7a9c3b5d2f1e'); // Redirect after delete
      } catch (err) {
        setError(err.response?.data?.error || 'Failed to delete violation');
      }
    }
  };

  const handleEditSave = async (updatedData) => {
    // Implement save logic using PUT /api/violations/:id
    try {
        await API.put(`/api/violations/${violation.id}`, updatedData);
        setIsEditing(false);
        fetchViolation(); // Refresh data
    } catch (err) {
        setError(err.response?.data?.error || 'Failed to update violation');
    }
  };
  
  // Helper to format date
  const formatDate = (dateString) => {
      if (!dateString) return 'N/A';
      try {
          return new Date(dateString).toLocaleDateString();
      } catch { return dateString; }
  }
  const formatDateTime = (dateString) => {
      if (!dateString) return 'N/A';
      try {
          return new Date(dateString).toLocaleString();
      } catch { return dateString; }
  }

  if (loading) return <div className="p-4"><Spinner /> Loading violation details...</div>;
  if (error) return (
    <div className="p-4">
      <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
        <p><strong>Error:</strong> {error}</p>
        {error.includes('Authentication') && (
          <p className="mt-2">
            <Link to="/login" className="text-blue-600 hover:underline">Log in again</Link> or return to the 
            <Link to="/r/7a9c3b5d2f1e" className="text-blue-600 hover:underline ml-1">violations list</Link>.
          </p>
        )}
      </div>
      <Link to="/r/7a9c3b5d2f1e" className="text-blue-600 hover:underline">
        &larr; Back to Violations List
      </Link>
    </div>
  );
  
  if (!violation) return (
    <div className="p-4">
      <div className="bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded mb-4">
        <p>Violation not found. The record may have been deleted or you may not have permission to view it.</p>
      </div>
      <Link to="/r/7a9c3b5d2f1e" className="text-blue-600 hover:underline">
        &larr; Back to Violations List
      </Link>
    </div>
  );

  // TODO: Replace with actual check from auth context
  const canEditDelete = true; // Assume user can edit/delete for now

  return (
    <div className="p-4 md:p-8">
       {/* Go Back Link */} 
       <div className="mb-4">
         <Link to="/r/7a9c3b5d2f1e" className="text-blue-600 hover:underline text-sm">
           &larr; Back to Violations List
         </Link>
       </div>

      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-2xl font-bold mb-6 text-gray-800">Violation Details</h2>

        {/* Edit Mode - Render form or inline editable fields */} 
        {isEditing ? (
            // <ViolationEditForm violation={violation} onSave={handleEditSave} onCancel={() => setIsEditing(false)} />
            <div className="text-center p-4 border rounded bg-gray-100">
                <p className="mb-2">Inline editing form placeholder.</p>
                <Button onClick={() => setIsEditing(false)} color="gray">Cancel</Button>
            </div>
        ) : (
          <> 
            {/* Display Static Fields */} 
            <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-4 mb-6">
                <div><strong className="text-gray-600">Reference:</strong> {violation.reference}</div>
                <div><strong className="text-gray-600">Status:</strong> {violation.status}</div>
                <div><strong className="text-gray-600">Created At:</strong> {formatDateTime(violation.created_at)}</div>
                <div><strong className="text-gray-600">Created By:</strong> {violation.created_by_email || violation.created_by}</div>
                <div><strong className="text-gray-600">Incident Date:</strong> {formatDate(violation.incident_date)}</div>
                <div><strong className="text-gray-600">Incident Time:</strong> {violation.incident_time || 'N/A'}</div>
                <div><strong className="text-gray-600">Unit No.:</strong> {violation.unit_number}</div>
                <div><strong className="text-gray-600">Building:</strong> {violation.building}</div>
                <div className="md:col-span-2"><strong className="text-gray-600">Category:</strong> {violation.category}</div>
            </div>

            {/* Owner Info */} 
            <div className="mb-6 p-4 bg-gray-50 rounded border">
                <h3 className="text-lg font-semibold mb-3 text-gray-700">Owner/Property Manager</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-2">
                    <div><strong className="text-gray-600">Name:</strong> {`${violation.owner_property_manager_name?.first || ''} ${violation.owner_property_manager_name?.last || ''}`.trim()}</div>
                    <div><strong className="text-gray-600">Email:</strong> {violation.owner_property_manager_email || 'N/A'}</div>
                    <div><strong className="text-gray-600">Telephone:</strong> {violation.owner_property_manager_telephone || 'N/A'}</div>
                </div>
            </div>

             {/* Tenant Info (Optional) */}
            {(violation.tenant_name?.first || violation.tenant_name?.last || violation.tenant_email || violation.tenant_phone) && (
                <div className="mb-6 p-4 bg-gray-50 rounded border">
                    <h3 className="text-lg font-semibold mb-3 text-gray-700">Tenant Information</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-2">
                        <div><strong className="text-gray-600">Name:</strong> {`${violation.tenant_name?.first || ''} ${violation.tenant_name?.last || ''}`.trim() || 'N/A'}</div>
                        <div><strong className="text-gray-600">Email:</strong> {violation.tenant_email || 'N/A'}</div>
                        <div><strong className="text-gray-600">Phone:</strong> {violation.tenant_phone || 'N/A'}</div>
                    </div>
                </div>
            )}
            
             {/* Other Details */}
             <div className="mb-6 p-4 bg-gray-50 rounded border">
                <h3 className="text-lg font-semibold mb-3 text-gray-700">Violation Details</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-4">
                    <div><strong className="text-gray-600">Location:</strong> {violation.where_did || 'N/A'}</div>
                    <div><strong className="text-gray-600">Security/Police Called:</strong> {violation.was_security_or_police_called || 'N/A'}</div>
                    <div><strong className="text-gray-600">Fine Levied:</strong> {violation.fine_levied || 'N/A'}</div>
                    <div><strong className="text-gray-600">Noticed By:</strong> {violation.noticed_by || 'N/A'}</div>
                    <div><strong className="text-gray-600">Concierge Shift:</strong> {violation.concierge_shift || 'N/A'}</div>
                    <div><strong className="text-gray-600">People Called:</strong> {violation.people_called || 'N/A'}</div>
                    <div><strong className="text-gray-600">Actioned By:</strong> {violation.actioned_by || 'N/A'}</div>
                    <div className="md:col-span-2"><strong className="text-gray-600">People Involved:</strong> {violation.people_involved || 'N/A'}</div>
                </div>
            </div>

             {/* Incident Details & Action Taken */}
             <div className="mb-6">
                <h3 className="text-lg font-semibold mb-2 text-gray-700">Incident Details</h3>
                <p className="text-gray-700 whitespace-pre-wrap">{violation.incident_details || 'Not provided.'}</p>
            </div>
             <div className="mb-6">
                <h3 className="text-lg font-semibold mb-2 text-gray-700">Action Taken</h3>
                <p className="text-gray-700 whitespace-pre-wrap">{violation.action_taken || 'Not specified.'}</p>
            </div>

            {/* Attached Evidence */} 
            <div className="mb-6">
                <h3 className="text-lg font-semibold mb-3 text-gray-700">Attached Evidence</h3>
                {violation.attach_evidence && violation.attach_evidence.length > 0 ? (
                    <ul className="list-disc list-inside pl-5">
                    {violation.attach_evidence.map((file, index) => {
                        const filename = typeof file === 'string' ? file : file.name;
                        const evidenceUrl = `/evidence/${violation.id}/${filename}`;
                        // Basic image check by extension
                        const isImage = /\.(jpg|jpeg|png|gif)$/i.test(filename);
                        return (
                        <li key={index} className="mb-2">
                            <a 
                            href={evidenceUrl} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="text-blue-600 hover:underline"
                            >
                            {isImage ? (
                                <img src={evidenceUrl} alt={filename} className="max-w-xs max-h-32 inline-block mr-2 border" />
                            ) : (
                                <i className="fas fa-file mr-2"></i> // Example using Font Awesome
                            )}
                            {filename}
                            </a>
                        </li>
                        );
                    })}
                    </ul>
                ) : (
                    <p className="text-gray-500">No evidence attached.</p>
                )}
            </div>
            
            {/* Replies Section */} 
            <div className="mb-6">
                <h3 className="text-lg font-semibold mb-3 text-gray-700">Replies</h3>
                {replyLoading ? (
                    <Spinner size="sm" />
                ) : replies.length > 0 ? (
                    <ul className="space-y-4">
                    {replies.map(reply => (
                        <li key={reply.id} className="p-3 bg-gray-100 rounded border">
                        <p className="text-sm text-gray-800 whitespace-pre-wrap">{reply.response_text}</p>
                        <p className="text-xs text-gray-500 mt-1">From: {reply.email} on {formatDateTime(reply.created_at)}</p>
                        </li>
                    ))}
                    </ul>
                ) : (
                    <p className="text-gray-500">No replies yet.</p>
                )}
                <button onClick={fetchReplies} className="text-blue-600 text-sm mt-2 hover:underline">Refresh Replies</button>
            </div>

            {/* Action Buttons */} 
            <div className="mt-8 flex flex-wrap items-center gap-3 border-t pt-6">
                <Button 
                    onClick={() => window.open(`/violations/view/${violation.id}`, '_blank')}
                    color="blueGray"
                >
                    View as HTML
                </Button>
                <Button 
                    onClick={() => window.location.href = `/violations/pdf/${violation.id}`}
                    color="blueGray"
                >
                    Download PDF
                </Button>
                {canEditDelete && (
                    <Button onClick={() => setIsEditing(true)} color="lightBlue">
                        Edit
                    </Button>
                )}
                {canEditDelete && (
                    <Button 
                        onClick={handleDelete} 
                        color="red"
                        className="bg-red-500 hover:bg-red-600 text-white"
                    >
                        Delete
                    </Button>
                )}
            </div>
          </> 
        )} 
      </div>
    </div>
  );
};

export default ViolationDetail; 