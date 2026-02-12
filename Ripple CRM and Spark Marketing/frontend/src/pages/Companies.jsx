import { useEffect, useState, useCallback } from 'react';
import { MagnifyingGlassIcon, PlusIcon, PencilIcon, TrashIcon, XMarkIcon } from '@heroicons/react/24/outline';
import { api } from '../lib/api';
import { useDebounce } from '../lib/useDebounce';
import Modal from '../components/Modal';
import { toast } from '../components/Toast';

function CompanyForm({ onSubmit, initial = {}, submitLabel = 'Create' }) {
  const [form, setForm] = useState({
    name: '', trading_name: '', abn: '', industry: '',
    website: '', address: '', city: '', state: '', postcode: '', country: 'Australia',
    ...initial,
  });

  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }));

  return (
    <form onSubmit={(e) => { e.preventDefault(); onSubmit(form); }} className="space-y-3">
      <input placeholder="Company name *" required value={form.name} onChange={set('name')}
        className="w-full bg-midnight border border-border rounded-lg px-3 py-2 text-sm text-text-primary placeholder-text-muted focus:outline-none focus:border-gold" />
      <div className="grid grid-cols-2 gap-3">
        <input placeholder="Trading name" value={form.trading_name} onChange={set('trading_name')}
          className="bg-midnight border border-border rounded-lg px-3 py-2 text-sm text-text-primary placeholder-text-muted focus:outline-none focus:border-gold" />
        <input placeholder="ABN" value={form.abn} onChange={set('abn')}
          className="bg-midnight border border-border rounded-lg px-3 py-2 text-sm text-text-primary placeholder-text-muted focus:outline-none focus:border-gold" />
      </div>
      <div className="grid grid-cols-2 gap-3">
        <input placeholder="Industry" value={form.industry} onChange={set('industry')}
          className="bg-midnight border border-border rounded-lg px-3 py-2 text-sm text-text-primary placeholder-text-muted focus:outline-none focus:border-gold" />
        <input placeholder="Website" value={form.website} onChange={set('website')}
          className="bg-midnight border border-border rounded-lg px-3 py-2 text-sm text-text-primary placeholder-text-muted focus:outline-none focus:border-gold" />
      </div>
      <input placeholder="Address" value={form.address} onChange={set('address')}
        className="w-full bg-midnight border border-border rounded-lg px-3 py-2 text-sm text-text-primary placeholder-text-muted focus:outline-none focus:border-gold" />
      <div className="grid grid-cols-3 gap-3">
        <input placeholder="City" value={form.city} onChange={set('city')}
          className="bg-midnight border border-border rounded-lg px-3 py-2 text-sm text-text-primary placeholder-text-muted focus:outline-none focus:border-gold" />
        <input placeholder="State" value={form.state} onChange={set('state')}
          className="bg-midnight border border-border rounded-lg px-3 py-2 text-sm text-text-primary placeholder-text-muted focus:outline-none focus:border-gold" />
        <input placeholder="Postcode" value={form.postcode} onChange={set('postcode')}
          className="bg-midnight border border-border rounded-lg px-3 py-2 text-sm text-text-primary placeholder-text-muted focus:outline-none focus:border-gold" />
      </div>
      <button type="submit"
        className="w-full bg-gold hover:bg-gold-light text-midnight font-medium py-2 rounded-lg text-sm transition-colors">
        {submitLabel}
      </button>
    </form>
  );
}

