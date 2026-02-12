import { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { MagnifyingGlassIcon, PlusIcon } from '@heroicons/react/24/outline';
import { api } from '../lib/api';
import { useDebounce } from '../lib/useDebounce';
import Modal from '../components/Modal';
import { toast } from '../components/Toast';

const CONTACT_TYPES = ['lead', 'contact', 'customer'];

function ContactForm({ onSubmit, initial = {}, submitLabel = 'Create' }) {
  const [form, setForm] = useState({
    first_name: '', last_name: '', email: '', phone: '',
    role: '', title: '', type: 'lead', source: '',
    linkedin_url: '', preferred_channel: '', notes: '', timezone: '',
    ...initial,
  });

  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }));

  return (
    <form onSubmit={(e) => { e.preventDefault(); onSubmit(form); }} className="space-y-3">
      <div className="grid grid-cols-2 gap-3">
        <input placeholder="First name *" required value={form.first_name} onChange={set('first_name')}
          className="bg-midnight border border-border rounded-lg px-3 py-2 text-sm text-text-primary placeholder-text-muted focus:outline-none focus:border-gold" />
        <input placeholder="Last name *" required value={form.last_name} onChange={set('last_name')}
          className="bg-midnight border border-border rounded-lg px-3 py-2 text-sm text-text-primary placeholder-text-muted focus:outline-none focus:border-gold" />
      </div>
      <div className="grid grid-cols-2 gap-3">
        <input placeholder="Email" type="email" value={form.email} onChange={set('email')}
          className="bg-midnight border border-border rounded-lg px-3 py-2 text-sm text-text-primary placeholder-text-muted focus:outline-none focus:border-gold" />
        <input placeholder="Phone" value={form.phone} onChange={set('phone')}
          className="bg-midnight border border-border rounded-lg px-3 py-2 text-sm text-text-primary placeholder-text-muted focus:outline-none focus:border-gold" />
      </div>
      <div className="grid grid-cols-2 gap-3">
        <input placeholder="Role" value={form.role} onChange={set('role')}
          className="bg-midnight border border-border rounded-lg px-3 py-2 text-sm text-text-primary placeholder-text-muted focus:outline-none focus:border-gold" />
        <select value={form.type} onChange={set('type')}
          className="bg-midnight border border-border rounded-lg px-3 py-2 text-sm text-text-primary focus:outline-none focus:border-gold">
          {CONTACT_TYPES.map((t) => <option key={t} value={t}>{t.charAt(0).toUpperCase() + t.slice(1)}</option>)}
        </select>
      </div>
      <div className="grid grid-cols-2 gap-3">
        <input placeholder="Source" value={form.source} onChange={set('source')}
          className="bg-midnight border border-border rounded-lg px-3 py-2 text-sm text-text-primary placeholder-text-muted focus:outline-none focus:border-gold" />
        <input placeholder="LinkedIn URL" value={form.linkedin_url} onChange={set('linkedin_url')}
          className="bg-midnight border border-border rounded-lg px-3 py-2 text-sm text-text-primary placeholder-text-muted focus:outline-none focus:border-gold" />
      </div>
      <textarea placeholder="Notes" value={form.notes} onChange={set('notes')} rows={2}
        className="w-full bg-midnight border border-border rounded-lg px-3 py-2 text-sm text-text-primary placeholder-text-muted focus:outline-none focus:border-gold" />
      <button type="submit"
        className="w-full bg-gold hover:bg-gold-light text-midnight font-medium py-2 rounded-lg text-sm transition-colors">
        {submitLabel}
      </button>
    </form>
  );
}

function healthBadge(score) {
  if (score == null) return <span className="text-text-muted text-xs">—</span>;
  const colour = score >= 70 ? 'text-healthy' : score >= 40 ? 'text-warning' : 'text-critical';
  const label = score >= 70 ? 'Healthy' : score >= 40 ? 'Warning' : 'Critical';
  return <span className={`text-xs font-medium ${colour}`}>{Math.round(score)} ({label})</span>;
}

