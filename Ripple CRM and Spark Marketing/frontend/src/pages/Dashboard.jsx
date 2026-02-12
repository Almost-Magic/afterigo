import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  UserGroupIcon,
  CurrencyDollarIcon,
  ExclamationTriangleIcon,
  ClockIcon,
  ArrowPathIcon,
  ChevronRightIcon,
  PhoneIcon,
  EnvelopeIcon,
  CalendarIcon,
  DocumentTextIcon,
} from '@heroicons/react/24/outline';

const typeIcons = {
  email: EnvelopeIcon,
  call: PhoneIcon,
  meeting: CalendarIcon,
  note: DocumentTextIcon,
};

function MetricCard({ label, value, icon: Icon, colour = 'gold', sub }) {
  const colourMap = {
    gold: 'text-gold bg-gold/10',
    green: 'text-green-400 bg-green-400/10',
    red: 'text-red-400 bg-red-400/10',
    blue: 'text-blue-400 bg-blue-400/10',
  };
  return (
    <div className="bg-surface rounded-xl border border-border p-5">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs text-text-muted uppercase tracking-wide">{label}</p>
          <p className="text-3xl font-heading font-semibold mt-1 text-text-primary">{value}</p>
          {sub && <p className="text-xs text-text-muted mt-1">{sub}</p>}
        </div>
        <div className={`p-2 rounded-lg ${colourMap[colour]}`}>
          <Icon className="w-6 h-6" />
        </div>
      </div>
    </div>
  );
}

function SectionHeader({ title, linkTo, linkLabel }) {
  return (
    <div className="flex items-center justify-between mb-3">
      <h2 className="font-heading text-lg font-semibold text-text-primary">{title}</h2>
      {linkTo && (
        <Link to={linkTo} className="text-xs text-gold hover:underline flex items-center gap-1">
          {linkLabel} <ChevronRightIcon className="w-3 h-3" />
        </Link>
      )}
    </div>
  );
}

