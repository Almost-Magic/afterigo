export default function DateRangePicker({ dateFrom, dateTo, onChange }) {
  const presets = [
    { label: '30d', days: 30 },
    { label: '60d', days: 60 },
    { label: '90d', days: 90 },
    { label: 'All', days: null },
  ];

  const applyPreset = (days) => {
    if (days === null) {
      onChange({ dateFrom: '', dateTo: '' });
    } else {
      const to = new Date().toISOString().slice(0, 10);
      const from = new Date(Date.now() - days * 86400000).toISOString().slice(0, 10);
      onChange({ dateFrom: from, dateTo: to });
    }
  };

  return (
    <div className="flex items-center gap-2">
      <div className="flex gap-1">
        {presets.map((p) => (
          <button
            key={p.label}
            onClick={() => applyPreset(p.days)}
            className="px-2 py-1 text-xs rounded bg-surface-light border border-border text-text-secondary hover:text-text-primary hover:border-gold/30 transition-colors"
          >
            {p.label}
          </button>
        ))}
      </div>
      <input
        type="date"
        value={dateFrom}
        onChange={(e) => onChange({ dateFrom: e.target.value, dateTo })}
        className="bg-surface-light border border-border rounded-lg px-2 py-1 text-xs text-text-primary focus:outline-none focus:border-gold/50"
      />
      <span className="text-text-muted text-xs">to</span>
      <input
        type="date"
        value={dateTo}
        onChange={(e) => onChange({ dateFrom, dateTo: e.target.value })}
        className="bg-surface-light border border-border rounded-lg px-2 py-1 text-xs text-text-primary focus:outline-none focus:border-gold/50"
      />
    </div>
  );
}
