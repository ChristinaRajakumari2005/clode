export type RiskLevel = 'Low' | 'Moderate' | 'High' | 'Critical'

export interface NavItem {
  label: string
  path: string
}

export interface Metric {
  label: string
  value: string
  trend: string
}

export interface RiskCategoryScore {
  category: string
  score: number
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
}
