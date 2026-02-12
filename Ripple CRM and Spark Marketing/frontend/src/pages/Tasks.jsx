import { useEffect, useState, useCallback } from 'react';
import { PlusIcon, CheckCircleIcon } from '@heroicons/react/24/outline';
import { api } from '../lib/api';
import Modal from '../components/Modal';
import { toast } from '../components/Toast';

const STATUSES = ['todo', 'in_progress', 'done', 'cancelled'];
const PRIORITIES = ['low', 'medium', 'high', 'urgent'];
const STATUS_LABELS = { todo: 'To Do', in_progress: 'In Progress', done: 'Done', cancelled: 'Cancelled' };
const PRIORITY_COLOURS = {
  low: 'text-text-muted',
  medium: 'text-text-secondary',
  high: 'text-warning',
  urgent: 'text-critical',
};
const STATUS_COLOURS = {
  todo: 'bg-surface-light text-text-secondary',
  in_progress: 'bg-gold/10 text-gold',
  done: 'bg-healthy/10 text-healthy',
  cancelled: 'bg-surface-light text-text-muted',
};

function TaskForm({ onSubmit, contacts }) {
  const [form, setForm] = useState({
    title: '', description: '', due_date: '', priority: 'medium',
    status: 'todo', contact_id: '',
  });
  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }));
  const cls = 'bg-midnight border border-border rounded-lg px-3 py-2 text-sm text-text-primary placeholder-text-muted focus:outline-none focus:border-gold';

  return (
    <form onSubmit={(e) => {
      e.preventDefault();
      const payload = { ...form };
      if (!payload.description) delete payload.description;
      if (!payload.due_date) delete payload.due_date;
      if (!payload.contact_id) delete payload.contact_id;
      onSubmit(payload);
    }} className="space-y-3">
      <input placeholder="Task title *" required value={form.title} onChange={set('title')} className={`w-full ${cls}`} />
      <div className="grid grid-cols-2 gap-3">
        <select value={form.priority} onChange={set('priority')} className={cls}>
          {PRIORITIES.map((p) => <option key={p} value={p}>{p.charAt(0).toUpperCase() + p.slice(1)}</option>)}
        </select>
        <input type="date" placeholder="Due date" value={form.due_date} onChange={set('due_date')} className={cls} />
      </div>
      <select value={form.contact_id} onChange={set('contact_id')} className={`w-full ${cls}`}>
        <option value="">Link to contact (optional)</option>
        {contacts.map((c) => (
          <option key={c.id} value={c.id}>{c.first_name} {c.last_name}</option>
        ))}
      </select>
      <textarea placeholder="Description" value={form.description} onChange={set('description')} rows={2} className={`w-full ${cls}`} />
      <button type="submit"
        className="w-full bg-gold hover:bg-gold-light text-midnight font-medium py-2 rounded-lg text-sm transition-colors">
        Create Task
      </button>
    </form>
  );
}

