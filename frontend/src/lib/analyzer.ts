import type { AnalyzerFinding, AnalyzerResult, RiskLevel } from '../types/governance'

interface Rule {
  category: string
  severity: RiskLevel
  keywords: string[]
  insight: string
  recommendation: string
}

const rules: Rule[] = [
  {
    category: 'Privacy',
    severity: 'Critical',
    keywords: ['ssn', 'passport', 'credit card', 'personal email'],
    insight: 'Potential personally identifiable information appears in text.',
    recommendation: 'Mask identifiers and enforce strict data minimization before sharing.',
  },
  {
    category: 'Prompt Injection',
    severity: 'High',
    keywords: ['ignore previous instructions', 'override policy', 'system prompt'],
    insight: 'Instruction override patterns indicate possible prompt injection.',
    recommendation: 'Harden prompt templates and block privileged instruction tokens.',
  },
  {
    category: 'Hallucination',
    severity: 'Moderate',
    keywords: ['definitely guaranteed', '100% accurate', 'no doubt'],
    insight: 'Overconfident language can signal unverifiable claims.',
    recommendation: 'Require source-backed assertions and confidence qualifiers.',
  },
  {
    category: 'Toxicity',
    severity: 'High',
    keywords: ['hate', 'idiot', 'worthless'],
    insight: 'Abusive or harmful language detected.',
    recommendation: 'Apply safety rewrite and toxicity moderation policies.',
  },
  {
    category: 'Security',
    severity: 'High',
    keywords: ['api key', 'secret token', 'private key'],
    insight: 'Sensitive credential patterns were detected.',
    recommendation: 'Redact secrets and enforce secure secret management controls.',
  },
]

const severityScoreMap: Record<RiskLevel, number> = {
  Low: 8,
  Moderate: 16,
  High: 24,
  Critical: 32,
}

function mapRiskLevel(score: number): RiskLevel {
  if (score >= 80) return 'Critical'
  if (score >= 60) return 'High'
  if (score >= 35) return 'Moderate'
  return 'Low'
}

export function analyzeTextContent(text: string): AnalyzerResult {
  const normalized = text.toLowerCase()
  const findings: AnalyzerFinding[] = []
  let score = 10

  for (const rule of rules) {
    if (rule.keywords.some((keyword) => normalized.includes(keyword))) {
      findings.push({
        category: rule.category,
        severity: rule.severity,
        insight: rule.insight,
        recommendation: rule.recommendation,
      })
      score += severityScoreMap[rule.severity]
    }
  }

  if (text.length > 1200) {
    findings.push({
      category: 'Governance',
      severity: 'Moderate',
      insight: 'Long-form content may exceed approved context handling boundaries.',
      recommendation: 'Segment input and attach contextual governance metadata.',
    })
    score += 12
  }

  const boundedScore = Math.min(score, 100)
  return {
    score: boundedScore,
    level: mapRiskLevel(boundedScore),
    findings,
  }
}
