export default function Loading({ text = 'Loading...' }) {
  return (
    <div className="flex items-center justify-center py-12 text-text-secondary">
      <div className="mr-3 h-5 w-5 animate-spin rounded-full border-2 border-gold border-t-transparent" />
      {text}
    </div>
  )
}
