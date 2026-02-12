export default function TraitBar({ label, value, color = 'bg-gold' }) {
  return (
    <div className="mb-3">
      <div className="mb-1 flex justify-between text-sm">
        <span className="text-text-secondary">{label}</span>
        <span className="font-mono text-text-primary">{Math.round(value)}%</span>
      </div>
      <div className="h-2.5 w-full rounded-full bg-midnight">
        <div
          className={`h-full rounded-full ${color} transition-all duration-700`}
          style={{ width: `${value}%` }}
        />
      </div>
    </div>
  )
}
