import { useEffect, useState, useCallback } from 'react';
import { PlusIcon, PhoneIcon, EnvelopeIcon, CalendarIcon, DocumentTextIcon } from '@heroicons/react/24/outline';
import { api } from '../lib/api';
import Modal from '../components/Modal';
import { toast } from '../components/Toast';

const TYPES = ['email', 'call', 'meeting', 'note'];
const TYPE_ICONS = {
  email: EnvelopeIcon,
  call: PhoneIcon,
  meeting: CalendarIcon,
  note: DocumentTextIcon,
};
const TYPE_COLOURS = {
  email: 'text-gold bg-gold/10',
  call: 'text-healthy bg-healthy/10',
  meeting: 'text-purple bg-purple/10',
  note: 'text-text-secondary bg-surface-light',
};

function InteractionForm({ onSubmit, contacts }) {
  const [form, setForm] = useState({
    contact_id: '', type: 'email', subject: '', content: '',
    channel: '', duration_minutes: '', occurred_at: '',
  });
  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }));
  const cls = 'bg-midnight border border-border rounded-lg px-3 py-2 text-sm text-text-primary placeholder-text-muted focus:outline-none focus:border-gold';

  return (
    <form onSubmit={(e) => {
      e.preventDefault();
      const payload = { ...form };
      if (!payload.contact_id) { toast('Contact is required', 'error'); return; }
      if (!payload.subject) delete payload.subject;
      if (!payload.content) delete payload.content;
      if (!payload.channel) delete payload.channel;
      if (payload.duration_minutes) payload.duration_minutes = parseInt(payload.duration_minutes);
      else delete payload.duration_minutes;
      if (!payload.occurred_at) delete payload.occurred_at;
      onSubmit(payload);
    }} className="space-y-3">
      <select value={form.contact_id} onChange={set('contact_id')} required className={`w-full ${cls}`}>
        <option value="">Select contact *</option>
        {contacts.map((c) => (
          <option key={c.id} value={c.id}>{c.first_name} {c.last_name}</option>
        ))}
      </select>
      <div className="grid grid-cols-2 gap-3">
        <select value={form.type} onChange={set('type')} className={cls}>
          {TYPES.map((t) => <option key={t} value={t}>{t.charAt(0).toUpperCase() + t.slice(1)}</option>)}
        </select>
        <input placeholder="Channel" value={form.channel} onChange={set('channel')} className={cls} />
      </div>
      <input placeholder="Subject" value={form.subject} onChange={set('subject')} className={`w-full ${cls}`} />
      <textarea placeholder="Content / notes" value={form.content} onChange={set('content')} rows={3} className={`w-full ${cls}`} />
      <div className="grid grid-cols-2 gap-3">
        <input placeholder="Duration (min)" type="number" min="0" value={form.duration_minutes} onChange={set('duration_minutes')} className={cls} />
        <input type="datetime-local" value={form.occurred_at} onChange={set('occurred_at')} className={cls} />
      </div>
      <button type="submit"
        className="w-full bg-gold hover:bg-gold-light text-midnight font-medium py-2 rounded-lg text-sm transition-colors">
        Log Interaction
      </button>
    </form>
  );
}

