interface ProgressBarProps {
  value: number
}

export function ProgressBar({ value }: ProgressBarProps) {
  const normalized = Math.max(0, Math.min(100, value))
  const color =
    normalized >= 80
      ? 'bg-rose-500'
      : normalized >= 60
        ? 'bg-orange-500'
        : normalized >= 35
          ? 'bg-amber-500'
          : 'bg-emerald-500'

  return (
    <div className="h-2 w-full rounded-full bg-slate-800">
      <div className={`h-2 rounded-full ${color}`} style={{ width: `${normalized}%` }} />
    </div>
  )
}
