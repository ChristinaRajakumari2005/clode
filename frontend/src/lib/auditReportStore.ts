import type { AuditReport, RiskLevel } from '../types/governance'

const GENERATED_AUDIT_REPORTS_KEY = 'ai-governance-generated-audit-reports'
export const GENERATED_AUDIT_REPORTS_UPDATED_EVENT = 'generated-audit-reports-updated'

function normalizeRiskLevel(level: string | undefined): RiskLevel {
  const value = (level ?? '').toLowerCase()
  if (value === 'critical') return 'Critical'
  if (value === 'high') return 'High'
  if (value === 'medium' || value === 'moderate') return 'Moderate'
  return 'Low'
}

export function mapAuditStatus(overallStatus: string | undefined): AuditReport['status'] {
  const value = (overallStatus ?? '').toUpperCase()
  if (value === 'PASS') return 'Ready'
  if (value === 'WARNING') return 'Needs Review'
  if (value === 'FAIL') return 'Needs Review'
  return 'Draft'
}

export function mapAuditReportFromBackend(payload: {
  report_id: string
  generated_at: string
  overall_status: string
  executive_summary: string
  risk_level: string
  recommendations?: string[]
}): AuditReport {
  return {
    id: payload.report_id,
    title: `Workflow Audit Snapshot ${payload.report_id.slice(0, 8)}`,
    generatedAt: new Date(payload.generated_at).toISOString().replace('T', ' ').replace('.000Z', ' UTC'),
    status: mapAuditStatus(payload.overall_status),
    riskLevel: normalizeRiskLevel(payload.risk_level),
    owner: 'Workflow Automation',
    summary: payload.executive_summary,
    recommendations: payload.recommendations ?? [],
  }
}

export function loadGeneratedAuditReports(): AuditReport[] {
  try {
    const raw = window.localStorage.getItem(GENERATED_AUDIT_REPORTS_KEY)
    if (!raw) return []
    const parsed = JSON.parse(raw) as AuditReport[]
    return Array.isArray(parsed) ? parsed : []
  } catch {
    return []
  }
}

export function saveGeneratedAuditReport(report: AuditReport): void {
  const existing = loadGeneratedAuditReports()
  const deduped = [report, ...existing.filter((item) => item.id !== report.id)]
  window.localStorage.setItem(GENERATED_AUDIT_REPORTS_KEY, JSON.stringify(deduped))
  window.dispatchEvent(new CustomEvent(GENERATED_AUDIT_REPORTS_UPDATED_EVENT))
}