function TimelineItem({ interaction }) {
  const Icon = TYPE_ICONS[interaction.type] || DocumentTextIcon;
  const colour = TYPE_COLOURS[interaction.type] || 'text-text-muted bg-surface-light';
  const dt = new Date(interaction.occurred_at);

  return (
    <div className="flex gap-4 group">
      <div className="flex flex-col items-center">
        <div className={`w-8 h-8 rounded-full flex items-center justify-center ${colour}`}>
          <Icon className="w-4 h-4" />
        </div>
        <div className="w-px flex-1 bg-border mt-1" />
      </div>
      <div className="pb-6 flex-1">
        <div className="flex items-baseline justify-between">
          <h4 className="text-sm font-medium text-text-primary">
            {interaction.subject || `${interaction.type.charAt(0).toUpperCase() + interaction.type.slice(1)}`}
          </h4>
          <span className="text-xs text-text-muted shrink-0 ml-2">
            {dt.toLocaleDateString('en-AU', { day: 'numeric', month: 'short', year: 'numeric' })}
            {' '}
            {dt.toLocaleTimeString('en-AU', { hour: '2-digit', minute: '2-digit' })}
          </span>
        </div>
        {interaction.content && (
          <p className="text-sm text-text-secondary mt-1 line-clamp-3">{interaction.content}</p>
        )}
        <div className="flex gap-3 mt-1">
          {interaction.channel && <span className="text-xs text-text-muted">via {interaction.channel}</span>}
          {interaction.duration_minutes != null && (
            <span className="text-xs text-text-muted">{interaction.duration_minutes} min</span>
          )}
          {interaction.sentiment_score != null && (
            <span className={`text-xs ${interaction.sentiment_score >= 0.3 ? 'text-healthy' : interaction.sentiment_score <= -0.3 ? 'text-critical' : 'text-text-muted'}`}>
              sentiment: {interaction.sentiment_score.toFixed(1)}
            </span>
          )}
        </div>
      </div>
    </div>
  );
}

export default function Interactions() {
  const [interactions, setInteractions] = useState([]);
  const [contacts, setContacts] = useState([]);
  const [total, setTotal] = useState(0);
  const [typeFilter, setTypeFilter] = useState('');
  const [showCreate, setShowCreate] = useState(false);
  const [loading, setLoading] = useState(true);

  const fetchInteractions = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({ page_size: '100' });
      if (typeFilter) params.set('type', typeFilter);
      const data = await api.get(`/interactions?${params}`);
      setInteractions(data.items);
      setTotal(data.total);
    } catch (err) {
      toast(err.message, 'error');
    } finally {
      setLoading(false);
    }
  }, [typeFilter]);

  const fetchContacts = useCallback(async () => {
    try {
      const data = await api.get('/contacts?page_size=200');
      setContacts(data.items);
    } catch { /* ignore */ }
  }, []);

  useEffect(() => { fetchInteractions(); }, [fetchInteractions]);
  useEffect(() => { fetchContacts(); }, [fetchContacts]);

  const handleCreate = async (form) => {
    try {
      await api.post('/interactions', form);
      toast('Interaction logged');
      setShowCreate(false);
      fetchInteractions();
    } catch (err) {
      toast(err.message, 'error');
    }
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="font-heading text-2xl font-semibold">Interactions</h1>
          <p className="text-text-secondary text-sm mt-1">{total} interaction{total !== 1 ? 's' : ''}</p>
        </div>
        <button onClick={() => setShowCreate(true)}
          className="flex items-center gap-2 bg-gold hover:bg-gold-light text-midnight font-medium px-4 py-2 rounded-lg text-sm transition-colors">
          <PlusIcon className="w-4 h-4" /> Log Interaction
        </button>
      </div>

      <div className="flex gap-2 mb-4">
        <button onClick={() => setTypeFilter('')}
          className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${!typeFilter ? 'bg-gold text-midnight' : 'bg-surface border border-border text-text-secondary hover:text-text-primary'}`}>
          All
        </button>
        {TYPES.map((t) => (
          <button key={t} onClick={() => setTypeFilter(t)}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${typeFilter === t ? 'bg-gold text-midnight' : 'bg-surface border border-border text-text-secondary hover:text-text-primary'}`}>
            {t.charAt(0).toUpperCase() + t.slice(1)}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="text-text-muted text-sm py-8 text-center">Loading interactions...</div>
      ) : interactions.length === 0 ? (
        <div className="text-center py-12 text-text-secondary">
          <p className="text-lg mb-2">No interactions yet</p>
          <p className="text-sm">Log your first interaction to start building the timeline.</p>
        </div>
      ) : (
        <div className="bg-surface border border-border rounded-xl p-6">
          {interactions.map((i) => (
            <TimelineItem key={i.id} interaction={i} />
          ))}
        </div>
      )}

      <Modal open={showCreate} onClose={() => setShowCreate(false)} title="Log Interaction">
        <InteractionForm onSubmit={handleCreate} contacts={contacts} />
      </Modal>
    </div>
  );
}
