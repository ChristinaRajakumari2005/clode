import type { ComplianceFramework } from '../../types/governance'
import { Badge } from '../ui/Badge'
import { CheckCircle2, AlertTriangle, FileSearch } from 'lucide-react'


interface ComplianceFrameworkGridProps {
  frameworks: ComplianceFramework[]
}

export function ComplianceFrameworkGrid({ frameworks }: ComplianceFrameworkGridProps) {
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5">
      {frameworks.map((fw) => {
        const isHigh = fw.score >= 90
        const isMed = fw.score >= 80 && fw.score < 90

        return (
          <div
            key={fw.id}
            className="group relative flex flex-col justify-between rounded-2xl border border-slate-800 bg-slate-900/70 p-4 transition-all hover:border-brand-500/40 hover:bg-slate-900"
          >
            <div>
              <div className="flex items-center justify-between gap-2">
                <span className="text-[11px] font-bold uppercase tracking-wider text-brand-400">{fw.code}</span>
                <Badge
                  label={fw.status}
                  level={fw.status === 'Compliant' ? 'Low' : fw.status === 'At Risk' ? 'High' : 'Critical'}
                />
              </div>

              <h4 className="mt-2 text-sm font-semibold text-slate-100 group-hover:text-brand-200 line-clamp-1">
                {fw.name}
              </h4>

              <div className="mt-4 flex items-baseline justify-between">
                <span className="text-2xl font-bold text-slate-100">{fw.score}%</span>
                <span className="text-xs text-slate-400">
                  {fw.controlsPassed}/{fw.totalControls} Controls
                </span>
              </div>

              {/* Progress bar */}
              <div className="mt-2 h-1.5 w-full overflow-hidden rounded-full bg-slate-800">
                <div
                  className={`h-full rounded-full transition-all duration-500 ${
                    isHigh ? 'bg-emerald-400' : isMed ? 'bg-brand-400' : 'bg-amber-400'
                  }`}
                  style={{ width: `${fw.score}%` }}
                />
              </div>
            </div>

            <div className="mt-4 flex items-center justify-between border-t border-slate-800/80 pt-3 text-[11px] text-slate-400">
              <span className="flex items-center gap-1">
                {fw.status === 'Compliant' ? (
                  <CheckCircle2 size={12} className="text-emerald-400" />
                ) : (
                  <AlertTriangle size={12} className="text-amber-400" />
                )}
                Audited {fw.lastAudited}
              </span>
              <FileSearch size={12} className="text-slate-500 group-hover:text-slate-300" />
            </div>
          </div>
        )
      })}
    </div>
  )
}