export default function Contacts() {
  const [contacts, setContacts] = useState([]);
  const [total, setTotal] = useState(0);
  const [search, setSearch] = useState('');
  const [typeFilter, setTypeFilter] = useState('');
  const [page, setPage] = useState(1);
  const [showCreate, setShowCreate] = useState(false);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  const debouncedSearch = useDebounce(search, 300);

  const fetchContacts = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({ page, page_size: 50 });
      if (debouncedSearch) params.set('search', debouncedSearch);
      if (typeFilter) params.set('type', typeFilter);
      const data = await api.get(`/contacts?${params}`);
      setContacts(data.items);
      setTotal(data.total);
    } catch (err) {
      toast(err.message, 'error');
    } finally {
      setLoading(false);
    }
  }, [debouncedSearch, typeFilter, page]);

  useEffect(() => { fetchContacts(); }, [fetchContacts]);

  const handleCreate = async (form) => {
    try {
      await api.post('/contacts', form);
      toast('Contact created');
      setShowCreate(false);
      fetchContacts();
    } catch (err) {
      toast(err.message, 'error');
    }
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="font-heading text-2xl font-semibold">Contacts</h1>
          <p className="text-text-secondary text-sm mt-1">{total} contact{total !== 1 ? 's' : ''}</p>
        </div>
        <button onClick={() => setShowCreate(true)}
          className="flex items-center gap-2 bg-gold hover:bg-gold-light text-midnight font-medium px-4 py-2 rounded-lg text-sm transition-colors">
          <PlusIcon className="w-4 h-4" /> Add Contact
        </button>
      </div>

      <div className="flex gap-3 mb-4">
        <div className="relative flex-1">
          <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted" />
          <input placeholder="Search contacts..." value={search} onChange={(e) => { setSearch(e.target.value); setPage(1); }}
            className="w-full bg-surface border border-border rounded-lg pl-9 pr-3 py-2 text-sm text-text-primary placeholder-text-muted focus:outline-none focus:border-gold" />
        </div>
        <select value={typeFilter} onChange={(e) => { setTypeFilter(e.target.value); setPage(1); }}
          className="bg-surface border border-border rounded-lg px-3 py-2 text-sm text-text-primary focus:outline-none focus:border-gold">
          <option value="">All types</option>
          {CONTACT_TYPES.map((t) => <option key={t} value={t}>{t.charAt(0).toUpperCase() + t.slice(1)}</option>)}
        </select>
      </div>

      {loading ? (
        <div className="text-text-muted text-sm py-8 text-center">Loading contacts...</div>
      ) : contacts.length === 0 ? (
        <div className="text-center py-12 text-text-secondary">
          <p className="text-lg mb-2">No contacts yet</p>
          <p className="text-sm">Add your first contact to get started.</p>
        </div>
      ) : (
        <div className="bg-surface border border-border rounded-xl overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border text-text-muted text-xs uppercase tracking-wider">
                <th className="text-left px-4 py-3">Name</th>
                <th className="text-left px-4 py-3">Email</th>
                <th className="text-left px-4 py-3">Role</th>
                <th className="text-left px-4 py-3">Type</th>
                <th className="text-left px-4 py-3">Health</th>
                <th className="text-left px-4 py-3">Source</th>
              </tr>
            </thead>
            <tbody>
              {contacts.map((c) => (
                <tr key={c.id} onClick={() => navigate(`/contacts/${c.id}`)}
                  className="border-b border-border hover:bg-surface-light cursor-pointer transition-colors">
                  <td className="px-4 py-3 font-medium text-text-primary">{c.first_name} {c.last_name}</td>
                  <td className="px-4 py-3 text-text-secondary">{c.email || '—'}</td>
                  <td className="px-4 py-3 text-text-secondary">{c.role || '—'}</td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                      c.type === 'customer' ? 'bg-healthy/10 text-healthy' :
                      c.type === 'contact' ? 'bg-gold/10 text-gold' :
                      'bg-surface-light text-text-secondary'
                    }`}>{c.type}</span>
                  </td>
                  <td className="px-4 py-3">{healthBadge(c.relationship_health_score)}</td>
                  <td className="px-4 py-3 text-text-muted">{c.source || '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {total > 50 && (
        <div className="flex justify-center gap-2 mt-4">
          <button onClick={() => setPage((p) => Math.max(1, p - 1))} disabled={page === 1}
            className="px-3 py-1 bg-surface border border-border rounded text-sm disabled:opacity-50">Previous</button>
          <span className="px-3 py-1 text-sm text-text-secondary">Page {page}</span>
          <button onClick={() => setPage((p) => p + 1)} disabled={contacts.length < 50}
            className="px-3 py-1 bg-surface border border-border rounded text-sm disabled:opacity-50">Next</button>
        </div>
      )}

      <Modal open={showCreate} onClose={() => setShowCreate(false)} title="Add Contact">
        <ContactForm onSubmit={handleCreate} />
      </Modal>
    </div>
  );
}
