import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { api } from '../lib/api';
import { toast } from '../components/Toast';
import ModelSelector from '../components/ModelSelector';

const CHANNEL_COLORS = {
  paid: '#F87171',
  email: '#C9944A',
  social: '#A78BFA',
  organic: '#34D399',
  referral: '#FBBF24',
  direct: '#60A5FA',
};

function fmt(n) {
  if (n == null) return '$0';
  return '$' + Number(n).toLocaleString('en-AU', { maximumFractionDigits: 0 });
}

export default function ContactJourney() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [model, setModel] = useState('linear');
  const [journey, setJourney] = useState(null);
  const [attribution, setAttribution] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    Promise.all([
      api.get(`/contacts/${id}/journey`),
      api.get(`/contacts/${id}/attribution?model=${model}`),
    ])
      .then(([j, a]) => { setJourney(j); setAttribution(a); })
      .catch((e) => {
        toast(e.message, 'error');
        if (e.message.includes('not found')) navigate('/contacts');
      })
      .finally(() => setLoading(false));
  }, [id, model]);

  if (loading) return <div className="text-text-muted text-center py-12">Loading journey...</div>;
  if (!journey) return null;

  const { contact, touchpoints } = journey;
  const records = attribution?.items || [];

  const attrByTouchpoint = {};
  for (const r of records) {
    if (r.touchpoint_id) attrByTouchpoint[r.touchpoint_id] = r;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <button onClick={() => navigate('/contacts')} className="text-xs text-text-muted hover:text-gold transition-colors mb-1">
            &larr; Back to Contacts
          </button>
          <h2 className="text-xl font-semibold font-heading">{contact.name || 'Anonymous'}</h2>
          <p className="text-sm text-text-secondary">{contact.email} {contact.company && `at ${contact.company}`}</p>
        </div>
        <ModelSelector value={model} onChange={setModel} />
      </div>

      {records.length > 0 && (
        <div className="bg-surface border border-border rounded-xl p-4">
          <h3 className="text-sm font-medium text-text-secondary mb-3">Attribution ({model.replace('_', ' ')})</h3>
          <div className="space-y-2">
            {records.map((r, i) => (
              <div key={i} className="flex items-center justify-between py-1.5 border-b border-border/30 last:border-0">
                <div>
                  <span className="text-sm text-text-primary">{r.deal_name || r.deal_id}</span>
                  <span className="text-xs text-text-muted ml-2">{r.channel}</span>
                </div>
                <div className="flex items-center gap-4">
                  <span className="text-xs text-text-secondary">{(Number(r.attribution_weight) * 100).toFixed(1)}%</span>
                  <span className="font-mono text-sm text-gold">{fmt(r.attributed_amount)}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="bg-surface border border-border rounded-xl p-4">
        <h3 className="text-sm font-medium text-text-secondary mb-4">
          Journey Timeline ({touchpoints.length} touchpoints)
        </h3>
        <div className="relative">
          <div className="absolute left-4 top-0 bottom-0 w-px bg-border" />
          <div className="space-y-4">
            {touchpoints.map((tp, i) => {
              const attr = attrByTouchpoint[tp.id];
              const color = CHANNEL_COLORS[tp.channel] || '#6B7280';
              return (
                <div key={tp.id} className="relative pl-10">
                  <div
                    className="absolute left-2.5 top-2 w-3 h-3 rounded-full border-2 border-surface"
                    style={{ backgroundColor: color }}
                  />
                  <div className="bg-surface-light border border-border/50 rounded-lg p-3">
                    <div className="flex items-center justify-between mb-1">
                      <div className="flex items-center gap-2">
                        <span className="text-xs px-1.5 py-0.5 rounded text-white/90" style={{ backgroundColor: color }}>
                          {tp.channel}
                        </span>
                        <span className="text-xs text-text-muted">{tp.touchpoint_type}</span>
                      </div>
                      <span className="text-xs text-text-muted">
                        {new Date(tp.timestamp).toLocaleString()}
                      </span>
                    </div>
                    <p className="text-sm text-text-primary">{tp.page_url}</p>
                    <div className="flex items-center gap-3 mt-1 text-xs text-text-muted">
                      {tp.source && <span>Source: {tp.source}</span>}
                      {tp.medium && <span>Medium: {tp.medium}</span>}
                      {tp.utm_campaign && <span>Campaign: {tp.utm_campaign}</span>}
                    </div>
                    {attr && (
                      <div className="mt-2 pt-2 border-t border-border/30 flex items-center gap-3">
                        <span className="text-xs text-gold">Weight: {(Number(attr.attribution_weight) * 100).toFixed(1)}%</span>
                        <span className="text-xs font-mono text-gold">{fmt(attr.attributed_amount)}</span>
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
