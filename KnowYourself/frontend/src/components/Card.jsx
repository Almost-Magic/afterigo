export default function Card({ title, children, className = '' }) {
  return (
    <div className={`rounded-2xl border border-border bg-midnight-card p-6 ${className}`}>
      {title && <h2 className="mb-4 text-lg font-semibold text-text-primary">{title}</h2>}
      {children}
    </div>
  )
}
