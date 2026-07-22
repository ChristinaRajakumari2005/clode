interface MetricCardProps {
  label: string
  value: string
  trend: string
}

export function MetricCard({ label, value, trend }: MetricCardProps) {
  const isPositive = trend.startsWith('+')
  return (
    <article className="rounded-xl border border-slate-800 bg-slate-900/70 p-4">
      <p className="text-xs uppercase tracking-wider text-slate-400">{label}</p>
      <p className="mt-2 text-2xl font-semibold text-slate-100">{value}</p>
      <p className={`mt-2 text-sm ${isPositive ? 'text-emerald-400' : 'text-amber-300'}`}>{trend}</p>
    </article>
  )
}
