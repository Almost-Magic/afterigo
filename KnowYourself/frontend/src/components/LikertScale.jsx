const LABELS = ['Strongly Disagree', 'Disagree', 'Neutral', 'Agree', 'Strongly Agree']

export default function LikertScale({ value, onChange, questionIndex }) {
  return (
    <div className="flex items-center gap-2">
      {[1, 2, 3, 4, 5].map(v => (
        <button
          key={v}
          onClick={() => onChange(questionIndex, v)}
          className={`flex h-10 w-10 items-center justify-center rounded-lg border text-sm font-medium transition-all ${
            value === v
              ? 'border-gold bg-gold text-midnight scale-110'
              : 'border-border text-text-secondary hover:border-gold hover:text-gold'
          }`}
          title={LABELS[v - 1]}
        >
          {v}
        </button>
      ))}
    </div>
  )
}
