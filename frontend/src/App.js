import React from 'react';
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
import Layout from './components/common/Layout';
import API from './api';

function NewViolationPage() {
  const navigate = useNavigate();
  
  const handleSubmit = async (values) => {
    try {
      await API.post('/api/violations', values);
      navigate('/violations');
    } catch (error) {
      console.error('Error creating violation:', error);
      alert('Failed to create violation: ' + (error.message || 'Unknown error'));
    }
  };
  
  return (
    <Layout>
      <h2 className="text-2xl font-bold mb-4">Create New Violation</h2>
      <DynamicViolationForm onSubmit={handleSubmit} submitLabel="Create Violation" />
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
