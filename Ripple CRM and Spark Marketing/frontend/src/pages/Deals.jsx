import { useEffect, useState, useCallback } from 'react';
import { PlusIcon } from '@heroicons/react/24/outline';
import { api } from '../lib/api';
import Modal from '../components/Modal';
import { toast } from '../components/Toast';

const STAGES = [
  { key: 'lead', label: 'Lead', colour: 'bg-surface-light' },
  { key: 'qualified', label: 'Qualified', colour: 'bg-purple/10' },
  { key: 'proposal', label: 'Proposal', colour: 'bg-gold/10' },
  { key: 'negotiation', label: 'Negotiation', colour: 'bg-warning/10' },
  { key: 'closed_won', label: 'Won', colour: 'bg-healthy/10' },
  { key: 'closed_lost', label: 'Lost', colour: 'bg-critical/10' },
];

function DealForm({ onSubmit }) {
  const [form, setForm] = useState({
    title: '', description: '', value: '', currency: 'AUD',
    stage: 'lead', probability: '', expected_close_date: '',
    owner: '', source: '',
  });
  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }));
  const cls = 'bg-midnight border border-border rounded-lg px-3 py-2 text-sm text-text-primary placeholder-text-muted focus:outline-none focus:border-gold';

  return (
    <form onSubmit={(e) => {
      e.preventDefault();
      const payload = { ...form };
      if (payload.value) payload.value = parseFloat(payload.value);
      else delete payload.value;
      if (payload.probability) payload.probability = parseFloat(payload.probability);
      else delete payload.probability;
      if (!payload.expected_close_date) delete payload.expected_close_date;
      if (!payload.owner) delete payload.owner;
      if (!payload.source) delete payload.source;
      if (!payload.description) delete payload.description;
      onSubmit(payload);
    }} className="space-y-3">
      <input placeholder="Deal title *" required value={form.title} onChange={set('title')} className={`w-full ${cls}`} />
      <div className="grid grid-cols-2 gap-3">
        <input placeholder="Value" type="number" step="0.01" value={form.value} onChange={set('value')} className={cls} />
        <select value={form.stage} onChange={set('stage')} className={cls}>
          {STAGES.map((s) => <option key={s.key} value={s.key}>{s.label}</option>)}
        </select>
      </div>
      <div className="grid grid-cols-2 gap-3">
        <input placeholder="Probability %" type="number" min="0" max="100" value={form.probability} onChange={set('probability')} className={cls} />
        <input placeholder="Expected close" type="date" value={form.expected_close_date} onChange={set('expected_close_date')} className={cls} />
      </div>
      <div className="grid grid-cols-2 gap-3">
        <input placeholder="Owner" value={form.owner} onChange={set('owner')} className={cls} />
        <input placeholder="Source" value={form.source} onChange={set('source')} className={cls} />
      </div>
      <textarea placeholder="Description" value={form.description} onChange={set('description')} rows={2}
        className={`w-full ${cls}`} />
      <button type="submit"
        className="w-full bg-gold hover:bg-gold-light text-midnight font-medium py-2 rounded-lg text-sm transition-colors">
        Create Deal
      </button>
    </form>
  );
}

function DealCard({ deal, onStageChange }) {
  const fmt = (v) => v != null ? `$${Number(v).toLocaleString('en-AU')}` : '';

  return (
    <div className="bg-midnight border border-border rounded-lg p-3 mb-2 hover:border-gold/30 transition-colors group">
      <div className="flex items-start justify-between">
        <h4 className="text-sm font-medium text-text-primary leading-tight">{deal.title}</h4>
        {deal.value != null && (
          <span className="text-xs font-mono text-gold ml-2 shrink-0">{fmt(deal.value)}</span>
        )}
      </div>
      {deal.owner && <p className="text-xs text-text-muted mt-1">{deal.owner}</p>}
      {deal.expected_close_date && (
        <p className="text-xs text-text-secondary mt-1">Close: {deal.expected_close_date}</p>
      )}
      {deal.probability != null && (
        <div className="mt-2">
          <div className="w-full h-1 bg-surface-light rounded-full overflow-hidden">
            <div className="h-full bg-gold rounded-full transition-all" style={{ width: `${deal.probability}%` }} />
          </div>
          <span className="text-[10px] text-text-muted">{deal.probability}%</span>
        </div>
      )}
      <div className="flex gap-1 mt-2 opacity-0 group-hover:opacity-100 transition-opacity flex-wrap">
        {STAGES.filter((s) => s.key !== deal.stage).slice(0, 3).map((s) => (
          <button key={s.key} onClick={() => onStageChange(deal.id, s.key)}
            className="text-[10px] px-1.5 py-0.5 bg-surface-light rounded text-text-muted hover:text-text-primary">
            → {s.label}
          </button>
        ))}
      </div>
    </div>
  );
}

