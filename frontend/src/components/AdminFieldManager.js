import React, { useEffect, useState, memo } from 'react';
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
  options: ''
};

function AdminFieldManager() {
  const [fields, setFields] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [form, setForm] = useState(initialFormState);
  const [editing, setEditing] = useState(null);

  useEffect(() => {
    fetchFields();
  }, []);

  const fetchFields = async () => {
    setLoading(true);
    try {
      const res = await API.get('/api/fields');
      setFields(res.data);
    } catch (err) {
      setError('Failed to load fields');
    }
    setLoading(false);
  };

  const handleChange = e => {
    const { name, value, type, checked } = e.target;
    setForm(f => ({ ...f, [name]: type === 'checkbox' ? checked : value }));
  };

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

  const handleEdit = field => {
    setEditing(field);
    setForm({
      name: field.name,
      label: field.label,
      type: field.type,
      required: field.required,
      options: field.options || '',
    });
  };

  const handleDelete = async id => {
    if (!window.confirm('Delete this field?')) return;
    try {
      await API.delete(`/api/fields/${id}`);
      fetchFields();
    } catch (err) {
      setError('Failed to delete field');
    }
  };

  const handleToggle = async id => {
    try {
      await API.post(`/api/fields/${id}/toggle`);
      fetchFields();
    } catch (err) {
      setError('Failed to toggle field');
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

  return (
    <div>
      <h2>Admin Field Manager</h2>
      {error && <div className="alert alert-danger">{error}</div>}
      <form onSubmit={handleSubmit} className="mb-3 flex flex-wrap gap-2 items-center">
        <Input name="name" value={form.name} onChange={handleChange} placeholder="Name" required disabled={!!editing} className="w-32" />
        <Input name="label" value={form.label} onChange={handleChange} placeholder="Label" required className="w-32" />
        <select name="type" value={form.type} onChange={handleChange} className="border p-2 rounded w-28">
          <option value="text">Text</option>
          <option value="number">Number</option>
          <option value="date">Date</option>
          <option value="select">Select</option>
        </select>
        <label className="flex items-center gap-1">
          <input type="checkbox" name="required" checked={form.required} onChange={handleChange} className="accent-blue-600" /> Required
        </label>
        {form.type === 'select' && (
          <Input name="options" value={form.options || ''} onChange={handleChange} placeholder="Comma-separated options" className="w-48" />
        )}
        <Button type="submit" className="bg-blue-600 text-white hover:bg-blue-700 text-sm">{editing ? 'Update' : 'Add'} Field</Button>
        {editing && <Button type="button" className="bg-gray-300 text-sm" onClick={resetForm}>Cancel</Button>}
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