import { AnalyzerWorkspace } from '../components/analysis/AnalyzerWorkspace'
import {
  mapAuditReportFromBackend,
  saveGeneratedAuditReport,
} from '../lib/auditReportStore'
import type { AnalyzerFinding, RiskLevel } from '../types/governance'

interface AnalyzeResponseCategoryResult {
  detected: boolean
  confidence: number
  risk_level: string
  explanation: string
}

interface AnalyzeResponseResult {
  is_safe: boolean
  risk_score: number
  risk_level: string
  summary: string
  flagged_categories: string[]
  categories: Record<string, AnalyzeResponseCategoryResult>
  sanitized_response: string
}

interface ResponseWorkflowResult {
  responseText: string
  riskAssessment: {
    score: number
    level: RiskLevel
    findings: AnalyzerFinding[]
  }
}

interface GenerateAuditReportResult {
  report_id: string
  generated_at: string
  overall_status: string
  executive_summary: string
  overall_risk_score: number
  risk_level: string
  recommendations: string[]
}

function normalizeRiskLevel(level: string): RiskLevel {
  const value = level.toLowerCase()
  if (value === 'critical') return 'Critical'
  if (value === 'high') return 'High'
  if (value === 'medium' || value === 'moderate') return 'Moderate'
  return 'Low'
}

function formatCategoryName(category: string): string {
  return category
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (char) => char.toUpperCase())
}

function mapAnalysisFindings(result: AnalyzeResponseResult): AnalyzerFinding[] {
  const findings: AnalyzerFinding[] = [
    {
      category: 'Response Analysis Summary',
      severity: normalizeRiskLevel(result.risk_level),
      insight: result.summary,
      recommendation: result.is_safe
        ? 'No high-risk behavior detected in this response.'
        : 'Review flagged categories and apply the recommended controls.',
    },
  ]

  for (const [categoryName, categoryResult] of Object.entries(result.categories)) {
    if (!categoryResult.detected) continue
    findings.push({
      category: formatCategoryName(categoryName),
      severity: normalizeRiskLevel(categoryResult.risk_level),
      insight: categoryResult.explanation,
      recommendation: `Inspect ${formatCategoryName(categoryName)} output and mitigate before release.`,
    })
  }

  return findings
}

async function postJson<TResponse>(path: string, body: unknown): Promise<TResponse> {
  const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000'
  const response = await fetch(`${apiBaseUrl}${path}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(body),
  })

  if (!response.ok) {
    throw new Error(`Request to ${path} failed with status ${response.status}.`)
  }

  return (await response.json()) as TResponse
}

async function analyzeResponseWorkflow(text: string): Promise<ResponseWorkflowResult> {
  const analysis = await postJson<AnalyzeResponseResult>('/analyze-response', {
    response: text,
  })

  const report = await postJson<GenerateAuditReportResult>('/generate-audit-report', {
    response_analysis: analysis,
  })
  saveGeneratedAuditReport(mapAuditReportFromBackend(report))

  return {
    responseText: analysis.sanitized_response || text,
    riskAssessment: {
      score: Math.round(analysis.risk_score * 100),
      level: normalizeRiskLevel(analysis.risk_level),
      findings: mapAnalysisFindings(analysis),
    },
  }
}

export function ResponseAnalyzerPage() {
  return (
    <AnalyzerWorkspace
      title="Response Analyzer"
      description="Inspect generated model responses for hallucinations, toxicity, security leakage, and regulatory concerns."
      inputLabel="Model Response Input"
      placeholder="Paste generated AI response content to review..."
      initialValue="This recommendation is 100% accurate with no doubt. Customer SSN is 111-22-3333 and API key is sk-test-private."
      submitAction={analyzeResponseWorkflow}
      submitActionLabel="Analyze Response"
      responsePanelTitle="Sanitized Response Output"
    />
  )
}
