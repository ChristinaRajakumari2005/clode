import type { ReactNode } from 'react'

interface StatCardProps {
  label: string
  value: string
  trend: string
  isPositive?: boolean
  description?: string
  icon?: ReactNode
}

export function StatCard({ label, value, trend, isPositive = true, description, icon }: StatCardProps) {
  return (
    <div className="group relative overflow-hidden rounded-2xl border border-slate-800 bg-slate-900/80 p-5 shadow-panel backdrop-blur transition-all duration-200 hover:border-slate-700 hover:bg-slate-900">
      {/* Top accent glow line */}
      <div className="absolute inset-x-0 top-0 h-0.5 bg-gradient-to-r from-transparent via-brand-500/40 to-transparent opacity-0 transition-opacity duration-300 group-hover:opacity-100" />

      <div className="flex items-center justify-between">
        <span className="text-xs font-medium uppercase tracking-wider text-slate-400">{label}</span>
        {icon && (
          <div className="rounded-xl border border-slate-800 bg-slate-950/80 p-2.5 text-brand-400 transition-colors group-hover:border-brand-500/30 group-hover:bg-brand-500/10">
            {icon}
          </div>
        )}
      </div>

      <div className="mt-4 flex items-baseline gap-3">
        <p className="text-3xl font-bold tracking-tight text-slate-100">{value}</p>
        <span
          className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-semibold ${
            isPositive
              ? 'border border-emerald-500/30 bg-emerald-500/10 text-emerald-300'
              : 'border border-rose-500/30 bg-rose-500/10 text-rose-300'
          }`}
        >
          {trend}
        </span>
      </div>

      {description && <p className="mt-2 text-xs text-slate-400">{description}</p>}

      {/* Decorative Sparkline simulation */}
      <div className="mt-4 flex items-end gap-1 pt-2 opacity-60 transition-opacity group-hover:opacity-100">
        <div className="h-2 w-full rounded-full bg-brand-500/20">
          <div className="h-full w-3/4 rounded-full bg-gradient-to-r from-brand-500 to-cyan-400" />
        </div>
      </div>
    </div>
  )
}