export default function Deals() {
  const [deals, setDeals] = useState([]);
  const [total, setTotal] = useState(0);
  const [showCreate, setShowCreate] = useState(false);
  const [loading, setLoading] = useState(true);

  const fetchDeals = useCallback(async () => {
    setLoading(true);
    try {
      const data = await api.get('/deals?page_size=200');
      setDeals(data.items);
      setTotal(data.total);
    } catch (err) {
      toast(err.message, 'error');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchDeals(); }, [fetchDeals]);

  const handleCreate = async (form) => {
    try {
      await api.post('/deals', form);
      toast('Deal created');
      setShowCreate(false);
      fetchDeals();
    } catch (err) {
      toast(err.message, 'error');
    }
  };

  const handleStageChange = async (dealId, newStage) => {
    try {
      await api.put(`/deals/${dealId}`, { stage: newStage });
      toast(`Moved to ${newStage}`);
      fetchDeals();
    } catch (err) {
      toast(err.message, 'error');
    }
  };

  const pipelineValue = deals.filter((d) => !['closed_won', 'closed_lost'].includes(d.stage))
    .reduce((sum, d) => sum + (d.value || 0), 0);

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="font-heading text-2xl font-semibold">Deal Pipeline</h1>
          <p className="text-text-secondary text-sm mt-1">
            {total} deal{total !== 1 ? 's' : ''} · Pipeline value: ${pipelineValue.toLocaleString('en-AU')} AUD
          </p>
        </div>
        <button onClick={() => setShowCreate(true)}
          className="flex items-center gap-2 bg-gold hover:bg-gold-light text-midnight font-medium px-4 py-2 rounded-lg text-sm transition-colors">
          <PlusIcon className="w-4 h-4" /> Add Deal
        </button>
      </div>

      {loading ? (
        <div className="text-text-muted text-sm py-8 text-center">Loading pipeline...</div>
      ) : (
        <div className="grid grid-cols-6 gap-3 min-h-[60vh]">
          {STAGES.map((stage) => {
            const stageDeals = deals.filter((d) => d.stage === stage.key);
            const stageValue = stageDeals.reduce((s, d) => s + (d.value || 0), 0);
            return (
              <div key={stage.key} className={`rounded-xl p-3 ${stage.colour} border border-border`}>
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-xs font-semibold text-text-primary uppercase tracking-wider">{stage.label}</h3>
                  <span className="text-[10px] bg-surface rounded-full px-2 py-0.5 text-text-muted">
                    {stageDeals.length}
                  </span>
                </div>
                {stageValue > 0 && (
                  <p className="text-xs text-gold font-mono mb-2">${stageValue.toLocaleString('en-AU')}</p>
                )}
                <div className="space-y-0">
                  {stageDeals.map((d) => (
                    <DealCard key={d.id} deal={d} onStageChange={handleStageChange} />
                  ))}
                </div>
                {stageDeals.length === 0 && (
                  <p className="text-xs text-text-muted text-center py-4">No deals</p>
                )}
              </div>
            );
          })}
        </div>
      )}

      <Modal open={showCreate} onClose={() => setShowCreate(false)} title="Add Deal">
        <DealForm onSubmit={handleCreate} />
      </Modal>
    </div>
  );
}
