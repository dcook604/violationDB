import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import AdminFieldManager from './components/AdminFieldManager';
import DynamicViolationForm from './components/DynamicViolationForm';
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

function NewViolationPage() {
  const navigate = useNavigate();
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  const handleSubmit = async (values) => {
    setIsSubmitting(true);
    try {
      const response = await API.post('/api/violations', values);
      
      // If there are file uploads, this might take a moment
      if (response.data && response.data.id) {
        // Return the response data for file uploads
        const result = response.data;
        
        // If we have files to upload, display a different message
        if (Object.keys(values.files || {}).length > 0) {
          // The file upload will happen in DynamicViolationForm after submission
          // We'll keep the loading state active during file uploads
        } else {
          // If no files to upload, we're done
          setIsSubmitting(false);
          // Navigate to the newly created violation
          navigate(`/violations/${response.data.id}`);
        }
        return result;
      } else {
        setIsSubmitting(false);
        navigate('/violations');
      }
    } catch (error) {
      setIsSubmitting(false);
      console.error('Error creating violation:', error);
      alert('Failed to create violation: ' + (error.message || 'Unknown error'));
    }
  };
  
  // This callback will be called after file uploads complete
  const handleFileUploadsComplete = () => {
    setIsSubmitting(false);
    // Now navigate to the violation page
    if (window.latestViolationId) {
      navigate(`/violations/${window.latestViolationId}`);
    } else {
      navigate('/violations');
    }
  };
  
  return (
    <Layout>
      {/* Loading overlay - show different messages based on the stage */}
      <LoadingOverlay 
        isLoading={isSubmitting} 
        message={
          window.isUploadingFiles 
            ? "Uploading files... Please wait" 
            : "Creating violation... Please wait"
        } 
      />
      
      <h2 className="text-2xl font-bold mb-4">Create New Violation</h2>
      <DynamicViolationForm 
        onSubmit={handleSubmit} 
        submitLabel="Create Violation" 
        onFileUploadsComplete={handleFileUploadsComplete}
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
          <Route path="/admin" element={<AdminRoute><Layout><AdminFieldManager /></Layout></AdminRoute>} />
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
                <ViolationDetail />
              </Layout>
            </PrivateRoute>
          } />
        </Routes>
      </AuthProvider>
    </Router>
  );
}

export default App;
