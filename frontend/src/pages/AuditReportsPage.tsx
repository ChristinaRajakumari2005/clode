import { auditReports } from '../data/mockData'
import { Badge } from '../components/ui/Badge'
import { Button } from '../components/ui/Button'
import { Panel } from '../components/ui/Panel'
import { Table } from '../components/ui/Table'

export function AuditReportsPage() {
  const rows = auditReports.map((report) => [
    report.id,
    report.title,
    report.generatedAt,
    <Badge key={`${report.id}-status`} label={report.status} />,
    <Badge key={`${report.id}-risk`} label={report.riskLevel} level={report.riskLevel} />,
    report.owner,
  ])

  return (
    <div className="space-y-5">
      <header className="flex items-start justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold text-slate-100">Audit Reports</h1>
          <p className="mt-2 text-sm text-slate-400">
            Export-ready governance snapshots and historical compliance evidence.
          </p>
        </div>
        <Button>Create New Report</Button>
      </header>

      <Panel title="Report Registry" subtitle="Latest generated reports">
        <Table
          columns={['ID', 'Title', 'Generated', 'Status', 'Risk', 'Owner']}
          rows={rows}
        />
      </Panel>
    </div>
  )
}
