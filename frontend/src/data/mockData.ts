import type { AuditReport, Metric, NavItem, RiskCategoryScore } from '../types/governance'

export const navItems: NavItem[] = [
  { label: 'Dashboard', path: '/dashboard' },
  { label: 'Prompt Analyzer', path: '/prompt-analyzer' },
  { label: 'Response Analyzer', path: '/response-analyzer' },
  { label: 'Audit Reports', path: '/audit-reports' },
  { label: 'Settings', path: '/settings' },
]

export const keyMetrics: Metric[] = [
  { label: 'Total Analyses (30d)', value: '12,480', trend: '+14.6%' },
  { label: 'Critical Findings', value: '37', trend: '-6.2%' },
  { label: 'Policy Coverage', value: '96.4%', trend: '+2.3%' },
  { label: 'Avg Resolution SLA', value: '3.8h', trend: '-0.9h' },
]

export const riskCategoryScores: RiskCategoryScore[] = [
  { category: 'Governance', score: 81 },
  { category: 'Compliance', score: 76 },
  { category: 'Privacy', score: 69 },
  { category: 'Hallucination', score: 58 },
  { category: 'Prompt Injection', score: 84 },
  { category: 'Toxicity', score: 35 },
  { category: 'Security', score: 73 },
]

export const auditReports: AuditReport[] = [
  {
    id: 'AR-2026-0712',
    title: 'Quarterly AI Governance Readiness',
    generatedAt: '2026-07-12 09:20 UTC',
    status: 'Ready',
    riskLevel: 'Moderate',
    owner: 'Model Risk Office',
  },
  {
    id: 'AR-2026-0708',
    title: 'Prompt Injection Exposure Review',
    generatedAt: '2026-07-08 14:55 UTC',
    status: 'Needs Review',
    riskLevel: 'High',
    owner: 'Security Engineering',
  },
  {
    id: 'AR-2026-0702',
    title: 'PII Leakage Compliance Snapshot',
    generatedAt: '2026-07-02 11:10 UTC',
    status: 'Draft',
    riskLevel: 'Critical',
    owner: 'Privacy Office',
  },
  {
    id: 'AR-2026-0628',
    title: 'Safety and Toxicity Trend Analysis',
    generatedAt: '2026-06-28 08:45 UTC',
    status: 'Ready',
    riskLevel: 'Low',
    owner: 'Responsible AI Team',
  },
]
