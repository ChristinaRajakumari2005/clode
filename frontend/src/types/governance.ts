export type RiskLevel = 'Low' | 'Moderate' | 'High' | 'Critical'

export interface NavItem {
  label: string
  path: string
  category?: 'Overview' | 'Analyzers' | 'Governance' | 'System'
  icon?: string
}

export interface Metric {
  label: string
  value: string
  trend: string
  isPositive?: boolean
  description?: string
}

export interface RiskCategoryScore {
  category: string
  score: number
  trend?: string
}

export interface AnalyzerFinding {
  category: string
  severity: RiskLevel
  insight: string
  recommendation: string
}

export interface AnalyzerResult {
  score: number
  level: RiskLevel
  findings: AnalyzerFinding[]
}

export interface AuditReport {
  id: string
  title: string
  generatedAt: string
  status: 'Ready' | 'Draft' | 'Needs Review'
  riskLevel: RiskLevel
  owner: string
  summary?: string
  frameworkScores?: { framework: string; score: number }[]
  findingsCount?: { critical: number; high: number; moderate: number; low: number }
  recommendations?: string[]
}

export interface ActivityItem {
  id: string
  type: 'Prompt Scan' | 'Response Scan' | 'Policy Update' | 'Report Generated' | 'Security Alert'
  title: string
  timestamp: string
  severity: RiskLevel
  user: string
  details: string
}

export interface ComplianceFramework {
  id: string
  name: string
  code: string
  score: number
  status: 'Compliant' | 'At Risk' | 'Non-Compliant'
  controlsPassed: number
  totalControls: number
  lastAudited: string
}

export interface NotificationItem {
  id: string
  title: string
  message: string
  timestamp: string
  read: boolean
  type: 'alert' | 'info' | 'warning'
}

