import { useEffect, useState, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeftIcon, PencilIcon, TrashIcon, PlusIcon, PhoneIcon, EnvelopeIcon, CalendarIcon, DocumentTextIcon } from '@heroicons/react/24/outline';
import { api } from '../lib/api';
import Modal from '../components/Modal';
import { toast } from '../components/Toast';

const TYPE_ICONS = { email: EnvelopeIcon, call: PhoneIcon, meeting: CalendarIcon, note: DocumentTextIcon };
const TYPE_COLOURS = { email: 'text-gold bg-gold/10', call: 'text-healthy bg-healthy/10', meeting: 'text-purple bg-purple/10', note: 'text-text-secondary bg-surface-light' };

function Field({ label, value, editing, name, onChange }) {
  return (
    <div>
      <label className="text-xs text-text-muted uppercase tracking-wider">{label}</label>
      {editing ? (
        <input value={value || ''} onChange={(e) => onChange(name, e.target.value)}
          className="w-full bg-midnight border border-border rounded px-2 py-1.5 text-sm text-text-primary mt-1 focus:outline-none focus:border-gold" />
      ) : (
        <p className="text-sm text-text-primary mt-1">{value || '—'}</p>
      )}
    </div>
  );
}

export default function ContactDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [contact, setContact] = useState(null);
  const [editing, setEditing] = useState(false);
  const [editData, setEditData] = useState({});
  const [loading, setLoading] = useState(true);
  const [timeline, setTimeline] = useState([]);
  const [notes, setNotes] = useState([]);
  const [newNote, setNewNote] = useState('');
  const [showLogInteraction, setShowLogInteraction] = useState(false);
  const [interactionForm, setInteractionForm] = useState({ type: 'email', subject: '', content: '', channel: '', duration_minutes: '' });

  useEffect(() => {
    api.get(`/contacts/${id}`)
      .then((c) => { setContact(c); setEditData(c); setLoading(false); })
      .catch(() => { toast('Contact not found', 'error'); navigate('/contacts'); });
  }, [id, navigate]);

  const fetchTimeline = useCallback(async () => {
    try {
      const data = await api.get(`/contacts/${id}/interactions?page_size=50`);
      setTimeline(data.items);
    } catch { /* ignore */ }
  }, [id]);

  const fetchNotes = useCallback(async () => {
    try {
      const data = await api.get(`/notes?contact_id=${id}&page_size=50`);
      setNotes(data.items);
    } catch { /* ignore */ }
  }, [id]);

  useEffect(() => { fetchTimeline(); fetchNotes(); }, [fetchTimeline, fetchNotes]);

  const handleFieldChange = (name, value) => {
    setEditData((d) => ({ ...d, [name]: value }));
  };

  const handleSave = async () => {
    try {
      const updated = await api.put(`/contacts/${id}`, editData);
      setContact(updated);
      setEditData(updated);
      setEditing(false);
      toast('Contact updated');
    } catch (err) {
      toast(err.message, 'error');
    }
  };

  const handleDelete = async () => {
    if (!confirm('Delete this contact? This action cannot be undone.')) return;
    try {
      await api.delete(`/contacts/${id}`);
      toast('Contact deleted');
      navigate('/contacts');
    } catch (err) {
      toast(err.message, 'error');
    }
  };

  if (loading) return <div className="text-text-muted py-8 text-center">Loading...</div>;
  if (!contact) return null;

  const healthScore = contact.relationship_health_score;
  const healthColour = healthScore == null ? 'text-text-muted' : healthScore >= 70 ? 'text-healthy' : healthScore >= 40 ? 'text-warning' : 'text-critical';
  const healthLabel = healthScore == null ? 'Not scored' : healthScore >= 70 ? 'Healthy' : healthScore >= 40 ? 'Warning' : 'Critical';

  return (
    <div>
      <button onClick={() => navigate('/contacts')} className="flex items-center gap-1 text-text-secondary text-sm hover:text-text-primary mb-4">
        <ArrowLeftIcon className="w-4 h-4" /> Back to Contacts
      </button>

      <div className="bg-surface border border-border rounded-xl p-6 mb-6">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="font-heading text-2xl font-semibold">
              {contact.first_name} {contact.last_name}
            </h1>
            <div className="flex items-center gap-3 mt-2">
              {contact.role && <span className="text-text-secondary text-sm">{contact.role}</span>}
              <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                contact.type === 'customer' ? 'bg-healthy/10 text-healthy' :
                contact.type === 'contact' ? 'bg-gold/10 text-gold' :
                'bg-surface-light text-text-secondary'
              }`}>{contact.type}</span>
              <span className={`text-xs font-medium ${healthColour}`}>
                {healthScore != null && `${Math.round(healthScore)} — `}{healthLabel}
              </span>
              {contact.trust_decay_days != null && (
                <span className="text-xs text-warning">
                  {contact.trust_decay_days}d since last interaction
                </span>
              )}
            </div>
          </div>
          <div className="flex gap-2">
            {editing ? (
              <>
                <button onClick={handleSave}
                  className="px-3 py-1.5 bg-gold text-midnight text-sm font-medium rounded-lg">Save</button>
                <button onClick={() => { setEditing(false); setEditData(contact); }}
                  className="px-3 py-1.5 bg-surface-light text-text-secondary text-sm rounded-lg">Cancel</button>
              </>
            ) : (
              <>
                <button onClick={() => setEditing(true)}
                  className="p-2 hover:bg-surface-light rounded-lg text-text-secondary"><PencilIcon className="w-4 h-4" /></button>
                <button onClick={handleDelete}
                  className="p-2 hover:bg-critical/10 rounded-lg text-critical"><TrashIcon className="w-4 h-4" /></button>
              </>
            )}
          </div>
        </div>
      </div>

      <div className="bg-surface border border-border rounded-xl p-6 mb-6">
        <h2 className="font-heading text-lg font-semibold mb-4">Details</h2>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          <Field label="First Name" value={editing ? editData.first_name : contact.first_name}
            editing={editing} name="first_name" onChange={handleFieldChange} />
          <Field label="Last Name" value={editing ? editData.last_name : contact.last_name}
            editing={editing} name="last_name" onChange={handleFieldChange} />
          <Field label="Email" value={editing ? editData.email : contact.email}
            editing={editing} name="email" onChange={handleFieldChange} />
          <Field label="Phone" value={editing ? editData.phone : contact.phone}
            editing={editing} name="phone" onChange={handleFieldChange} />
          <Field label="Role" value={editing ? editData.role : contact.role}
            editing={editing} name="role" onChange={handleFieldChange} />
          <Field label="Source" value={editing ? editData.source : contact.source}
            editing={editing} name="source" onChange={handleFieldChange} />
          <Field label="LinkedIn" value={editing ? editData.linkedin_url : contact.linkedin_url}
            editing={editing} name="linkedin_url" onChange={handleFieldChange} />
          <Field label="Timezone" value={editing ? editData.timezone : contact.timezone}
            editing={editing} name="timezone" onChange={handleFieldChange} />
          <Field label="Preferred Channel" value={editing ? editData.preferred_channel : contact.preferred_channel}
            editing={editing} name="preferred_channel" onChange={handleFieldChange} />
        </div>
      </div>

      {/* Activity Timeline */}
      <div className="bg-surface border border-border rounded-xl p-6 mb-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-heading text-lg font-semibold">Activity Timeline</h2>
          <button onClick={() => setShowLogInteraction(true)}
            className="flex items-center gap-1 text-xs bg-gold/10 text-gold px-3 py-1.5 rounded-lg hover:bg-gold/20">
            <PlusIcon className="w-3 h-3" /> Log Interaction
          </button>
        </div>
        {timeline.length === 0 ? (
          <p className="text-text-secondary text-sm">No interactions yet. Log your first touchpoint.</p>
        ) : (
          <div>
            {timeline.map((i) => {
              const Icon = TYPE_ICONS[i.type] || DocumentTextIcon;
              const colour = TYPE_COLOURS[i.type] || 'text-text-muted bg-surface-light';
              const dt = new Date(i.occurred_at);
              return (
                <div key={i.id} className="flex gap-4 group">
                  <div className="flex flex-col items-center">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center ${colour}`}>
                      <Icon className="w-4 h-4" />
                    </div>
                    <div className="w-px flex-1 bg-border mt-1" />
                  </div>
                  <div className="pb-4 flex-1">
                    <div className="flex items-baseline justify-between">
                      <h4 className="text-sm font-medium text-text-primary">
                        {i.subject || i.type.charAt(0).toUpperCase() + i.type.slice(1)}
                      </h4>
                      <span className="text-xs text-text-muted shrink-0 ml-2">
                        {dt.toLocaleDateString('en-AU', { day: 'numeric', month: 'short' })}
                      </span>
                    </div>
                    {i.content && <p className="text-xs text-text-secondary mt-1 line-clamp-2">{i.content}</p>}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Notes */}
      <div className="bg-surface border border-border rounded-xl p-6">
        <h2 className="font-heading text-lg font-semibold mb-4">Notes</h2>
        <div className="flex gap-2 mb-4">
          <input value={newNote} onChange={(e) => setNewNote(e.target.value)} placeholder="Add a note..."
            className="flex-1 bg-midnight border border-border rounded-lg px-3 py-2 text-sm text-text-primary placeholder-text-muted focus:outline-none focus:border-gold"
            onKeyDown={async (e) => {
              if (e.key === 'Enter' && newNote.trim()) {
                try {
                  await api.post('/notes', { contact_id: id, content: newNote.trim() });
                  setNewNote('');
                  fetchNotes();
                  toast('Note added');
                } catch (err) { toast(err.message, 'error'); }
              }
            }} />
          <button onClick={async () => {
            if (!newNote.trim()) return;
            try {
              await api.post('/notes', { contact_id: id, content: newNote.trim() });
              setNewNote('');
              fetchNotes();
              toast('Note added');
            } catch (err) { toast(err.message, 'error'); }
          }} className="px-3 py-2 bg-gold text-midnight text-sm font-medium rounded-lg">Add</button>
        </div>
        {notes.length === 0 ? (
          <p className="text-text-muted text-sm">No notes yet.</p>
        ) : (
          <div className="space-y-3">
            {notes.map((n) => (
              <div key={n.id} className="bg-midnight border border-border rounded-lg p-3">
                <p className="text-sm text-text-primary">{n.content}</p>
                <span className="text-xs text-text-muted mt-1 block">
                  {new Date(n.created_at).toLocaleDateString('en-AU', { day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' })}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Log Interaction Modal */}
      <Modal open={showLogInteraction} onClose={() => setShowLogInteraction(false)} title="Log Interaction">
        <form onSubmit={async (e) => {
          e.preventDefault();
          const payload = { contact_id: id, ...interactionForm };
          if (!payload.subject) delete payload.subject;
          if (!payload.content) delete payload.content;
          if (!payload.channel) delete payload.channel;
          if (payload.duration_minutes) payload.duration_minutes = parseInt(payload.duration_minutes);
          else delete payload.duration_minutes;
          try {
            await api.post('/interactions', payload);
            toast('Interaction logged');
            setShowLogInteraction(false);
            setInteractionForm({ type: 'email', subject: '', content: '', channel: '', duration_minutes: '' });
            fetchTimeline();
          } catch (err) { toast(err.message, 'error'); }
        }} className="space-y-3">
          {(() => {
            const cls = 'bg-midnight border border-border rounded-lg px-3 py-2 text-sm text-text-primary placeholder-text-muted focus:outline-none focus:border-gold';
            const set = (k) => (e) => setInteractionForm((f) => ({ ...f, [k]: e.target.value }));
            return <>
              <select value={interactionForm.type} onChange={set('type')} className={`w-full ${cls}`}>
                <option value="email">Email</option>
                <option value="call">Call</option>
                <option value="meeting">Meeting</option>
                <option value="note">Note</option>
              </select>
              <input placeholder="Subject" value={interactionForm.subject} onChange={set('subject')} className={`w-full ${cls}`} />
              <textarea placeholder="Content" value={interactionForm.content} onChange={set('content')} rows={3} className={`w-full ${cls}`} />
              <div className="grid grid-cols-2 gap-3">
                <input placeholder="Channel" value={interactionForm.channel} onChange={set('channel')} className={cls} />
                <input placeholder="Duration (min)" type="number" min="0" value={interactionForm.duration_minutes} onChange={set('duration_minutes')} className={cls} />
              </div>
              <button type="submit" className="w-full bg-gold hover:bg-gold-light text-midnight font-medium py-2 rounded-lg text-sm transition-colors">Log Interaction</button>
            </>;
          })()}
        </form>
      </Modal>
    </div>
  );
}
