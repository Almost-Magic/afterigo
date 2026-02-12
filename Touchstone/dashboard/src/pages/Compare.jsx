import { useEffect, useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { api } from '../lib/api';
import { toast } from '../components/Toast';
import DateRangePicker from '../components/DateRangePicker';

const MODEL_COLORS = {
  first_touch: '#C9944A',
  last_touch: '#34D399',
  linear: '#A78BFA',
  time_decay: '#FBBF24',
  position_based: '#60A5FA',
};

const MODEL_LABELS = {
  first_touch: 'First Touch',
  last_touch: 'Last Touch',
  linear: 'Linear',
  time_decay: 'Time Decay',
  position_based: 'Position Based',
};

function fmt(n) {
  if (n == null) return '$0';
  return '$' + Number(n).toLocaleString('en-AU', { maximumFractionDigits: 0 });
}

export default function Compare() {
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    const params = new URLSearchParams();
    if (dateFrom) params.append('date_from', dateFrom);
    if (dateTo) params.append('date_to', dateTo);
    api.get(`/attribution/compare?${params}`)
      .then((d) => { setData(d); setLoading(false); })
      .catch((e) => { toast(e.message, 'error'); setLoading(false); });
  }, [dateFrom, dateTo]);

  const models = ['first_touch', 'last_touch', 'linear', 'time_decay', 'position_based'];
  const campaigns = data?.campaigns || [];

  const chartData = campaigns.slice(0, 8).map((c) => {
    const row = { name: c.campaign_name?.replace(/\s*—.*/, '').slice(0, 18) || 'Unattributed' };
    for (const m of models) {
      row[m] = Number(c[m] || 0);
    }
    return row;
  });

  const maxVariance = campaigns.reduce((max, c) => {
    const vals = models.map((m) => Number(c[m] || 0)).filter((v) => v > 0);
    if (vals.length < 2) return max;
    const range = Math.max(...vals) - Math.min(...vals);
    return range > max ? range : max;
  }, 0);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <h2 className="text-xl font-semibold font-heading">Model Comparison</h2>
        <DateRangePicker dateFrom={dateFrom} dateTo={dateTo} onChange={({ dateFrom: f, dateTo: t }) => { setDateFrom(f); setDateTo(t); }} />
      </div>

      {loading ? (
        <div className="text-text-muted text-center py-12">Loading comparison data...</div>
      ) : (
        <>
          <div className="bg-surface border border-border rounded-xl p-4">
            <h3 className="text-sm font-medium text-text-secondary mb-4">Revenue by Campaign x Model</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={chartData} margin={{ left: 10, right: 10 }}>
                <XAxis dataKey="name" stroke="#6B7280" fontSize={10} tick={{ fill: '#9CA3AF' }} />
                <YAxis tickFormatter={(v) => `$${(v / 1000).toFixed(0)}k`} stroke="#6B7280" fontSize={11} />
                <Tooltip formatter={(v, name) => [fmt(v), MODEL_LABELS[name] || name]} contentStyle={{ background: '#151B26', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 8, fontSize: 12 }} />
                <Legend wrapperStyle={{ fontSize: 11 }} formatter={(v) => MODEL_LABELS[v] || v} />
                {models.map((m) => (
                  <Bar key={m} dataKey={m} fill={MODEL_COLORS[m] || '#6B7280'} radius={[2, 2, 0, 0]} />
                ))}
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="bg-surface border border-border rounded-xl overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border text-text-muted text-xs">
                  <th className="text-left p-3 font-medium">Campaign</th>
                  {models.map((m) => (
                    <th key={m} className="text-right p-3 font-medium">{MODEL_LABELS[m]}</th>
                  ))}
                  <th className="text-right p-3 font-medium">Variance</th>
                </tr>
              </thead>
              <tbody>
                {campaigns.map((c, i) => {
                  const vals = models.map((m) => Number(c[m] || 0)).filter((v) => v > 0);
                  const variance = vals.length >= 2 ? Math.max(...vals) - Math.min(...vals) : 0;
                  const highVariance = variance > maxVariance * 0.5 && variance > 10000;

                  return (
                    <tr key={i} className={`border-b border-border/50 transition-colors ${highVariance ? 'bg-warning/5' : 'hover:bg-surface-light/50'}`}>
                      <td className="p-3 text-text-primary">{c.campaign_name || 'Unattributed'}</td>
                      {models.map((m) => (
                        <td key={m} className="p-3 text-right font-mono text-text-secondary">
                          {fmt(c[m])}
                        </td>
                      ))}
                      <td className={`p-3 text-right font-mono ${highVariance ? 'text-warning font-medium' : 'text-text-muted'}`}>
                        {fmt(variance)}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
            {campaigns.length === 0 && (
              <p className="text-center text-text-muted py-8">No comparison data. Calculate attributions for multiple models first.</p>
            )}
          </div>
        </>
      )}
    </div>
  );
}