function HealthBadge({ score, label }) {
  if (!score && score !== 0) return <span className="text-xs text-text-muted">—</span>;
  const colour =
    label === 'Healthy' ? 'bg-green-400/10 text-green-400' :
    label === 'Warning' ? 'bg-amber-400/10 text-amber-400' :
    'bg-red-400/10 text-red-400';
  return (
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${colour}`}>
      {Math.round(score)}
    </span>
  );
}

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchDashboard = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/dashboard');
      if (!res.ok) throw new Error(`${res.status}`);
      setData(await res.json());
      setError(null);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchDashboard(); }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <ArrowPathIcon className="w-8 h-8 text-text-muted animate-spin" />
      </div>
    );
  }
  if (error) {
    return (
      <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-6 text-center">
        <p className="text-red-400 font-medium">Failed to load dashboard</p>
        <p className="text-text-muted text-sm mt-1">{error}</p>
        <button onClick={fetchDashboard} className="mt-3 text-sm text-gold hover:underline">Retry</button>
      </div>
    );
  }
  if (!data) return null;

  const { metrics, people_to_reach, deals_needing_attention, overdue_commitments, todays_tasks, recent_activity } = data;

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-heading text-2xl font-semibold text-text-primary">Daily Command Centre</h1>
          <p className="text-sm text-text-muted mt-1">
            {new Date().toLocaleDateString('en-AU', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' })}
          </p>
        </div>
        <button
          onClick={fetchDashboard}
          className="p-2 rounded-lg hover:bg-surface-light text-text-muted hover:text-text-primary transition-colors"
          title="Refresh"
        >
          <ArrowPathIcon className="w-5 h-5" />
        </button>
      </div>

      {/* Metric Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard label="Contacts" value={metrics.total_contacts} icon={UserGroupIcon} colour="blue" />
        <MetricCard label="Active Deals" value={metrics.active_deals} icon={CurrencyDollarIcon} colour="gold" />
        <MetricCard
          label="Pipeline Value"
          value={`$${metrics.pipeline_value.toLocaleString('en-AU')}`}
          icon={CurrencyDollarIcon}
          colour="green"
        />
        <MetricCard
          label="Overdue Tasks"
          value={metrics.overdue_tasks}
          icon={ExclamationTriangleIcon}
          colour={metrics.overdue_tasks > 0 ? 'red' : 'green'}
        />
      </div>

      {/* Two-Column Layout */}
      <div className="grid lg:grid-cols-2 gap-6">
        {/* People to Reach Out To */}
        <div className="bg-surface rounded-xl border border-border p-5">
          <SectionHeader title="People to Reach" linkTo="/contacts" linkLabel="All contacts" />
          {people_to_reach.length === 0 ? (
            <p className="text-sm text-text-muted py-4 text-center">All relationships healthy</p>
          ) : (
            <div className="space-y-2">
              {people_to_reach.map((p) => (
                <Link
                  key={p.id}
                  to={`/contacts/${p.id}`}
                  className="flex items-center justify-between p-3 rounded-lg hover:bg-surface-light transition-colors"
                >
                  <div>
                    <p className="text-sm font-medium text-text-primary">{p.name}</p>
                    <p className="text-xs text-text-muted">
                      {p.trust_decay_days} days since last contact
                    </p>
                  </div>
                  <HealthBadge score={p.health_score} label={p.health_score >= 70 ? 'Healthy' : p.health_score >= 40 ? 'Warning' : 'Critical'} />
                </Link>
              ))}
            </div>
          )}
        </div>

        {/* Deals Needing Attention */}
        <div className="bg-surface rounded-xl border border-border p-5">
          <SectionHeader title="Deals Needing Attention" linkTo="/deals" linkLabel="All deals" />
          {deals_needing_attention.length === 0 ? (
            <p className="text-sm text-text-muted py-4 text-center">All deals on track</p>
          ) : (
            <div className="space-y-2">
              {deals_needing_attention.map((d) => (
                <div key={d.id} className="flex items-center justify-between p-3 rounded-lg hover:bg-surface-light transition-colors">
                  <div>
                    <p className="text-sm font-medium text-text-primary">{d.title}</p>
                    <p className="text-xs text-text-muted">
                      {d.stage.replace('_', ' ')} · {d.days_in_stage != null ? `${d.days_in_stage}d in stage` : 'New'}
                    </p>
                  </div>
                  <span className="text-sm font-medium text-gold">
                    ${(d.value || 0).toLocaleString('en-AU')}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Overdue Commitments */}
        <div className="bg-surface rounded-xl border border-border p-5">
          <SectionHeader title="Overdue Commitments" linkTo="/commitments" linkLabel="All commitments" />
          {overdue_commitments.length === 0 ? (
            <p className="text-sm text-text-muted py-4 text-center">No overdue commitments</p>
          ) : (
            <div className="space-y-2">
              {overdue_commitments.map((c) => (
                <div key={c.id} className="flex items-center justify-between p-3 rounded-lg bg-red-500/5 border border-red-500/10">
                  <div>
                    <p className="text-sm font-medium text-text-primary">{c.description}</p>
                    <p className="text-xs text-text-muted">
                      {c.committed_by === 'us' ? 'We promised' : 'They promised'} · Due {c.due_date}
                    </p>
                  </div>
                  <span className="text-xs font-medium text-red-400">
                    {c.days_overdue}d overdue
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Today's Tasks */}
        <div className="bg-surface rounded-xl border border-border p-5">
          <SectionHeader title="Today's Tasks" linkTo="/tasks" linkLabel="All tasks" />
          {todays_tasks.length === 0 ? (
            <p className="text-sm text-text-muted py-4 text-center">No tasks due today</p>
          ) : (
            <div className="space-y-2">
              {todays_tasks.map((t) => (
                <div key={t.id} className="flex items-center justify-between p-3 rounded-lg hover:bg-surface-light transition-colors">
                  <div className="flex items-center gap-3">
                    <ClockIcon className="w-4 h-4 text-text-muted" />
                    <span className="text-sm text-text-primary">{t.title}</span>
                  </div>
                  <span className={`text-xs px-2 py-0.5 rounded-full ${
                    t.priority === 'urgent' ? 'bg-red-400/10 text-red-400' :
                    t.priority === 'high' ? 'bg-amber-400/10 text-amber-400' :
                    'bg-surface-light text-text-muted'
                  }`}>
                    {t.priority}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-surface rounded-xl border border-border p-5">
        <SectionHeader title="Recent Activity" linkTo="/interactions" linkLabel="All interactions" />
        {recent_activity.length === 0 ? (
          <p className="text-sm text-text-muted py-4 text-center">No recent activity</p>
        ) : (
          <div className="divide-y divide-border">
            {recent_activity.map((a) => {
              const Icon = typeIcons[a.type] || DocumentTextIcon;
              return (
                <div key={a.id} className="flex items-center gap-4 py-3">
                  <div className="p-2 rounded-lg bg-surface-light">
                    <Icon className="w-4 h-4 text-text-muted" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-text-primary truncate">{a.subject}</p>
                    <p className="text-xs text-text-muted">{a.type}</p>
                  </div>
                  <span className="text-xs text-text-muted whitespace-nowrap">
                    {a.occurred_at ? new Date(a.occurred_at).toLocaleDateString('en-AU', { day: 'numeric', month: 'short' }) : '—'}
                  </span>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
