import { useEffect, useState, useCallback } from 'react';
import { PlusIcon, ExclamationTriangleIcon } from '@heroicons/react/24/outline';
import { api } from '../lib/api';
import Modal from '../components/Modal';
import { toast } from '../components/Toast';

const STATUS_OPTIONS = ['pending', 'fulfilled', 'broken'];
const STATUS_COLOURS = {
  pending: 'bg-warning/10 text-warning',
  fulfilled: 'bg-healthy/10 text-healthy',
  broken: 'bg-critical/10 text-critical',
};

function CommitmentForm({ onSubmit, contacts }) {
  const [form, setForm] = useState({
    description: '', committed_by: 'us', due_date: '',
    contact_id: '', status: 'pending',
  });
  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }));
  const cls = 'bg-midnight border border-border rounded-lg px-3 py-2 text-sm text-text-primary placeholder-text-muted focus:outline-none focus:border-gold';

  return (
    <form onSubmit={(e) => {
      e.preventDefault();
      const payload = { ...form };
      if (!payload.due_date) delete payload.due_date;
      if (!payload.contact_id) delete payload.contact_id;
      onSubmit(payload);
    }} className="space-y-3">
      <textarea placeholder="What was promised? *" required value={form.description} onChange={set('description')} rows={2} className={`w-full ${cls}`} />
      <div className="grid grid-cols-2 gap-3">
        <select value={form.committed_by} onChange={set('committed_by')} className={cls}>
          <option value="us">We promised</option>
          <option value="them">They promised</option>
        </select>
        <input type="date" placeholder="Due date" value={form.due_date} onChange={set('due_date')} className={cls} />
      </div>
      <select value={form.contact_id} onChange={set('contact_id')} className={`w-full ${cls}`}>
        <option value="">Link to contact (optional)</option>
        {contacts.map((c) => (
          <option key={c.id} value={c.id}>{c.first_name} {c.last_name}</option>
        ))}
      </select>
      <button type="submit"
        className="w-full bg-gold hover:bg-gold-light text-midnight font-medium py-2 rounded-lg text-sm transition-colors">
        Add Commitment
      </button>
    </form>
  );
}

