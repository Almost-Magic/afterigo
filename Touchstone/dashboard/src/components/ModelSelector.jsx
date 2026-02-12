const MODELS = [
  { value: 'first_touch', label: 'First Touch' },
  { value: 'last_touch', label: 'Last Touch' },
  { value: 'linear', label: 'Linear' },
  { value: 'time_decay', label: 'Time Decay' },
  { value: 'position_based', label: 'Position Based' },
];

export default function ModelSelector({ value, onChange }) {
  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className="bg-surface-light border border-border rounded-lg px-3 py-1.5 text-sm text-text-primary focus:outline-none focus:border-gold/50"
    >
      {MODELS.map((m) => (
        <option key={m.value} value={m.value}>{m.label}</option>
      ))}
    </select>
  );
}

export { MODELS };
