import clsx from 'clsx'
import type { RiskLevel } from '../../types/governance'

interface BadgeProps {
  label: string
  level?: RiskLevel | 'info'
}

const styles: Record<NonNullable<BadgeProps['level']>, string> = {
  Low: 'bg-emerald-500/15 text-emerald-300 ring-emerald-500/30',
  Moderate: 'bg-amber-500/15 text-amber-300 ring-amber-500/30',
  High: 'bg-orange-500/15 text-orange-300 ring-orange-500/30',
  Critical: 'bg-rose-500/15 text-rose-300 ring-rose-500/30',
  info: 'bg-brand-500/15 text-brand-300 ring-brand-500/30',
}

export function Badge({ label, level = 'info' }: BadgeProps) {
  return (
    <span
      className={clsx(
        'inline-flex items-center rounded-full px-2.5 py-1 text-xs font-medium ring-1 ring-inset',
        styles[level],
      )}
    >
      {label}
    </span>
  )
}
