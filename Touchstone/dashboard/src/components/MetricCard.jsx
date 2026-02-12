export default function MetricCard({ label, value, sub, color = 'gold' }) {
  const colorMap = {
    gold: 'text-gold',
    green: 'text-healthy',
    purple: 'text-purple',
    red: 'text-critical',
  };

  return (
    <div className="bg-surface border border-border rounded-xl p-4">
      <p className="text-xs text-text-muted mb-1">{label}</p>
      <p className={`text-2xl font-semibold font-heading ${colorMap[color] || colorMap.gold}`}>
        {value}
      </p>
      {sub && <p className="text-xs text-text-secondary mt-1">{sub}</p>}
    </div>
  );
}
