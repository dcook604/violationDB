import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import Login from './views/auth/Login';
import Dashboard from './views/Dashboard';
import { AuthProvider } from './context/AuthContext';
import { PrivateRoute, AdminRoute } from './components/Routes';
import ViolationList from './components/ViolationList';
import ViolationDetail from './components/ViolationDetail';
import UserManagement from './components/UserManagement';
import Settings from './components/Settings';
import Layout from './components/common/Layout';
import LoadingOverlay from './components/common/LoadingOverlay';
import API from './api';
import StaticViolationForm from './components/StaticViolationForm';

function NewViolationPage() {
  const navigate = useNavigate();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitMessage, setSubmitMessage] = useState('Submitting...'); // For more detailed feedback
  
  const handleSubmit = async (values) => {
    setIsSubmitting(true);
    setSubmitMessage('Creating violation record...');
    
    // 1. Separate files from other data
    const { attach_evidence, ...violationData } = values;
    const filesToUpload = attach_evidence || [];
    
    let violationId = null;

    try {
      // 2. Create the violation record (without files)
      const createResponse = await API.post('/api/violations', violationData);
      
      if (!createResponse.data || !createResponse.data.id) {
        throw new Error('Failed to create violation record. No ID received.');
      }
      violationId = createResponse.data.id;
      console.log('Violation created with ID:', violationId);

      // 3. Upload files if they exist
      if (filesToUpload.length > 0) {
        setSubmitMessage(`Uploading ${filesToUpload.length} evidence file(s)...`);
        const formData = new FormData();
        filesToUpload.forEach((file) => {
          // The backend expects files under the key 'files'
          formData.append('files', file);
        });

        // Use the field name 'attach_evidence' as a query parameter
        // if your backend endpoint /api/violations/<id>/upload requires it.
        // Check the api_upload_files route in violation_routes.py
        // It currently expects `request.args.get('field')`, but we might not need it
        // if we only have one file field. Let's omit it for now unless errors occur.
        try {
          const uploadResponse = await API.post(`/api/violations/${violationId}/upload`, formData, {
            headers: {
              'Content-Type': 'multipart/form-data',
            },
          });
          console.log('File upload response:', uploadResponse.data);
          if (uploadResponse.data.warnings && uploadResponse.data.warnings.length > 0) {
             // Optionally alert user about non-critical upload warnings
             console.warn("File upload warnings:", uploadResponse.data.warnings);
          }
        } catch (uploadError) {
            console.error('File upload failed:', uploadError.response ? uploadError.response.data : uploadError);
             // Decide how to handle upload failure: proceed with navigation? Show blocking error?
            // For now, log the error and proceed, but alert the user.
            alert(`Violation created (ID: ${violationId}), but evidence upload failed. Please try uploading files later via the edit page.\nError: ${uploadError.response?.data?.error || uploadError.message}`);
             // Skip navigation or navigate anyway?
             // Let's navigate but the user knows files failed.
        }
      }

      // 4. Success - Navigate to the new violation detail page
      setSubmitMessage('Success!');
      setIsSubmitting(false);
      navigate(`/violations/${violationId}`);

    } catch (error) {
      // Handle errors from either creation or upload step
      setIsSubmitting(false);
      setSubmitMessage('Submission failed.'); // Reset message
      console.error('Error during violation submission process:', error.response ? error.response.data : error);
      alert('Failed to submit violation: ' + (error.response?.data?.error || error.message || 'Unknown error'));
       // Do not navigate on error
    }
  };
  
  // Remove handleFileUploadsComplete as it's no longer needed with this flow
  // const handleFileUploadsComplete = () => { ... };
  
  return (
    <Layout>
      <LoadingOverlay 
        isLoading={isSubmitting} 
        message={submitMessage} // Use the dynamic message
      />
      <StaticViolationForm 
        onSubmit={handleSubmit} 
        submitLabel="Create Violation" 
      />
    </Layout>
  );
}

function App() {
  return (
    <Router>
      <AuthProvider>
        <Routes>
          {/* Public Routes */}
          <Route path="/login" element={<Login />} />
          
          {/* Protected Routes */}
          <Route path="/" element={<PrivateRoute><Layout><Navigate to="/dashboard" replace /></Layout></PrivateRoute>} />
          <Route path="/dashboard" element={<PrivateRoute><Layout><Dashboard /></Layout></PrivateRoute>} />
          
          {/* Admin Routes */}
          <Route path="/admin/users" element={<AdminRoute><Layout><UserManagement /></Layout></AdminRoute>} />
          <Route path="/admin/settings" element={<AdminRoute><Layout><Settings /></Layout></AdminRoute>} />
          
          {/* Violation Routes */}
          <Route path="/violations/new" element={
            <PrivateRoute>
              <NewViolationPage />
            </PrivateRoute>
          } />
          <Route path="/violations" element={
            <PrivateRoute>
              <Layout>
                <ViolationList />
              </Layout>
            </PrivateRoute>
          } />
          <Route path="/violations/:id" element={
            <PrivateRoute>
              <Layout>
                <ViolationDetail usePublicId={false} />
              </Layout>
            </PrivateRoute>
          } />
          <Route path="/violations/public/:publicId" element={
            <PrivateRoute>
              <Layout>
                <ViolationDetail usePublicId={true} />
              </Layout>
            </PrivateRoute>
          } />
        </Routes>
      </AuthProvider>
    </Router>
  );
}

export default App;
