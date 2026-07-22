import { useMemo, useState } from 'react'
import { analyzeTextContent } from '../../lib/analyzer'
import { Badge } from '../ui/Badge'
import { Button } from '../ui/Button'
import { Panel } from '../ui/Panel'
import { ProgressBar } from '../ui/ProgressBar'

interface AnalyzerWorkspaceProps {
  title: string
  description: string
  inputLabel: string
  placeholder: string
  initialValue?: string
}

export function AnalyzerWorkspace({
  title,
  description,
  inputLabel,
  placeholder,
  initialValue = '',
}: AnalyzerWorkspaceProps) {
  const [text, setText] = useState(initialValue)
  const [version, setVersion] = useState(0)

  const result = useMemo(() => analyzeTextContent(text), [text, version])

  return (
    <div className="space-y-5">
      <header>
        <h1 className="text-2xl font-semibold text-slate-100">{title}</h1>
        <p className="mt-2 text-sm text-slate-400">{description}</p>
      </header>

      <div className="grid gap-5 xl:grid-cols-[1.1fr_0.9fr]">
        <Panel
          title={inputLabel}
          subtitle="This simulation runs fully in the browser with no backend calls."
          actions={<Badge label="Local Analysis" />}
        >
          <textarea
            value={text}
            onChange={(event) => setText(event.target.value)}
            placeholder={placeholder}
            className="h-64 w-full resize-none rounded-xl border border-slate-800 bg-slate-950 p-3 text-sm text-slate-200 outline-none placeholder:text-slate-500 focus:border-brand-500"
          />
          <div className="mt-4 flex gap-3">
            <Button onClick={() => setVersion((value) => value + 1)}>Analyze Content</Button>
            <Button variant="secondary" onClick={() => setText('')}>
              Clear
            </Button>
          </div>
        </Panel>

        <Panel title="Risk Assessment" subtitle="Weighted score across policy dimensions">
          <div className="rounded-xl border border-slate-800 bg-slate-950/70 p-4">
            <div className="mb-2 flex items-center justify-between">
              <p className="text-sm text-slate-300">Overall Risk Score</p>
              <Badge label={result.level} level={result.level} />
            </div>
            <p className="text-3xl font-semibold text-slate-100">{result.score}/100</p>
            <div className="mt-3">
              <ProgressBar value={result.score} />
            </div>
          </div>

          <div className="mt-4 space-y-3">
            {result.findings.length > 0 ? (
              result.findings.map((finding, index) => (
                <article key={`${finding.category}-${index}`} className="rounded-xl border border-slate-800 p-3">
                  <div className="mb-2 flex items-center justify-between">
                    <p className="text-sm font-medium text-slate-100">{finding.category}</p>
                    <Badge label={finding.severity} level={finding.severity} />
                  </div>
                  <p className="text-sm text-slate-300">{finding.insight}</p>
                  <p className="mt-2 text-xs text-slate-400">Recommendation: {finding.recommendation}</p>
                </article>
              ))
            ) : (
              <p className="rounded-xl border border-emerald-500/30 bg-emerald-500/10 p-3 text-sm text-emerald-200">
                No direct high-signal policy concerns were detected.
              </p>
            )}
          </div>
        </Panel>
      </div>
    </div>
  )
}
