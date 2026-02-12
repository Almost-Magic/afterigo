import { useEffect, useState } from 'react';
import { BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { api } from '../lib/api';
import { toast } from '../components/Toast';
import MetricCard from '../components/MetricCard';
import ModelSelector from '../components/ModelSelector';
import DateRangePicker from '../components/DateRangePicker';

const COLORS = ['#C9944A', '#34D399', '#A78BFA', '#FBBF24', '#F87171', '#60A5FA'];

function fmt(n) {
  if (n == null) return '$0';
  return '$' + Number(n).toLocaleString('en-AU', { maximumFractionDigits: 0 });
}

export default function Overview() {
  const [model, setModel] = useState('linear');
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [campaigns, setCampaigns] = useState(null);
  const [channels, setChannels] = useState(null);
  const [loading, setLoading] = useState(true);
  const [calculating, setCalculating] = useState(false);

  const fetchData = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({ model });
      if (dateFrom) params.append('date_from', dateFrom);
      if (dateTo) params.append('date_to', dateTo);
      const qs = params.toString();
      const [camp, chan] = await Promise.all([
        api.get(`/attribution/campaigns?${qs}`),
        api.get(`/attribution/channels?${qs}`),
      ]);
      setCampaigns(camp);
      setChannels(chan);
    } catch (err) {
      toast(err.message, 'error');
    }
    setLoading(false);
  };

  useEffect(() => { fetchData(); }, [model, dateFrom, dateTo]);

  const recalculate = async () => {
    setCalculating(true);
    try {
      const result = await api.post('/attribution/calculate', { model, recalculate: true });
      toast(`Calculated: ${result.deals_processed} deals, ${result.attributions_created} attributions`);
      await fetchData();
    } catch (err) {
      toast(err.message, 'error');
    }
    setCalculating(false);
  };

  const totalRevenue = campaigns?.total_attributed_revenue || 0;
  const dealCount = campaigns?.items?.reduce((s, c) => s + (c.deal_count || 0), 0) || 0;
  const campaignCount = campaigns?.items?.length || 0;
  const channelCount = channels?.items?.length || 0;

  const barData = (campaigns?.items || [])
    .slice(0, 6)
    .map((c) => ({ name: c.campaign_name?.replace(/\s*—.*/, '') || 'Unattributed', revenue: Number(c.attributed_revenue) }));

  const pieData = (channels?.items || []).map((c) => ({
    name: c.channel, value: Number(c.attributed_revenue),
  }));

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <h2 className="text-xl font-semibold font-heading">Attribution Overview</h2>
        <div className="flex items-center gap-3 flex-wrap">
          <ModelSelector value={model} onChange={setModel} />
          <DateRangePicker
            dateFrom={dateFrom}
            dateTo={dateTo}
            onChange={({ dateFrom: f, dateTo: t }) => { setDateFrom(f); setDateTo(t); }}
          />
          <button
            onClick={recalculate}
            disabled={calculating}
            className="px-3 py-1.5 bg-gold/20 text-gold text-sm rounded-lg border border-gold/30 hover:bg-gold/30 transition-colors disabled:opacity-50"
          >
            {calculating ? 'Calculating...' : 'Recalculate'}
          </button>
        </div>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard label="Total Attributed Revenue" value={fmt(totalRevenue)} color="gold" />
        <MetricCard label="Deals Attributed" value={dealCount} color="green" />
        <MetricCard label="Campaigns" value={campaignCount} color="purple" />
        <MetricCard label="Channels" value={channelCount} sub={`Model: ${model.replace('_', ' ')}`} />
      </div>

      {loading ? (
        <div className="text-text-muted text-center py-12">Loading attribution data...</div>
      ) : (
        <div className="grid lg:grid-cols-2 gap-6">
          <div className="bg-surface border border-border rounded-xl p-4">
            <h3 className="text-sm font-medium text-text-secondary mb-4">Revenue by Campaign</h3>
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={barData} layout="vertical" margin={{ left: 10, right: 20 }}>
                <XAxis type="number" tickFormatter={(v) => `$${(v / 1000).toFixed(0)}k`} stroke="#6B7280" fontSize={11} />
                <YAxis type="category" dataKey="name" width={130} stroke="#6B7280" fontSize={11} tick={{ fill: '#9CA3AF' }} />
                <Tooltip
                  formatter={(v) => [fmt(v), 'Revenue']}
                  contentStyle={{ background: '#151B26', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 8, fontSize: 12 }}
                  labelStyle={{ color: '#F0F0F0' }}
                />
                <Bar dataKey="revenue" fill="#C9944A" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="bg-surface border border-border rounded-xl p-4">
            <h3 className="text-sm font-medium text-text-secondary mb-4">Revenue by Channel</h3>
            <ResponsiveContainer width="100%" height={280}>
              <PieChart>
                <Pie data={pieData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={100} label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`} labelLine={false} fontSize={11}>
                  {pieData.map((_, i) => (
                    <Cell key={i} fill={COLORS[i % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  formatter={(v) => [fmt(v), 'Revenue']}
                  contentStyle={{ background: '#151B26', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 8, fontSize: 12 }}
                />
                <Legend wrapperStyle={{ fontSize: 11, color: '#9CA3AF' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}
    </div>
  );
}
