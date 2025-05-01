import React, { useEffect, useState, memo, useCallback } from 'react';
import API from '../api';
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';
import Button from './common/Button';
import Input from './common/Input';

// Memoized list item component to improve performance
const DraggableItem = memo(({ field, onEdit, onDelete, onToggle, index }) => (
  <Draggable draggableId={String(field.id)} index={index}>
    {provided => (
      <li ref={provided.innerRef} {...provided.draggableProps} {...provided.dragHandleProps} className="list-group-item d-flex align-items-center justify-content-between">
        <span>{field.label} ({field.type}) {field.required && <b>*</b>} {!field.active && <span className="badge bg-secondary">Inactive</span>}</span>
        <div>
          <Button className="bg-yellow-500 text-white text-xs px-2 py-1 mr-1" onClick={() => onEdit(field)}>Edit</Button>
          <Button className="bg-red-600 text-white text-xs px-2 py-1 mr-1" onClick={() => onDelete(field.id)}>Delete</Button>
          <Button className="bg-gray-500 text-white text-xs px-2 py-1" onClick={() => onToggle(field.id)}>{field.active ? 'Disable' : 'Enable'}</Button>
        </div>
      </li>
    )}
  </Draggable>
));

// Initial form state
const initialFormState = {
  name: '',
  label: '',
  type: 'text',
  required: false,
  options: '',
  validation: '',
  grid_column: 0 // Default to full width
};

