import { useEffect, useMemo, useState } from 'react'
import { auditReports } from '../data/mockData'
import type { AuditReport } from '../types/governance'
import { Badge } from '../components/ui/Badge'
import { Button } from '../components/ui/Button'
import { Panel } from '../components/ui/Panel'
import { Table } from '../components/ui/Table'
import { ReportViewerModal } from '../components/reports/ReportViewerModal'
import { Eye, FilePlus, Filter } from 'lucide-react'
import {
  GENERATED_AUDIT_REPORTS_UPDATED_EVENT,
  loadGeneratedAuditReports,
} from '../lib/auditReportStore'

export function AuditReportsPage() {
  const [selectedReport, setSelectedReport] = useState<AuditReport | null>(null)
  const [statusFilter, setStatusFilter] = useState<'All' | 'Ready' | 'Needs Review' | 'Draft'>('All')
  const [generatedReports, setGeneratedReports] = useState<AuditReport[]>(() => loadGeneratedAuditReports())

  useEffect(() => {
    const refreshReports = () => setGeneratedReports(loadGeneratedAuditReports())

    window.addEventListener(GENERATED_AUDIT_REPORTS_UPDATED_EVENT, refreshReports)
    window.addEventListener('storage', refreshReports)
    return () => {
      window.removeEventListener(GENERATED_AUDIT_REPORTS_UPDATED_EVENT, refreshReports)
      window.removeEventListener('storage', refreshReports)
    }
  }, [])

  const allReports = useMemo(
    () => [...generatedReports, ...auditReports],
    [generatedReports],
  )

  const filteredReports = allReports.filter(
    (rep) => statusFilter === 'All' || rep.status === statusFilter,
  )

  const rows = filteredReports.map((report) => [
    <span key={`${report.id}-id`} className="font-mono text-xs font-semibold text-brand-300">
      {report.id}
    </span>,
    <span key={`${report.id}-title`} className="font-medium text-slate-100">
      {report.title}
    </span>,
    report.generatedAt,
    <Badge key={`${report.id}-status`} label={report.status} />,
    <Badge key={`${report.id}-risk`} label={report.riskLevel} level={report.riskLevel} />,
    report.owner,
    <Button
      key={`${report.id}-action`}
      variant="secondary"
      onClick={() => setSelectedReport(report)}
    >
      <Eye size={14} className="mr-1.5 inline" /> View Report
    </Button>,
  ])

  return (
    <div className="space-y-6">
      <header className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-800/80 pb-5">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-100">Audit Reports & Evidence Registry</h1>
          <p className="mt-1 text-xs text-slate-400">
            Export-ready governance snapshots, regulatory compliance evidence, and historical audit logs.
          </p>
        </div>
        <Button onClick={() => setSelectedReport(allReports[0] ?? null)}>
          <FilePlus size={16} className="mr-2 inline" /> Create New Report Snapshot
        </Button>
      </header>

      {/* Filter Tabs */}
      <div className="flex items-center gap-2">
        <Filter size={14} className="text-slate-400 mr-1" />
        {(['All', 'Ready', 'Needs Review', 'Draft'] as const).map((filter) => (
          <button
            key={filter}
            onClick={() => setStatusFilter(filter)}
            className={`rounded-xl px-3 py-1.5 text-xs font-semibold transition ${
              statusFilter === filter
                ? 'bg-brand-500/20 text-brand-200 ring-1 ring-brand-500/30'
                : 'bg-slate-900/80 text-slate-400 hover:text-slate-200'
            }`}
          >
            {filter}
          </button>
        ))}
      </div>

      <Panel title="Report Registry" subtitle="Click any report row or 'View Report' button for full compliance breakdown">
        <Table
          columns={['ID', 'Title', 'Generated', 'Status', 'Risk Level', 'Owner', 'Actions']}
          rows={rows}
        />
      </Panel>

      {/* Interactive Full Report Viewer Modal */}
      <ReportViewerModal report={selectedReport} onClose={() => setSelectedReport(null)} />
    </div>
  )
}