export default function Commitments() {
  const [commitments, setCommitments] = useState([]);
  const [contacts, setContacts] = useState([]);
  const [total, setTotal] = useState(0);
  const [statusFilter, setStatusFilter] = useState('');
  const [showOverdue, setShowOverdue] = useState(false);
  const [showCreate, setShowCreate] = useState(false);
  const [loading, setLoading] = useState(true);

  const fetchCommitments = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({ page_size: '100' });
      if (statusFilter) params.set('status', statusFilter);
      if (showOverdue) params.set('overdue', 'true');
      const data = await api.get(`/commitments?${params}`);
      setCommitments(data.items);
      setTotal(data.total);
    } catch (err) {
      toast(err.message, 'error');
    } finally {
      setLoading(false);
    }
  }, [statusFilter, showOverdue]);

  const fetchContacts = useCallback(async () => {
    try {
      const data = await api.get('/contacts?page_size=200');
      setContacts(data.items);
    } catch { /* ignore */ }
  }, []);

  useEffect(() => { fetchCommitments(); }, [fetchCommitments]);
  useEffect(() => { fetchContacts(); }, [fetchContacts]);

  const handleCreate = async (form) => {
    try {
      await api.post('/commitments', form);
      toast('Commitment added');
      setShowCreate(false);
      fetchCommitments();
    } catch (err) {
      toast(err.message, 'error');
    }
  };

  const handleStatusChange = async (id, newStatus) => {
    try {
      await api.put(`/commitments/${id}`, { status: newStatus });
      toast(`Marked as ${newStatus}`);
      fetchCommitments();
    } catch (err) {
      toast(err.message, 'error');
    }
  };

  const overdueCount = commitments.filter((c) => c.is_overdue).length;

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="font-heading text-2xl font-semibold">Commitments</h1>
          <p className="text-text-secondary text-sm mt-1">
            {total} commitment{total !== 1 ? 's' : ''}
            {overdueCount > 0 && (
              <span className="text-critical ml-2">
                <ExclamationTriangleIcon className="w-3 h-3 inline mr-0.5" />
                {overdueCount} overdue
              </span>
            )}
          </p>
        </div>
        <button onClick={() => setShowCreate(true)}
          className="flex items-center gap-2 bg-gold hover:bg-gold-light text-midnight font-medium px-4 py-2 rounded-lg text-sm transition-colors">
          <PlusIcon className="w-4 h-4" /> Add Commitment
        </button>
      </div>

      <div className="flex gap-2 mb-4 flex-wrap">
        <button onClick={() => { setStatusFilter(''); setShowOverdue(false); }}
          className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${!statusFilter && !showOverdue ? 'bg-gold text-midnight' : 'bg-surface border border-border text-text-secondary'}`}>
          All
        </button>
        {STATUS_OPTIONS.map((s) => (
          <button key={s} onClick={() => { setStatusFilter(s); setShowOverdue(false); }}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${statusFilter === s ? 'bg-gold text-midnight' : 'bg-surface border border-border text-text-secondary'}`}>
            {s.charAt(0).toUpperCase() + s.slice(1)}
          </button>
        ))}
        <button onClick={() => { setStatusFilter(''); setShowOverdue(!showOverdue); }}
          className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${showOverdue ? 'bg-critical text-white' : 'bg-surface border border-border text-critical'}`}>
          Overdue Only
        </button>
      </div>

      {loading ? (
        <div className="text-text-muted text-sm py-8 text-center">Loading commitments...</div>
      ) : commitments.length === 0 ? (
        <div className="text-center py-12 text-text-secondary">
          <p className="text-lg mb-2">No commitments yet</p>
          <p className="text-sm">Track promises — both yours and theirs — to build trust.</p>
        </div>
      ) : (
        <div className="bg-surface border border-border rounded-xl overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border text-text-muted text-xs uppercase tracking-wider">
                <th className="text-left px-4 py-3">Promise</th>
                <th className="text-left px-4 py-3">By</th>
                <th className="text-left px-4 py-3">Due</th>
                <th className="text-left px-4 py-3">Status</th>
                <th className="text-right px-4 py-3">Actions</th>
              </tr>
            </thead>
            <tbody>
              {commitments.map((c) => (
                <tr key={c.id} className={`border-b border-border transition-colors ${c.is_overdue ? 'bg-critical/5' : 'hover:bg-surface-light'}`}>
                  <td className="px-4 py-3 text-text-primary">
                    <span className="font-medium">{c.description}</span>
                    {c.is_overdue && (
                      <span className="ml-2 inline-flex items-center gap-0.5 text-critical text-xs">
                        <ExclamationTriangleIcon className="w-3 h-3" /> Overdue
                      </span>
                    )}
                  </td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${c.committed_by === 'us' ? 'bg-gold/10 text-gold' : 'bg-purple/10 text-purple'}`}>
                      {c.committed_by === 'us' ? 'We promised' : 'They promised'}
                    </span>
                  </td>
                  <td className={`px-4 py-3 text-xs ${c.is_overdue ? 'text-critical font-medium' : 'text-text-secondary'}`}>
                    {c.due_date || '—'}
                  </td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${STATUS_COLOURS[c.status]}`}>
                      {c.status}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-right">
                    {c.status === 'pending' && (
                      <div className="flex gap-1 justify-end">
                        <button onClick={() => handleStatusChange(c.id, 'fulfilled')}
                          className="text-xs px-2 py-1 bg-healthy/10 text-healthy rounded hover:bg-healthy/20">
                          Fulfilled
                        </button>
                        <button onClick={() => handleStatusChange(c.id, 'broken')}
                          className="text-xs px-2 py-1 bg-critical/10 text-critical rounded hover:bg-critical/20">
                          Broken
                        </button>
                      </div>
                    )}
                    {c.fulfilled_at && (
                      <span className="text-xs text-text-muted">
                        {new Date(c.fulfilled_at).toLocaleDateString('en-AU')}
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <Modal open={showCreate} onClose={() => setShowCreate(false)} title="Add Commitment">
        <CommitmentForm onSubmit={handleCreate} contacts={contacts} />
      </Modal>
    </div>
  );
}
