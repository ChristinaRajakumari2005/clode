import { useMemo, useState } from 'react'
import { analyzeTextContent } from '../../lib/analyzer'
import type { AnalyzerFinding, RiskLevel } from '../../types/governance'
import { Badge } from '../ui/Badge'
import { Button } from '../ui/Button'
import { Panel } from '../ui/Panel'
import { ProgressBar } from '../ui/ProgressBar'

interface RemoteRiskAssessment {
  score: number
  level: RiskLevel
  findings: AnalyzerFinding[]
}

interface SubmitActionResult {
  responseText: string
  riskAssessment?: RemoteRiskAssessment
}

interface AnalyzerWorkspaceProps {
  title: string
  description: string
  inputLabel: string
  placeholder: string
  initialValue?: string
  submitAction?: (text: string) => Promise<string | SubmitActionResult>
  submitActionLabel?: string
  responsePanelTitle?: string
}

export function AnalyzerWorkspace({
  title,
  description,
  inputLabel,
  placeholder,
  initialValue = '',
  submitAction,
  submitActionLabel = 'Analyze Content',
  responsePanelTitle = 'AI Response',
}: AnalyzerWorkspaceProps) {
  const [text, setText] = useState(initialValue)
  const [version, setVersion] = useState(0)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [submittedResponse, setSubmittedResponse] = useState<string | null>(null)
  const [submitError, setSubmitError] = useState<string | null>(null)
  const [remoteRiskAssessment, setRemoteRiskAssessment] = useState<RemoteRiskAssessment | null>(null)

  const localResult = useMemo(() => analyzeTextContent(text), [text, version])
  const result = remoteRiskAssessment ?? localResult

  const handleAnalyze = async () => {
    setVersion((value) => value + 1)

    if (!submitAction) {
      return
    }

    const trimmed = text.trim()
    if (!trimmed) {
      setSubmittedResponse(null)
      setSubmitError('Please enter a prompt before submitting.')
      return
    }

    setIsSubmitting(true)
    setSubmitError(null)
    try {
      const resultPayload = await submitAction(trimmed)
      if (typeof resultPayload === 'string') {
        setSubmittedResponse(resultPayload)
        setRemoteRiskAssessment(null)
      } else {
        setSubmittedResponse(resultPayload.responseText)
        setRemoteRiskAssessment(resultPayload.riskAssessment ?? null)
      }
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to generate AI response.'
      setSubmittedResponse(null)
      setRemoteRiskAssessment(null)
      setSubmitError(message)
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleClear = () => {
    setText('')
    setSubmittedResponse(null)
    setSubmitError(null)
    setRemoteRiskAssessment(null)
  }

  return (
    <div className="space-y-5">
      <header>
        <h1 className="text-2xl font-semibold text-slate-100">{title}</h1>
        <p className="mt-2 text-sm text-slate-400">{description}</p>
      </header>

      <div className="grid gap-5 xl:grid-cols-[1.1fr_0.9fr]">
        <Panel
          title={inputLabel}
          subtitle={
            submitAction
              ? 'Submits the prompt to backend AI generation and shows risk signals locally.'
              : 'This simulation runs fully in the browser with no backend calls.'
          }
          actions={<Badge label={submitAction ? 'Live API + Local Analysis' : 'Local Analysis'} />}
        >
          <textarea
            value={text}
            onChange={(event) => {
              setText(event.target.value)
              setRemoteRiskAssessment(null)
            }}
            placeholder={placeholder}
            className="h-64 w-full resize-none rounded-xl border border-slate-800 bg-slate-950 p-3 text-sm text-slate-200 outline-none placeholder:text-slate-500 focus:border-brand-500"
          />
          <div className="mt-4 flex gap-3">
            <Button onClick={handleAnalyze} disabled={isSubmitting}>
              {isSubmitting ? 'Submitting...' : submitActionLabel}
            </Button>
            <Button variant="secondary" onClick={handleClear} disabled={isSubmitting}>
              Clear
            </Button>
          </div>

          {submitAction && (
            <div className="mt-4 rounded-xl border border-slate-800 bg-slate-950/70 p-3">
              <p className="text-sm font-medium text-slate-100">{responsePanelTitle}</p>
              {isSubmitting ? (
                <p className="mt-2 text-sm text-slate-400">Generating AI response...</p>
              ) : submitError ? (
                <p className="mt-2 rounded-lg border border-rose-500/30 bg-rose-500/10 p-2 text-sm text-rose-200">
                  {submitError}
                </p>
              ) : submittedResponse ? (
                <p className="mt-2 whitespace-pre-wrap text-sm text-slate-300">{submittedResponse}</p>
              ) : (
                <p className="mt-2 text-sm text-slate-500">Submit a prompt to view generated response.</p>
              )}
            </div>
          )}
        </Panel>

        <Panel
          title="Risk Assessment"
          subtitle={
            remoteRiskAssessment
              ? 'Weighted score from backend workflow risk scoring.'
              : 'Weighted score across policy dimensions.'
          }
        >
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
