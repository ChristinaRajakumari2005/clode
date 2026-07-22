import { ArrowUpRight } from 'lucide-react'
import { keyMetrics, riskCategoryScores } from '../data/mockData'
import { Badge } from '../components/ui/Badge'
import { MetricCard } from '../components/ui/MetricCard'
import { Panel } from '../components/ui/Panel'
import { ProgressBar } from '../components/ui/ProgressBar'

export function DashboardPage() {
  return (
    <div className="space-y-5">
      <header className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold text-slate-100">Dashboard</h1>
          <p className="mt-2 text-sm text-slate-400">
            Unified governance and compliance visibility for AI prompt/response workflows.
          </p>
        </div>
        <Badge label="Compliance Window: Q3 2026" />
      </header>

      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {keyMetrics.map((metric) => (
          <MetricCard key={metric.label} label={metric.label} value={metric.value} trend={metric.trend} />
        ))}
      </section>

      <section className="grid gap-5 xl:grid-cols-[1fr_340px]">
        <Panel title="Risk Category Heatmap" subtitle="Current weighted risk scores by domain">
          <div className="space-y-4">
            {riskCategoryScores.map((item) => (
              <div key={item.category}>
                <div className="mb-2 flex items-center justify-between text-sm">
                  <span className="text-slate-300">{item.category}</span>
                  <span className="font-medium text-slate-200">{item.score}</span>
                </div>
                <ProgressBar value={item.score} />
              </div>
            ))}
          </div>
        </Panel>

        <Panel title="Governance Posture" subtitle="Actionable highlights for this week">
          <div className="space-y-3">
            {[
              '3 critical findings require policy owner sign-off.',
              'Prompt injection controls improved by 11% from prior period.',
              'Two audit reports are pending legal/compliance review.',
            ].map((insight) => (
              <article
                key={insight}
                className="flex items-start gap-2 rounded-xl border border-slate-800 bg-slate-950/70 p-3"
              >
                <ArrowUpRight size={16} className="mt-0.5 text-brand-300" />
                <p className="text-sm text-slate-300">{insight}</p>
              </article>
            ))}
          </div>
        </Panel>
      </section>
    </div>
  )
}
