import React, { useEffect, useState } from 'react';
import API from '../api';
import Table from './common/Table';
import Button from './common/Button';
import Modal from './common/Modal';
import Input from './common/Input';

export default function UserManagement() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [modalType, setModalType] = useState(''); // 'add' | 'edit' | 'delete' | 'password'
  const [selectedUser, setSelectedUser] = useState(null);
  const [form, setForm] = useState({ email: '', role: 'user', is_active: true });
  const [password, setPassword] = useState('');
  const [defaultPassword, setDefaultPassword] = useState('changeme123');
  const [useCustomPassword, setUseCustomPassword] = useState(false);
  const [saving, setSaving] = useState(false);
  const [search, setSearch] = useState('');

  useEffect(() => { fetchUsers(); }, []);

  // Clear success message after 5 seconds
  useEffect(() => {
    if (success) {
      const timer = setTimeout(() => {
        setSuccess(null);
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [success]);

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const res = await API.get('/api/users');
      setUsers(res.data);
    } catch (err) {
      setError('Failed to load users');
    }
    setLoading(false);
  };

  const openModal = (type, user = null) => {
    setModalType(type);
    setSelectedUser(user);
    setShowModal(true);
    setError(null);
    if (type === 'edit' && user) {
      setForm({ email: user.email, role: user.role, is_active: user.is_active });
    } else if (type === 'add') {
      setForm({ email: '', role: 'user', is_active: true });
      setDefaultPassword('changeme123');
      setUseCustomPassword(false);
    } else if (type === 'password') {
      setPassword('');
    }
  };
  const closeModal = () => { setShowModal(false); setError(null); };

  const handleChange = e => {
    const { name, value, type, checked } = e.target;
    setForm(f => ({ ...f, [name]: type === 'checkbox' ? checked : value }));
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      if (modalType === 'add') {
        // Include password in the creation payload
        const userPayload = { ...form, password: useCustomPassword ? password : defaultPassword };
        const res = await API.post('/api/users', userPayload);
        
        // Show success message with password info if default was used
        if (!useCustomPassword) {
          setSuccess(`User ${form.email} created successfully with password: ${defaultPassword}`);
        } else {
          setSuccess(`User ${form.email} created successfully with custom password`);
        }
      } else if (modalType === 'edit' && selectedUser) {
        await API.put(`/api/users/${selectedUser.id}`, form);
        setSuccess(`User ${form.email} updated successfully`);
      }
      closeModal();
      fetchUsers();
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to save user');
    }
    setSaving(false);
  };

  const handleDelete = async () => {
    setSaving(true);
    try {
      await API.delete(`/api/users/${selectedUser.id}`);
      setSuccess(`User ${selectedUser.email} deleted successfully`);
      closeModal();
      fetchUsers();
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to delete user');
    }
    setSaving(false);
  };

  const handleChangePassword = async () => {
    setSaving(true);
    try {
      await API.post(`/api/users/${selectedUser.id}/change-password`, { password });
      setSuccess(`Password for ${selectedUser.email} changed successfully`);
      closeModal();
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to change password');
    }
    setSaving(false);
  };

  const filteredUsers = users.filter(u =>
    u.email.toLowerCase().includes(search.toLowerCase()) ||
    u.role.toLowerCase().includes(search.toLowerCase())
  );

  const columns = [
    { label: 'Email', accessor: 'email' },
    { label: 'Role', accessor: 'role' },
    { label: 'Active', accessor: 'is_active' },
    { label: 'Actions', accessor: 'actions' },
  ];

  return (
    <div className="p-8">
      <h2 className="text-2xl font-bold mb-4">User Management</h2>
      
      {/* Success message */}
      {success && (
        <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded relative mb-4">
          <span className="block sm:inline">{success}</span>
          <span className="absolute top-0 bottom-0 right-0 px-4 py-3" onClick={() => setSuccess(null)}>
            <svg className="fill-current h-6 w-6 text-green-500" role="button" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">
              <title>Close</title>
              <path d="M14.348 14.849a1.2 1.2 0 0 1-1.697 0L10 11.819l-2.651 3.029a1.2 1.2 0 1 1-1.697-1.697l2.758-3.15-2.759-3.152a1.2 1.2 0 1 1 1.697-1.697L10 8.183l2.651-3.031a1.2 1.2 0 1 1 1.697 1.697l-2.758 3.152 2.758 3.15a1.2 1.2 0 0 1 0 1.698z"/>
            </svg>
          </span>
        </div>
      )}
      
      <div className="mb-4 flex items-center gap-2">
        <Button className="bg-blue-600 text-white" onClick={() => openModal('add')}>Add User</Button>
        <Input
          placeholder="Search by email or role..."
          value={search}
          onChange={e => setSearch(e.target.value)}
          className="w-64"
        />
      </div>
      {loading ? <div>Loading...</div> : (
        <Table
          columns={columns}
          data={filteredUsers}
          renderCell={(row, col) => {
            if (col.accessor === 'actions') {
              return (
                <div className="flex gap-2">
                  <Button className="bg-yellow-500 text-white text-xs px-2 py-1" onClick={() => openModal('edit', row)}>Edit</Button>
                  <Button className="bg-red-600 text-white text-xs px-2 py-1" onClick={() => openModal('delete', row)}>Delete</Button>
                  <Button className="bg-gray-600 text-white text-xs px-2 py-1" onClick={() => openModal('password', row)}>Change Password</Button>
                </div>
              );
            }
            if (col.accessor === 'is_active') {
              return row.is_active ? 'Yes' : 'No';
            }
            return row[col.accessor];
          }}
        />
      )}
      <Modal
        isOpen={showModal}
        onClose={closeModal}
        title={modalType === 'add' ? 'Add User' : modalType === 'edit' ? 'Edit User' : modalType === 'delete' ? 'Delete User' : 'Change Password'}
        actions={
          modalType === 'delete' ? [
            <Button key="cancel" onClick={closeModal} className="bg-gray-300">Cancel</Button>,
            <Button key="delete" onClick={handleDelete} className="bg-red-600 text-white" disabled={saving}>Delete</Button>
          ] : modalType === 'password' ? [
            <Button key="cancel" onClick={closeModal} className="bg-gray-300">Cancel</Button>,
            <Button key="save" onClick={handleChangePassword} className="bg-blue-600 text-white" disabled={saving}>Change</Button>
          ] : [
            <Button key="cancel" onClick={closeModal} className="bg-gray-300">Cancel</Button>,
            <Button key="save" onClick={handleSave} className="bg-blue-600 text-white" disabled={saving}>{modalType === 'add' ? 'Add' : 'Save'}</Button>
          ]
        }
      >
        {error && <div className="text-red-600 mb-2">{error}</div>}
        {(modalType === 'add' || modalType === 'edit') && (
          <form onSubmit={e => { e.preventDefault(); handleSave(); }}>
            <div className="mb-2">
              <label className="block font-semibold mb-1">Email</label>
              <Input name="email" value={form.email} onChange={handleChange} />
            </div>
            <div className="mb-2">
              <label className="block font-semibold mb-1">Role</label>
              <select name="role" value={form.role} onChange={handleChange} className="border p-2 rounded w-full">
                <option value="user">User</option>
                <option value="admin">Admin</option>
              </select>
            </div>
            {modalType === 'add' && (
              <div className="mb-4">
                <label className="block font-semibold mb-1">Password</label>
                <div className="mb-2">
                  <div className="flex items-center gap-2 mb-2">
                    <input 
                      type="radio" 
                      id="defaultPwd" 
                      checked={!useCustomPassword} 
                      onChange={() => setUseCustomPassword(false)} 
                      className="accent-blue-600" 
                    />
                    <label htmlFor="defaultPwd" className="font-medium">Use default password</label>
                  </div>
                  <Input 
                    name="defaultPassword"
                    value={defaultPassword} 
                    onChange={e => setDefaultPassword(e.target.value)}
                    disabled={useCustomPassword}
                    className={useCustomPassword ? "bg-gray-100" : ""}
                  />
                </div>
                <div className="mb-2">
                  <div className="flex items-center gap-2 mb-2">
                    <input 
                      type="radio" 
                      id="customPwd" 
                      checked={useCustomPassword} 
                      onChange={() => setUseCustomPassword(true)} 
                      className="accent-blue-600" 
                    />
                    <label htmlFor="customPwd" className="font-medium">Use custom password</label>
                  </div>
                  <Input 
                    name="password"
                    type="password" 
                    value={password} 
                    onChange={e => setPassword(e.target.value)}
                    disabled={!useCustomPassword}
                    className={!useCustomPassword ? "bg-gray-100" : ""}
                    placeholder="Enter custom password"
                  />
                </div>
              </div>
            )}
            <div className="mb-2 flex items-center gap-2">
              <input type="checkbox" name="is_active" checked={form.is_active} onChange={handleChange} className="accent-blue-600" />
              <label className="font-semibold">Active</label>
            </div>
          </form>
        )}
        {modalType === 'password' && (
          <form onSubmit={e => { e.preventDefault(); handleChangePassword(); }}>
            <div className="mb-2">
              <label className="block font-semibold mb-1">New Password</label>
              <Input name="password" type="password" value={password} onChange={e => setPassword(e.target.value)} />
            </div>
          </form>
        )}
        {modalType === 'delete' && (
          <div>Are you sure you want to delete user <b>{selectedUser?.email}</b>?</div>
        )}
      </Modal>
    </div>
  );
} 