export default function Companies() {
  const [companies, setCompanies] = useState([]);
  const [total, setTotal] = useState(0);
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [showCreate, setShowCreate] = useState(false);
  const [editing, setEditing] = useState(null);
  const [loading, setLoading] = useState(true);
  const debouncedSearch = useDebounce(search, 300);

  const fetchCompanies = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({ page, page_size: 50 });
      if (debouncedSearch) params.set('search', debouncedSearch);
      const data = await api.get(`/companies?${params}`);
      setCompanies(data.items);
      setTotal(data.total);
    } catch (err) {
      toast(err.message, 'error');
    } finally {
      setLoading(false);
    }
  }, [debouncedSearch, page]);

  useEffect(() => { fetchCompanies(); }, [fetchCompanies]);

  const handleCreate = async (form) => {
    try {
      await api.post('/companies', form);
      toast('Company created');
      setShowCreate(false);
      fetchCompanies();
    } catch (err) {
      toast(err.message, 'error');
    }
  };

  const handleUpdate = async (form) => {
    try {
      await api.put(`/companies/${editing.id}`, form);
      toast('Company updated');
      setEditing(null);
      fetchCompanies();
    } catch (err) {
      toast(err.message, 'error');
    }
  };

  const handleDelete = async (id) => {
    if (!confirm('Delete this company?')) return;
    try {
      await api.delete(`/companies/${id}`);
      toast('Company deleted');
      fetchCompanies();
    } catch (err) {
      toast(err.message, 'error');
    }
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="font-heading text-2xl font-semibold">Companies</h1>
          <p className="text-text-secondary text-sm mt-1">{total} compan{total !== 1 ? 'ies' : 'y'}</p>
        </div>
        <button onClick={() => setShowCreate(true)}
          className="flex items-center gap-2 bg-gold hover:bg-gold-light text-midnight font-medium px-4 py-2 rounded-lg text-sm transition-colors">
          <PlusIcon className="w-4 h-4" /> Add Company
        </button>
      </div>

      <div className="relative mb-4">
        <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted" />
        <input placeholder="Search companies..." value={search} onChange={(e) => { setSearch(e.target.value); setPage(1); }}
          className="w-full bg-surface border border-border rounded-lg pl-9 pr-3 py-2 text-sm text-text-primary placeholder-text-muted focus:outline-none focus:border-gold" />
      </div>

      {loading ? (
        <div className="text-text-muted text-sm py-8 text-center">Loading companies...</div>
      ) : companies.length === 0 ? (
        <div className="text-center py-12 text-text-secondary">
          <p className="text-lg mb-2">No companies yet</p>
          <p className="text-sm">Add your first company to get started.</p>
        </div>
      ) : (
        <div className="bg-surface border border-border rounded-xl overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border text-text-muted text-xs uppercase tracking-wider">
                <th className="text-left px-4 py-3">Name</th>
                <th className="text-left px-4 py-3">ABN</th>
                <th className="text-left px-4 py-3">Industry</th>
                <th className="text-left px-4 py-3">Location</th>
                <th className="text-left px-4 py-3">Health</th>
                <th className="text-right px-4 py-3">Actions</th>
              </tr>
            </thead>
            <tbody>
              {companies.map((c) => (
                <tr key={c.id} className="border-b border-border hover:bg-surface-light transition-colors">
                  <td className="px-4 py-3 font-medium text-text-primary">{c.name}</td>
                  <td className="px-4 py-3 text-text-secondary font-mono text-xs">{c.abn || '—'}</td>
                  <td className="px-4 py-3 text-text-secondary">{c.industry || '—'}</td>
                  <td className="px-4 py-3 text-text-secondary">
                    {[c.city, c.state].filter(Boolean).join(', ') || '—'}
                  </td>
                  <td className="px-4 py-3 text-text-muted text-xs">
                    {c.account_health_score != null ? Math.round(c.account_health_score) : '—'}
                  </td>
                  <td className="px-4 py-3 text-right">
                    <button onClick={() => setEditing(c)} className="p-1 hover:bg-surface-light rounded text-text-secondary">
                      <PencilIcon className="w-4 h-4" />
                    </button>
                    <button onClick={() => handleDelete(c.id)} className="p-1 hover:bg-critical/10 rounded text-critical ml-1">
                      <TrashIcon className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <Modal open={showCreate} onClose={() => setShowCreate(false)} title="Add Company">
        <CompanyForm onSubmit={handleCreate} />
      </Modal>

      <Modal open={!!editing} onClose={() => setEditing(null)} title="Edit Company">
        {editing && <CompanyForm onSubmit={handleUpdate} initial={editing} submitLabel="Update" />}
      </Modal>
    </div>
  );
}
