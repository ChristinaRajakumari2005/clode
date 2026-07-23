import { useState } from 'react'
import type { AuditReport } from '../../types/governance'
import { Badge } from '../ui/Badge'
import { Button } from '../ui/Button'
import { X, Download, FileText, CheckCircle2, Copy, Check } from 'lucide-react'

interface ReportViewerModalProps {
  report: AuditReport | null
  onClose: () => void
}

export function ReportViewerModal({ report, onClose }: ReportViewerModalProps) {
  const [downloading, setDownloading] = useState<string | null>(null)
  const [copied, setCopied] = useState(false)

  if (!report) return null

  const handleDownload = (format: 'PDF' | 'CSV') => {
    setDownloading(format)
    setTimeout(() => {
      setDownloading(null)
      alert(`Simulated download of ${report.id}_Governance_Report.${format.toLowerCase()} completed!`)
    }, 800)
  }

  const handleCopyId = () => {
    navigator.clipboard.writeText(report.id)
    setCopied(true)
    setTimeout(() => setCopied(false), 1500)
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/85 p-4 backdrop-blur-sm">
      <div className="flex h-full max-h-[90vh] w-full max-w-4xl flex-col overflow-hidden rounded-2xl border border-slate-800 bg-slate-900 shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-800 bg-slate-950/60 px-6 py-4">
          <div className="flex items-center gap-3">
            <div className="rounded-xl border border-brand-500/30 bg-brand-500/10 p-2.5 text-brand-300">
              <FileText size={20} />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-lg font-bold text-slate-100">{report.title}</h2>
                <button
                  onClick={handleCopyId}
                  className="flex items-center gap-1 rounded bg-slate-800 px-2 py-0.5 text-xs text-slate-400 hover:text-slate-200"
                >
                  <span>{copied ? 'Copied!' : report.id}</span>
                  {copied ? <Check size={10} className="text-emerald-400" /> : <Copy size={10} />}
                </button>
              </div>

              <p className="text-xs text-slate-400">
                Generated {report.generatedAt} • Owner: {report.owner}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="rounded-lg border border-slate-800 p-2 text-slate-400 hover:bg-slate-800 hover:text-slate-200"
          >
            <X size={18} />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {/* Metadata Bar */}
          <div className="grid gap-4 sm:grid-cols-3">
            <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-4">
              <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">Report Status</span>
              <div className="mt-2">
                <Badge label={report.status} />
              </div>
            </div>
            <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-4">
              <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">Overall Risk Level</span>
              <div className="mt-2">
                <Badge label={report.riskLevel} level={report.riskLevel} />
              </div>
            </div>
            <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-4">
              <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">Assigned Owner</span>
              <p className="mt-2 text-sm font-semibold text-slate-200">{report.owner}</p>
            </div>
          </div>

          {/* Executive Summary */}
          <div className="rounded-xl border border-slate-800 bg-slate-950/40 p-4">
            <h3 className="text-sm font-semibold text-slate-200 mb-2">Executive Summary</h3>
            <p className="text-sm text-slate-300 leading-relaxed">
              {report.summary ||
                'This audit snapshot provides automated verification results for AI prompt and response telemetry, assessing regulatory compliance and identifying risk exposures across active model deployments.'}
            </p>
          </div>

          {/* Framework Breakdown */}
          {report.frameworkScores && report.frameworkScores.length > 0 && (
            <div>
              <h3 className="text-sm font-semibold text-slate-200 mb-3">Compliance Framework Scores</h3>
              <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
                {report.frameworkScores.map((fw) => (
                  <div key={fw.framework} className="rounded-xl border border-slate-800 bg-slate-950/60 p-3.5">
                    <span className="text-xs text-slate-400">{fw.framework}</span>
                    <div className="mt-2 flex items-baseline justify-between">
                      <span className="text-xl font-bold text-slate-100">{fw.score}%</span>
                      <span className={`text-xs font-semibold ${fw.score >= 90 ? 'text-emerald-400' : 'text-amber-400'}`}>
                        {fw.score >= 90 ? 'Passing' : 'Review'}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Findings Count Breakdown */}
          {report.findingsCount && (
            <div>
              <h3 className="text-sm font-semibold text-slate-200 mb-3">Discovered Findings Breakdown</h3>
              <div className="grid grid-cols-4 gap-3">
                <div className="rounded-xl border border-rose-500/30 bg-rose-500/10 p-3 text-center">
                  <span className="text-2xl font-bold text-rose-300">{report.findingsCount.critical}</span>
                  <p className="text-xs text-rose-400">Critical</p>
                </div>
                <div className="rounded-xl border border-orange-500/30 bg-orange-500/10 p-3 text-center">
                  <span className="text-2xl font-bold text-orange-300">{report.findingsCount.high}</span>
                  <p className="text-xs text-orange-400">High</p>
                </div>
                <div className="rounded-xl border border-amber-500/30 bg-amber-500/10 p-3 text-center">
                  <span className="text-2xl font-bold text-amber-300">{report.findingsCount.moderate}</span>
                  <p className="text-xs text-amber-400">Moderate</p>
                </div>
                <div className="rounded-xl border border-emerald-500/30 bg-emerald-500/10 p-3 text-center">
                  <span className="text-2xl font-bold text-emerald-300">{report.findingsCount.low}</span>
                  <p className="text-xs text-emerald-400">Low</p>
                </div>
              </div>
            </div>
          )}

          {/* Key Recommendations */}
          {report.recommendations && report.recommendations.length > 0 && (
            <div>
              <h3 className="text-sm font-semibold text-slate-200 mb-3">Actionable Remediation Guidance</h3>
              <ul className="space-y-2">
                {report.recommendations.map((rec, i) => (
                  <li key={i} className="flex items-start gap-2.5 rounded-lg border border-slate-800 bg-slate-950/60 p-3 text-xs text-slate-300">
                    <CheckCircle2 size={16} className="mt-0.5 text-brand-400 shrink-0" />
                    <span>{rec}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {/* Footer actions */}
        <div className="flex items-center justify-between border-t border-slate-800 bg-slate-950/80 px-6 py-4">
          <span className="text-xs text-slate-500">Immutable audit hash verified</span>
          <div className="flex items-center gap-3">
            <Button
              variant="secondary"
              onClick={() => handleDownload('CSV')}
              disabled={!!downloading}
            >
              {downloading === 'CSV' ? 'Exporting...' : 'Export CSV'}
            </Button>
            <Button onClick={() => handleDownload('PDF')} disabled={!!downloading}>
              <Download size={14} className="mr-2 inline" />
              {downloading === 'PDF' ? 'Generating PDF...' : 'Download PDF Report'}
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}
