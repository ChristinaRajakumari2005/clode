import { useState } from 'react'
import {
  keyMetrics,
  riskCategoryScores,
  complianceFrameworks,
  recentActivities,
} from '../data/mockData'
import { Badge } from '../components/ui/Badge'
import { Panel } from '../components/ui/Panel'
import { ProgressBar } from '../components/ui/ProgressBar'
import { StatCard } from '../components/dashboard/StatCard'
import { ComplianceFrameworkGrid } from '../components/dashboard/ComplianceFrameworkGrid'
import { ActivityFeed } from '../components/dashboard/ActivityFeed'
import { QuickActions } from '../components/dashboard/QuickActions'
import { Activity, ShieldCheck, AlertTriangle, Clock } from 'lucide-react'


export function DashboardPage() {
  const [timeframe, setTimeframe] = useState<'7d' | '30d' | '90d'>('30d')

  const metricIcons = [
    <Activity key="1" size={18} />,
    <AlertTriangle key="2" size={18} />,
    <ShieldCheck key="3" size={18} />,
    <Clock key="4" size={18} />,
  ]

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <header className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-800/80 pb-5">
        <div>
          <div className="flex items-center gap-2.5">
            <h1 className="text-2xl font-bold tracking-tight text-slate-100">Executive Dashboard</h1>
            <span className="rounded-full bg-brand-500/20 px-2.5 py-0.5 text-xs font-semibold text-brand-300 ring-1 ring-brand-500/30">
              Q3 2026 Live
            </span>
          </div>
          <p className="mt-1 text-xs text-slate-400">
            Real-time compliance monitoring & risk intelligence across active AI pipelines.
          </p>
        </div>

        {/* Timeframe selector */}
        <div className="flex items-center gap-1 rounded-xl border border-slate-800 bg-slate-900/90 p-1">
          {(['7d', '30d', '90d'] as const).map((tf) => (
            <button
              key={tf}
              onClick={() => setTimeframe(tf)}
              className={`rounded-lg px-3 py-1 text-xs font-semibold transition ${
                timeframe === tf ? 'bg-brand-500/20 text-brand-200 ring-1 ring-brand-500/40' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {tf === '7d' ? '7 Days' : tf === '30d' ? '30 Days' : '90 Days'}
            </button>
          ))}
        </div>
      </header>

      {/* Quick Launchpad */}
      <section>
        <p className="mb-2.5 text-xs font-bold uppercase tracking-wider text-slate-400">Quick Actions</p>
        <QuickActions />
      </section>

      {/* Primary KPI Metric Cards */}
      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {keyMetrics.map((metric, idx) => (
          <StatCard
            key={metric.label}
            label={metric.label}
            value={metric.value}
            trend={metric.trend}
            isPositive={metric.isPositive}
            description={metric.description}
            icon={metricIcons[idx]}
          />
        ))}
      </section>

      {/* Compliance Frameworks Health */}
      <section className="space-y-3">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wider">Compliance Framework Baseline</h3>
            <p className="text-xs text-slate-400">Automated audit status against active regulatory standards</p>
          </div>
          <Badge label="All Systems Operational" />
        </div>
        <ComplianceFrameworkGrid frameworks={complianceFrameworks} />
      </section>

      {/* Heatmap & Activity Stream */}
      <section className="grid gap-6 xl:grid-cols-[1fr_420px]">
        {/* Risk Category Progress Bars */}
        <Panel title="Risk Category Heatmap" subtitle="Current weighted risk scores by governance domain">
          <div className="space-y-4">
            {riskCategoryScores.map((item) => (
              <div key={item.category} className="group">
                <div className="mb-1.5 flex items-center justify-between text-xs">
                  <span className="font-semibold text-slate-300 group-hover:text-slate-100">{item.category}</span>
                  <div className="flex items-center gap-2">
                    {item.trend && (
                      <span className={`text-[11px] ${item.trend.startsWith('+') ? 'text-emerald-400' : 'text-slate-400'}`}>
                        {item.trend}
                      </span>
                    )}
                    <span className="font-mono font-bold text-slate-200">{item.score}/100</span>
                  </div>
                </div>
                <ProgressBar value={item.score} />
              </div>
            ))}
          </div>
        </Panel>

        {/* Live Security Feed & Actionable Insights */}
        <Panel title="Live Activity & Audit Stream" subtitle="Recent prompt scans and policy events">
          <ActivityFeed activities={recentActivities} />
        </Panel>
      </section>
    </div>
  )
}