function AdminFieldManager() {
  const [fields, setFields] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [form, setForm] = useState(initialFormState);
  const [editing, setEditing] = useState(null);
  
  // Memoize handlers to prevent re-renders
  const handleEdit = useCallback(field => {
    setEditing(field);
    setForm({
      name: field.name,
      label: field.label,
      type: field.type,
      required: field.required,
      options: field.options || '',
      validation: field.validation || '',
      grid_column: field.grid_column || 0
    });
  }, []);

  const handleDelete = useCallback(async id => {
    if (!window.confirm('Delete this field?')) return;
    try {
      await API.delete(`/api/fields/${id}`);
      fetchFields();
    } catch (err) {
      setError('Failed to delete field');
    }
  }, []);

  const handleToggle = useCallback(async id => {
    try {
      await API.post(`/api/fields/${id}/toggle`);
      fetchFields();
    } catch (err) {
      setError('Failed to toggle field');
    }
  }, []);

  const fetchFields = useCallback(async () => {
    setLoading(true);
    try {
      // Request all fields, including inactive ones
      const res = await API.get('/api/fields?active=false');
      setFields(res.data);
    } catch (err) {
      setError('Failed to load fields');
    }
    setLoading(false);
  }, []);

  useEffect(() => {
    fetchFields();
  }, [fetchFields]);

  const handleChange = useCallback(e => {
    const { name, value, type, checked } = e.target;
    setForm(f => ({ ...f, [name]: type === 'checkbox' ? checked : value }));
    
    // Set default validation for file type
    if (name === 'type' && value === 'file') {
      setForm(f => ({ 
        ...f, 
        [name]: value,
        validation: f.validation || JSON.stringify({
          maxFiles: 5,
          maxSizePerFile: 5, // in MB
          allowedTypes: ['image/jpeg', 'image/png', 'image/gif']
        })
      }));
    }
  }, []);

  const handleSubmit = async e => {
    e.preventDefault();
    try {
      if (editing) {
        await API.put(`/api/fields/${editing.id}`, form);
      } else {
        await API.post('/api/fields', form);
      }
      setForm(initialFormState);
      setEditing(null);
      fetchFields();
    } catch (err) {
      setError('Failed to save field');
    }
  };

  const onDragEnd = async result => {
    if (!result.destination) return;
    const reordered = Array.from(fields);
    const [removed] = reordered.splice(result.source.index, 1);
    reordered.splice(result.destination.index, 0, removed);
    setFields(reordered);
    try {
      await API.post('/api/fields/reorder', { order: reordered.map(f => f.id) });
    } catch (err) {
      setError('Failed to reorder fields');
    }
  };

  const resetForm = () => {
    setForm(initialFormState);
    setEditing(null);
  };

  const handleValidationChange = e => {
    if (form.type === 'file') {
      try {
        const currentValidation = form.validation ? JSON.parse(form.validation) : {
          maxFiles: 5,
          maxSizePerFile: 5,
          allowedTypes: ['image/jpeg', 'image/png', 'image/gif']
        };
        
        const { name, value, type } = e.target;
        const newValidation = {
          ...currentValidation,
          [name]: type === 'number' ? Number(value) : value
        };
        
        setForm(f => ({
          ...f,
          validation: JSON.stringify(newValidation)
        }));
      } catch (err) {
        console.error('Invalid validation JSON', err);
      }
    }
  };

  return (
    <div>
      <h2>Admin Field Manager</h2>
      {error && <div className="alert alert-danger">{error}</div>}
      <form onSubmit={handleSubmit} className="mb-3 flex flex-wrap gap-2 items-center">
        <Input name="name" value={form.name} onChange={handleChange} placeholder="Name" required disabled={!!editing} className="w-32" />
        <Input name="label" value={form.label} onChange={handleChange} placeholder="Label" required className="w-32" />
        <select name="type" value={form.type} onChange={handleChange} className="border p-2 rounded w-28">
          <option value="text">Text</option>
          <option value="email">Email</option>
          <option value="number">Number</option>
          <option value="date">Date</option>
          <option value="time">Time</option>
          <option value="select">Select</option>
          <option value="file">File Upload</option>
        </select>
        <label className="flex items-center gap-1">
          <input type="checkbox" name="required" checked={form.required} onChange={handleChange} className="accent-blue-600" /> Required
        </label>
        
        {/* Add grid column selector */}
        <div className="ml-2">
          <label className="text-xs block">Layout Width</label>
          <select 
            name="grid_column" 
            value={form.grid_column} 
            onChange={handleChange} 
            className="border p-2 rounded text-sm"
          >
            <option value="0">Full Width</option>
            <option value="6">Half Width</option>
            <option value="4">Third Width</option>
            <option value="3">Quarter Width</option>
          </select>
        </div>

        {form.type === 'select' && (
          <Input name="options" value={form.options || ''} onChange={handleChange} placeholder="Comma-separated options" className="w-48" />
        )}
        {form.type === 'file' && (
          <div className="w-full mt-2 p-2 border rounded bg-gray-50">
            <h4 className="text-sm font-bold mb-2">File Upload Settings</h4>
            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="text-xs block">Max Files</label>
                <Input 
                  type="number" 
                  name="maxFiles" 
                  value={form.validation ? JSON.parse(form.validation).maxFiles : 5}
                  onChange={handleValidationChange}
                  min="1" 
                  max="5" 
                  className="w-full text-sm"
                />
              </div>
              <div>
                <label className="text-xs block">Max Size per File (MB)</label>
                <Input 
                  type="number" 
                  name="maxSizePerFile" 
                  value={form.validation ? JSON.parse(form.validation).maxSizePerFile : 5}
                  onChange={handleValidationChange}
                  min="1" 
                  max="5" 
                  className="w-full text-sm"
                />
              </div>
            </div>
            <p className="text-xs text-gray-500 mt-1">Allowed file types: JPEG, PNG, GIF</p>
          </div>
        )}
        <div className="w-full flex gap-2 mt-3">
          <Button type="submit" className="bg-blue-600 text-white hover:bg-blue-700 text-sm">{editing ? 'Update' : 'Add'} Field</Button>
          {editing && <Button type="button" className="bg-gray-300 text-sm" onClick={resetForm}>Cancel</Button>}
        </div>
      </form>
      {loading ? <div>Loading...</div> : (
        <DragDropContext onDragEnd={onDragEnd}>
          <Droppable droppableId="fields">
            {provided => (
              <ul {...provided.droppableProps} ref={provided.innerRef} className="list-group">
                {fields.map((field, idx) => (
                  <DraggableItem
                    key={field.id}
                    field={field}
                    index={idx}
                    onEdit={handleEdit}
                    onDelete={handleDelete}
                    onToggle={handleToggle}
                  />
                ))}
                {provided.placeholder}
              </ul>
            )}
          </Droppable>
        </DragDropContext>
      )}
    </div>
  );
}

export default memo(AdminFieldManager); 