export default function Tasks() {
  const [tasks, setTasks] = useState([]);
  const [contacts, setContacts] = useState([]);
  const [total, setTotal] = useState(0);
  const [statusFilter, setStatusFilter] = useState('');
  const [priorityFilter, setPriorityFilter] = useState('');
  const [showCreate, setShowCreate] = useState(false);
  const [loading, setLoading] = useState(true);

  const fetchTasks = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({ page_size: '100' });
      if (statusFilter) params.set('status', statusFilter);
      if (priorityFilter) params.set('priority', priorityFilter);
      const data = await api.get(`/tasks?${params}`);
      setTasks(data.items);
      setTotal(data.total);
    } catch (err) {
      toast(err.message, 'error');
    } finally {
      setLoading(false);
    }
  }, [statusFilter, priorityFilter]);

  const fetchContacts = useCallback(async () => {
    try {
      const data = await api.get('/contacts?page_size=200');
      setContacts(data.items);
    } catch { /* ignore */ }
  }, []);

  useEffect(() => { fetchTasks(); }, [fetchTasks]);
  useEffect(() => { fetchContacts(); }, [fetchContacts]);

  const handleCreate = async (form) => {
    try {
      await api.post('/tasks', form);
      toast('Task created');
      setShowCreate(false);
      fetchTasks();
    } catch (err) {
      toast(err.message, 'error');
    }
  };

  const handleStatusChange = async (taskId, newStatus) => {
    try {
      await api.put(`/tasks/${taskId}`, { status: newStatus });
      toast(`Task ${newStatus === 'done' ? 'completed' : 'updated'}`);
      fetchTasks();
    } catch (err) {
      toast(err.message, 'error');
    }
  };

  const handleDelete = async (taskId) => {
    try {
      await api.delete(`/tasks/${taskId}`);
      toast('Task deleted');
      fetchTasks();
    } catch (err) {
      toast(err.message, 'error');
    }
  };

  const today = new Date().toISOString().split('T')[0];
  const overdueTasks = tasks.filter((t) => t.due_date && t.due_date < today && !['done', 'cancelled'].includes(t.status));

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="font-heading text-2xl font-semibold">Tasks</h1>
          <p className="text-text-secondary text-sm mt-1">
            {total} task{total !== 1 ? 's' : ''}
            {overdueTasks.length > 0 && <span className="text-critical ml-2">· {overdueTasks.length} overdue</span>}
          </p>
        </div>
        <button onClick={() => setShowCreate(true)}
          className="flex items-center gap-2 bg-gold hover:bg-gold-light text-midnight font-medium px-4 py-2 rounded-lg text-sm transition-colors">
          <PlusIcon className="w-4 h-4" /> Add Task
        </button>
      </div>

      <div className="flex gap-2 mb-4 flex-wrap">
        <div className="flex gap-1">
          <button onClick={() => setStatusFilter('')}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${!statusFilter ? 'bg-gold text-midnight' : 'bg-surface border border-border text-text-secondary'}`}>
            All
          </button>
          {STATUSES.map((s) => (
            <button key={s} onClick={() => setStatusFilter(s)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${statusFilter === s ? 'bg-gold text-midnight' : 'bg-surface border border-border text-text-secondary'}`}>
              {STATUS_LABELS[s]}
            </button>
          ))}
        </div>
        <div className="border-l border-border mx-1" />
        <select value={priorityFilter} onChange={(e) => setPriorityFilter(e.target.value)}
          className="bg-surface border border-border rounded-lg px-3 py-1.5 text-xs text-text-primary focus:outline-none focus:border-gold">
          <option value="">All priorities</option>
          {PRIORITIES.map((p) => <option key={p} value={p}>{p.charAt(0).toUpperCase() + p.slice(1)}</option>)}
        </select>
      </div>

      {loading ? (
        <div className="text-text-muted text-sm py-8 text-center">Loading tasks...</div>
      ) : tasks.length === 0 ? (
        <div className="text-center py-12 text-text-secondary">
          <p className="text-lg mb-2">No tasks yet</p>
          <p className="text-sm">Create your first task to stay on top of your work.</p>
        </div>
      ) : (
        <div className="bg-surface border border-border rounded-xl overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border text-text-muted text-xs uppercase tracking-wider">
                <th className="text-left px-4 py-3 w-8"></th>
                <th className="text-left px-4 py-3">Task</th>
                <th className="text-left px-4 py-3">Priority</th>
                <th className="text-left px-4 py-3">Due Date</th>
                <th className="text-left px-4 py-3">Status</th>
                <th className="text-right px-4 py-3">Actions</th>
              </tr>
            </thead>
            <tbody>
              {tasks.map((t) => {
                const isOverdue = t.due_date && t.due_date < today && !['done', 'cancelled'].includes(t.status);
                return (
                  <tr key={t.id} className={`border-b border-border transition-colors ${isOverdue ? 'bg-critical/5' : 'hover:bg-surface-light'}`}>
                    <td className="px-4 py-3">
                      <button onClick={() => handleStatusChange(t.id, t.status === 'done' ? 'todo' : 'done')}
                        className={`w-5 h-5 rounded-full border-2 flex items-center justify-center transition-colors ${t.status === 'done' ? 'border-healthy bg-healthy/20' : 'border-border hover:border-gold'}`}>
                        {t.status === 'done' && <CheckCircleIcon className="w-3 h-3 text-healthy" />}
                      </button>
                    </td>
                    <td className={`px-4 py-3 ${t.status === 'done' || t.status === 'cancelled' ? 'line-through text-text-muted' : 'text-text-primary'}`}>
                      <span className="font-medium">{t.title}</span>
                      {t.description && <p className="text-xs text-text-muted mt-0.5 line-clamp-1">{t.description}</p>}
                    </td>
                    <td className={`px-4 py-3 text-xs font-medium ${PRIORITY_COLOURS[t.priority]}`}>
                      {t.priority}
                    </td>
                    <td className={`px-4 py-3 text-xs ${isOverdue ? 'text-critical font-medium' : 'text-text-secondary'}`}>
                      {t.due_date || '—'}
                      {isOverdue && <span className="ml-1 text-critical">overdue</span>}
                    </td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${STATUS_COLOURS[t.status]}`}>
                        {STATUS_LABELS[t.status]}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-right">
                      <select value={t.status} onChange={(e) => handleStatusChange(t.id, e.target.value)}
                        className="bg-midnight border border-border rounded px-2 py-1 text-xs text-text-primary mr-2">
                        {STATUSES.map((s) => <option key={s} value={s}>{STATUS_LABELS[s]}</option>)}
                      </select>
                      <button onClick={() => handleDelete(t.id)}
                        className="text-xs text-critical hover:text-critical/80">Delete</button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      <Modal open={showCreate} onClose={() => setShowCreate(false)} title="Add Task">
        <TaskForm onSubmit={handleCreate} contacts={contacts} />
      </Modal>
    </div>
  );
}
