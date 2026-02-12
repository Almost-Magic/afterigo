import { useEffect, useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { api } from '../lib/api';
import { toast } from '../components/Toast';
import ModelSelector from '../components/ModelSelector';
import DateRangePicker from '../components/DateRangePicker';

function fmt(n) {
  if (n == null) return '$0';
  return '$' + Number(n).toLocaleString('en-AU', { maximumFractionDigits: 0 });
}

export default function Campaigns() {
  const [model, setModel] = useState('linear');
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [data, setData] = useState(null);
  const [sortBy, setSortBy] = useState('attributed_revenue');
  const [sortDir, setSortDir] = useState('desc');

  useEffect(() => {
    const params = new URLSearchParams({ model });
    if (dateFrom) params.append('date_from', dateFrom);
    if (dateTo) params.append('date_to', dateTo);
    api.get(`/attribution/campaigns?${params}`)
      .then(setData)
      .catch((e) => toast(e.message, 'error'));
  }, [model, dateFrom, dateTo]);

  const toggleSort = (col) => {
    if (sortBy === col) setSortDir((d) => (d === 'asc' ? 'desc' : 'asc'));
    else { setSortBy(col); setSortDir('desc'); }
  };

  const campaigns = [...(data?.items || [])].sort((a, b) => {
    const va = Number(a[sortBy]) || 0;
    const vb = Number(b[sortBy]) || 0;
    return sortDir === 'asc' ? va - vb : vb - va;
  });

  const chartData = campaigns.slice(0, 8).map((c) => ({
    name: c.campaign_name?.replace(/\s*—.*/, '').slice(0, 20) || 'Unattributed',
    revenue: Number(c.attributed_revenue),
  }));

  const arrow = (col) => sortBy === col ? (sortDir === 'asc' ? ' ^' : ' v') : '';

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <h2 className="text-xl font-semibold font-heading">Campaign Attribution</h2>
        <div className="flex items-center gap-3 flex-wrap">
          <ModelSelector value={model} onChange={setModel} />
          <DateRangePicker dateFrom={dateFrom} dateTo={dateTo} onChange={({ dateFrom: f, dateTo: t }) => { setDateFrom(f); setDateTo(t); }} />
        </div>
      </div>

      {data && (
        <div className="bg-surface border border-border rounded-xl p-4">
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={chartData} margin={{ left: 10, right: 10 }}>
              <XAxis dataKey="name" stroke="#6B7280" fontSize={10} tick={{ fill: '#9CA3AF' }} />
              <YAxis tickFormatter={(v) => `$${(v / 1000).toFixed(0)}k`} stroke="#6B7280" fontSize={11} />
              <Tooltip formatter={(v) => [fmt(v), 'Revenue']} contentStyle={{ background: '#151B26', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 8, fontSize: 12 }} />
              <Bar dataKey="revenue" fill="#C9944A" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      <div className="bg-surface border border-border rounded-xl overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border text-text-muted text-xs">
              <th className="text-left p-3 font-medium">Campaign</th>
              <th className="text-left p-3 font-medium">Channel</th>
              <th className="text-right p-3 font-medium cursor-pointer hover:text-text-primary" onClick={() => toggleSort('attributed_revenue')}>
                Revenue{arrow('attributed_revenue')}
              </th>
              <th className="text-right p-3 font-medium cursor-pointer hover:text-text-primary" onClick={() => toggleSort('deal_count')}>
                Deals{arrow('deal_count')}
              </th>
              <th className="text-right p-3 font-medium cursor-pointer hover:text-text-primary" onClick={() => toggleSort('touchpoint_count')}>
                Touchpoints{arrow('touchpoint_count')}
              </th>
              <th className="text-right p-3 font-medium">% of Total</th>
            </tr>
          </thead>
          <tbody>
            {campaigns.map((c, i) => (
              <tr key={i} className="border-b border-border/50 hover:bg-surface-light/50 transition-colors">
                <td className="p-3 text-text-primary">{c.campaign_name || 'Unattributed'}</td>
                <td className="p-3 text-text-secondary">{c.channel || '-'}</td>
                <td className="p-3 text-right font-mono text-gold">{fmt(c.attributed_revenue)}</td>
                <td className="p-3 text-right text-text-secondary">{c.deal_count}</td>
                <td className="p-3 text-right text-text-secondary">{c.touchpoint_count}</td>
                <td className="p-3 text-right text-text-muted">
                  {data?.total_attributed_revenue > 0
                    ? ((Number(c.attributed_revenue) / Number(data.total_attributed_revenue)) * 100).toFixed(1) + '%'
                    : '-'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {campaigns.length === 0 && (
          <p className="text-center text-text-muted py-8">No attribution data. Run calculation first.</p>
        )}
      </div>
    </div>
  );
}
