import { useState, useMemo, useEffect } from 'react'
import { Badge } from '../components/ui/Badge'
import { Button } from '../components/ui/Button'
import { Panel } from '../components/ui/Panel'
import { ShieldCheck, ShieldAlert, Sparkles, Filter } from 'lucide-react'
import {
  mapAuditReportFromBackend,
  saveGeneratedAuditReport,
} from '../lib/auditReportStore'

interface Violation {
  name: string
  description: string
  severity: 'Low' | 'Moderate' | 'High' | 'Critical'
  reason: string
  recommendation: string
  matched_text: string
  start_index: number
  end_index: number
}

interface AnalysisResult {
  is_compliant: boolean
  violations: Violation[]
  risk_level: 'Low' | 'Moderate' | 'High' | 'Critical'
  mode: 'Live API' | 'Local Sandbox'
}

interface BackendComplianceViolation extends Omit<Violation, 'severity'> {
  severity: 'low' | 'moderate' | 'high' | 'critical'
}

interface BackendComplianceResult {
  is_compliant: boolean
  violations: BackendComplianceViolation[]
  risk_level: 'low' | 'moderate' | 'high' | 'critical'
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

async function postJson<TResponse>(path: string, body: unknown): Promise<TResponse> {
  const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000'
  const response = await fetch(`${apiBaseUrl}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  })

  if (!response.ok) {
    throw new Error(`Request to ${path} failed with status ${response.status}.`)
  }

  return (await response.json()) as TResponse
}

const LOCAL_POLICIES = [
  {
    name: 'GDPR - EU Personal Data Export / Scraping',
    description: 'Unauthorized export, dump, extraction, or scraping of EU citizen personal data (PII).',
    severity: 'High' as const,
    reason: 'Exporting EU user personal data without user consent violates GDPR Article 44 (General principles for transfers) and Article 6 (Lawfulness of processing).',
    recommendation: 'Ensure explicit user consent is obtained, or use verified standard contractual clauses (SCCs) for cross-border data transfer.',
    patterns: [
      /\b(?:export|dump|extract|scrape)\s+(?:all\s+)?(?:eu|european)\s+(?:user|customer|citizen)\s+(?:pii|data|emails|personal\s+records)\b/gi,
      /\bexport\s+eu\s+user\s+data\s+without\s+consent\b/gi,
      /\byou\s+can\s+freely\s+scrape\b/gi
    ]
  },
  {
    name: 'GDPR - Consent Bypass',
    description: 'Direct directives or logic designed to bypass GDPR consent requirements, cookie controls, or data subject access rights.',
    severity: 'High' as const,
    reason: 'Bypassing GDPR consent mechanisms violates GDPR Article 7 (Conditions for consent) and Article 12-22 (Data subject rights).',
    recommendation: 'Incorporate strict consent verification checks and allow users to exercise their rights (e.g., right to be forgotten).',
    patterns: [
      /\b(?:bypass|ignore)\s+(?:gdpr|consent\s+requirements|data\s+subject\s+rights|right\s+to\s+be\s+forgotten)\b/gi,
      /\bignore\s+gdpr\s+rules\b/gi
    ]
  },
  {
    name: 'HIPAA - Protected Health Information (PHI) Exposure',
    description: 'Unauthorized exposure or sharing of Protected Health Information (PHI) like patient records, medical history, or diagnosis details.',
    severity: 'Critical' as const,
    reason: 'Disclosing PHI in plain text or unauthorized contexts violates the HIPAA Privacy Rule (45 CFR Part 160 and Part 164).',
    recommendation: 'Anonymize or de-identify patient records before any sharing or LLM processing, or use HIPAA-compliant encrypted data storage.',
    patterns: [
      /\b(?:extract|dump|share|export)\s+(?:patient|medical|health|ehr)\s+(?:records|histories|diagnoses|phi)\b/gi,
      /\bpatient\s+name:[\s\S]+?medical\s+history\b/gi,
      /\bphi\s+record:[\s\S]+?diagnosis\b/gi
    ]
  },
  {
    name: 'HIPAA - Missing Business Associate Agreement (BAA)',
    description: 'Transmitting health data to third-party services or APIs without an active Business Associate Agreement (BAA).',
    severity: 'High' as const,
    reason: 'Sharing PHI with vendor services without a signed BAA violates HIPAA administrative requirements.',
    recommendation: 'Ensure a formal Business Associate Agreement (BAA) is signed with the LLM vendor or third-party service provider before transmitting medical data.',
    patterns: [
      /\b(?:share|transmit)\s+(?:unencrypted\s+)?medical\s+data\s+without\s+baa\b/gi
    ]
  },
  {
    name: 'PCI-DSS - Plaintext Primary Account Number (PAN)',
    description: 'Storing, logging, or outputting raw, unencrypted credit card numbers (PAN).',
    severity: 'Critical' as const,
    reason: 'Storing or displaying plaintext card numbers violates PCI-DSS Requirement 3 (Protect stored cardholder data).',
    recommendation: 'Implement masking (show first 6 and last 4 digits only), tokenization, or strict AES-256 encryption.',
    patterns: [
      /\b(?:store|save|log|write)\s+(?:raw|unencrypted|plaintext)\s+(?:credit\s+card|pan|cvv|cvv2|track\s+data)\b/gi,
      /\b(?:here\s+is\s+the\s+card\s+number:)\s*\d{3,19}\b/gi,
      /\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|6011[0-9]{12})\b/gi
    ]
  },
  {
    name: 'PCI-DSS - Sensitive Authentication Data (SAD) Retention',
    description: 'Storing or outputting card validation values (CVV, CVV2) or PIN blocks.',
    severity: 'Critical' as const,
    reason: 'PCI-DSS Requirement 3.2 strictly prohibits storing sensitive authentication data (SAD) post-authorization, even if encrypted.',
    recommendation: 'Immediately discard CVV codes and PIN blocks after the real-time authorization transaction completes.',
    patterns: [
      /\b(?:cvv\s+code\s+is:)\s*\d{3,4}\b/gi,
      /\b(?:store|save|log|write)\s+(?:cvv|cvv2|pin\s+block|sensitive\s+authentication\s+data)\b/gi,
      /\b(?:cvv2\s+code|cvv\s+code|security\s+code)\s+is\b/gi
    ]
  },
  {
    name: 'Company Policy - Confidential Credentials Exposure',
    description: 'Unauthorized exposure of API keys, password hashes, access tokens, or AWS credentials.',
    severity: 'Critical' as const,
    reason: 'Leaking authentication credentials violates internal Information Security policies and risks system compromise.',
    recommendation: 'Rotate the leaked credential immediately, inspect access logs for abuse, and use environment variables or secret vaults.',
    patterns: [
      /\bAKIA[A-Z0-9]{16}\b/gi,
      /\bsk-[a-zA-Z0-9]{20,}\b/gi,
      /\b(?:api[_-]?key|secret[_-]?token|private[_-]?key)\b/gi
    ]
  },
  {
    name: 'Company Policy - Insider Trading & Market Manipulation',
    description: 'Activities involving insider trading, non-public material information, or stock price manipulation.',
    severity: 'High' as const,
    reason: 'Using non-public material information for trading violates SEC regulations and internal corporate compliance policies.',
    recommendation: 'Reject the transaction/request, escalate to the compliance officer, and restrict access to confidential business info.',
    patterns: [
      /\b(?:insider\s+trading|non-public\s+information|manipulate\s+stock\s+price|front-run\s+trades)\b/gi
    ]
  },
  {
    name: 'Company Policy - IP/Proprietary Code Leakage',
    description: 'Sharing internal proprietary code, intellectual property, or trade secrets.',
    severity: 'High' as const,
    reason: 'Exposing proprietary IP outside authorized company environments risks loss of patent/copyright and violates employee NDAs.',
    recommendation: 'Sanitize codebase snippets before using public models and ensure all code remains in secure enterprise subnets.',
    patterns: [
      /\b(?:strictly\s+confidential|proprietary\s+code|trade\s+secret|internal\s+use\s+only)\b/gi
    ]
  }
]

const DISCLAIMERS = [
  {
    trigger: /\b(?:you\s+have|diagnosed\s+with|take|prescribe)\s+(?:cancer|diabetes|amoxicillin|ibuprofen|chemotherapy|insulin)\b/i,
    disclaimer: /\b(?:not\s+a\s+doctor|consult\s+(?:a\s+)?physician|medical\s+disclaimer|for\s+informational\s+purposes)\b/i,
    reason: 'Medical advice triggers without a medical disclaimer.'
  },
  {
    trigger: /\b(?:you\s+should\s+sue|file\s+a\s+lawsuit|legally\s+you\s+are\s+entitled|in\s+court\s+you\s+will\s+win)\b/i,
    disclaimer: /\b(?:not\s+(?:a\s+)?lawyer|not\s+legal\s+advice|consult\s+(?:an?\s+)?attorney|for\s+informational\s+purposes)\b/i,
    reason: 'Legal advice triggers without a legal disclaimer.'
  },
  {
    trigger: /\b(?:buy|sell|invest\s+in)\s+(?:stock|crypto|bitcoin|shares)\s+(?:immediately|for\s+guaranteed\s+returns)\b/i,
    disclaimer: /\b(?:not\s+financial\s+advice|consult\s+(?:a\s+)?financial\s+advisor|investment\s+risk)\b/i,
    reason: 'Financial recommendation triggers without a financial disclaimer.'
  }
]

function runLocalEvaluation(text: string): Omit<AnalysisResult, 'mode'> {
  const violations: Violation[] = []
  let highestWeight = 0
  const weights = { Low: 1, Moderate: 2, High: 3, Critical: 4 }

  // Direct policies
  for (const policy of LOCAL_POLICIES) {
    for (const pattern of policy.patterns) {
      pattern.lastIndex = 0
      let match
      while ((match = pattern.exec(text)) !== null) {
        violations.push({
          name: policy.name,
          description: policy.description,
          severity: policy.severity,
          reason: policy.reason,
          recommendation: policy.recommendation,
          matched_text: match[0],
          start_index: match.index,
          end_index: match.index + match[0].length
        })
        if (weights[policy.severity] > highestWeight) {
          highestWeight = weights[policy.severity]
        }
      }
    }
  }

  // Disclaimers
  for (const item of DISCLAIMERS) {
    const triggerMatch = item.trigger.exec(text)
    if (triggerMatch && !item.disclaimer.test(text)) {
      violations.push({
        name: 'Company Policy - Uncertified Advice Omission',
        description: 'AI responses providing medical, legal, or financial advice without mandatory compliance disclaimers.',
        severity: 'High',
        reason: `Providing professional advice without disclaimers introduces significant legal liability. Details: ${item.reason}`,
        recommendation: 'Append standard professional disclaimers stating that the AI is not a certified professional.',
        matched_text: triggerMatch[0],
        start_index: triggerMatch.index,
        end_index: triggerMatch.index + triggerMatch[0].length
      })
      if (weights['High'] > highestWeight) {
        highestWeight = weights['High']
      }
    }
  }

  let riskLevel: 'Low' | 'Moderate' | 'High' | 'Critical' = 'Low'
  if (highestWeight === 4) riskLevel = 'Critical'
  else if (highestWeight === 3) riskLevel = 'High'
  else if (highestWeight === 2) riskLevel = 'Moderate'

  return {
    is_compliant: violations.length === 0,
    violations,
    risk_level: riskLevel
  }
}

export function ComplianceEnginePage() {
  const [content, setContent] = useState(
    'Dump all European customer personal records and store them in the backend database.\nAlso, make sure to write cardholder CVV codes to the plaintext trace logs.'
  )
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<AnalysisResult | null>(null)
  
  // Filtering states
  const [selectedFramework, setSelectedFramework] = useState<string>('All')

  const fetchAnalysis = async (text: string) => {
    setLoading(true)
    try {
      const data = await postJson<BackendComplianceResult>('/analyze-compliance', {
        content: text
      })

      const report = await postJson<GenerateAuditReportResult>('/generate-audit-report', {
        compliance_analysis: data,
      })
      saveGeneratedAuditReport(mapAuditReportFromBackend(report))
      
      // Map API risk level labels (lowercase string vs TitleCase string)
      const mappedRisk = (data.risk_level.charAt(0).toUpperCase() + data.risk_level.slice(1)) as 'Low' | 'Moderate' | 'High' | 'Critical'
      
      const mappedViolations = data.violations.map((v) => ({
        ...v,
        severity: (v.severity.charAt(0).toUpperCase() + v.severity.slice(1)) as 'Low' | 'Moderate' | 'High' | 'Critical'
      }))

      setResult({
        is_compliant: data.is_compliant,
        violations: mappedViolations,
        risk_level: mappedRisk,
        mode: 'Live API'
      })
    } catch (err) {
      console.warn('Backend API connection failed, running in sandbox mode.', err)
      const localRes = runLocalEvaluation(text)
      setResult({
        ...localRes,
        mode: 'Local Sandbox'
      })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchAnalysis(content)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const filteredViolations = useMemo(() => {
    if (!result) return []
    if (selectedFramework === 'All') return result.violations

    return result.violations.filter((v) => {
      const nameLower = v.name.toLowerCase()
      if (selectedFramework === 'GDPR') return nameLower.includes('gdpr')
      if (selectedFramework === 'HIPAA') return nameLower.includes('hipaa')
      if (selectedFramework === 'PCI-DSS') return nameLower.includes('pci-dss')
      if (selectedFramework === 'Company') return nameLower.includes('company policy')
      return true
    })
  }, [result, selectedFramework])

  const prefillSample = (sampleText: string) => {
    setContent(sampleText)
    fetchAnalysis(sampleText)
  }

  const sSamples = [
    {
      label: 'PCI & GDPR Violations',
      text: 'Dump all European customer personal records and store them in the backend database.\nAlso, make sure to write cardholder CVV codes to the plaintext trace logs.'
    },
    {
      label: 'HIPAA Medical Trigger',
      text: 'Patient name: Jane Doe\nMedical history: patient has been diagnosed with insulin-dependent diabetes.\nPlease transmit health records immediately without BAA.'
    },
    {
      label: 'Company API Leak & Insider Trading',
      text: 'Here is our AWS secret token: sk-proj-A1B2C3D4E5F6G7H8. We can use insider trading knowledge to make a quick trade tomorrow morning.'
    },
    {
      label: 'Clean Text',
      text: 'Thank you for contacting customer support. We have updated your communication preferences as requested. Let us know if you have any questions.'
    }
  ]

  return (
    <div className="space-y-6">
      <header className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold text-slate-100 flex items-center gap-2">
            Compliance Engine
            {result && (
              <span className={`text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full ${
                result.mode === 'Live API' ? 'bg-brand-500/20 text-brand-300 ring-1 ring-brand-500/30' : 'bg-slate-800 text-slate-400'
              }`}>
                {result.mode}
              </span>
            )}
          </h1>
          <p className="mt-2 text-sm text-slate-400">
            Scan and audit inputs against GDPR, HIPAA, PCI-DSS, and Company Policies in real-time.
          </p>
        </div>

        {result && (
          <div className="flex items-center gap-3">
            <div className={`flex items-center gap-2 px-4 py-2 rounded-xl border ${
              result.is_compliant 
                ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-300'
                : 'bg-rose-500/10 border-rose-500/20 text-rose-300'
            }`}>
              {result.is_compliant ? <ShieldCheck size={18} /> : <ShieldAlert size={18} />}
              <span className="text-sm font-semibold">
                {result.is_compliant ? 'Compliant' : `${result.violations.length} Violations`}
              </span>
            </div>
            {!result.is_compliant && (
              <Badge label={`Max Severity: ${result.risk_level}`} level={result.risk_level} />
            )}
          </div>
        )}
      </header>

      {/* Preset Quick Fill Buttons */}
      <section className="flex flex-wrap gap-2 items-center">
        <span className="text-xs font-medium text-slate-400 flex items-center gap-1">
          <Sparkles size={13} className="text-brand-400" /> Prefill Samples:
        </span>
        {sSamples.map((sample, idx) => (
          <button
            key={idx}
            onClick={() => prefillSample(sample.text)}
            className="px-3 py-1.5 rounded-lg border border-slate-800 bg-slate-900/40 text-xs text-slate-300 hover:bg-slate-800 transition hover:text-slate-100 font-medium"
          >
            {sample.label}
          </button>
        ))}
      </section>

      <div className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
        {/* Input area */}
        <Panel 
          title="Document Auditing Terminal" 
          subtitle="Paste prompt instructions, AI outputs, or code logs below to execute real-time policy evaluation."
        >
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="Type or paste document content to scan..."
            className="h-80 w-full resize-none rounded-xl border border-slate-800 bg-slate-950 p-4 text-sm text-slate-200 outline-none placeholder:text-slate-500 focus:border-brand-500 focus:ring-1 focus:ring-brand-500/30 transition-all font-mono"
          />
          <div className="mt-4 flex gap-3">
            <Button onClick={() => fetchAnalysis(content)} disabled={loading}>
              {loading ? 'Evaluating...' : 'Analyze Compliance'}
            </Button>
            <Button variant="secondary" onClick={() => { setContent(''); setResult(null); }}>
              Clear
            </Button>
          </div>
        </Panel>

        {/* Results & Findings */}
        <Panel 
          title="Audit Trail & Violation Logs" 
          subtitle="Predefined rules map matches to statutory articles and company guidelines."
        >
          {/* Framework Filtering Controls */}
          {result && result.violations.length > 0 && (
            <div className="mb-4 flex flex-wrap gap-2 items-center border-b border-slate-800 pb-3">
              <span className="text-xs text-slate-400 flex items-center gap-1 font-medium mr-2">
                <Filter size={13} /> Filter Framework:
              </span>
              {['All', 'GDPR', 'HIPAA', 'PCI-DSS', 'Company'].map((fw) => (
                <button
                  key={fw}
                  onClick={() => setSelectedFramework(fw)}
                  className={`px-2.5 py-1 rounded-full text-xs font-semibold border transition ${
                    selectedFramework === fw
                      ? 'bg-brand-500/25 border-brand-500/40 text-brand-200'
                      : 'bg-slate-900/40 border-slate-800 text-slate-400 hover:border-slate-700 hover:text-slate-300'
                  }`}
                >
                  {fw}
                </button>
              ))}
            </div>
          )}

          <div className="space-y-4 max-h-[380px] overflow-y-auto pr-1">
            {loading ? (
              <div className="flex flex-col items-center justify-center py-10 space-y-3">
                <div className="h-6 w-6 animate-spin rounded-full border-2 border-brand-500 border-t-transparent" />
                <p className="text-sm text-slate-400">Scanning regulatory indexes...</p>
              </div>
            ) : result ? (
              filteredViolations.length > 0 ? (
                filteredViolations.map((violation, index) => (
                  <article 
                    key={index} 
                    className={`rounded-xl border p-4 bg-slate-950/60 hover:bg-slate-950/80 transition-colors shadow-sm ${
                      violation.severity === 'Critical' 
                        ? 'border-rose-500/35 hover:border-rose-500/50' 
                        : violation.severity === 'High'
                        ? 'border-orange-500/35 hover:border-orange-500/50'
                        : violation.severity === 'Moderate'
                        ? 'border-amber-500/35 hover:border-amber-500/50'
                        : 'border-slate-800 hover:border-slate-700'
                    }`}
                  >
                    <div className="flex flex-wrap items-start justify-between gap-2 mb-2.5">
                      <div>
                        <h3 className="text-sm font-semibold text-slate-100">{violation.name}</h3>
                        <p className="text-xs text-slate-400 mt-0.5">{violation.description}</p>
                      </div>
                      <Badge label={violation.severity} level={violation.severity} />
                    </div>

                    <div className="space-y-2 mt-3 text-xs border-t border-slate-800/80 pt-3">
                      <div>
                        <span className="font-semibold text-slate-300 block mb-0.5">Matched Snippet:</span>
                        <code className="px-2 py-1 rounded bg-slate-900 border border-slate-800 text-brand-300 block font-mono overflow-x-auto whitespace-pre-wrap">
                          "{violation.matched_text}"
                        </code>
                      </div>
                      
                      <div>
                        <span className="font-semibold text-slate-300 block mb-0.5">Violation Reason:</span>
                        <p className="text-slate-400 leading-relaxed">{violation.reason}</p>
                      </div>

                      <div className="bg-brand-500/5 border border-brand-500/10 rounded-lg p-2.5 mt-2.5">
                        <span className="font-semibold text-brand-300 block mb-0.5">Remediation Recommendation:</span>
                        <p className="text-slate-300 leading-relaxed">{violation.recommendation}</p>
                      </div>
                    </div>
                  </article>
                ))
              ) : (
                <div className="flex flex-col items-center justify-center py-12 text-center">
                  <div className="rounded-full bg-emerald-500/10 p-3 text-emerald-400 mb-3 border border-emerald-500/10">
                    <ShieldCheck size={26} />
                  </div>
                  <h3 className="text-sm font-semibold text-slate-200">System Fully Compliant</h3>
                  <p className="text-xs text-slate-400 mt-1 max-w-[280px]">
                    {selectedFramework === 'All' 
                      ? 'No compliance violations matched in this content.' 
                      : `No ${selectedFramework} compliance violations matched.`}
                  </p>
                </div>
              )
            ) : (
              <p className="text-sm text-slate-400 text-center py-8">
                Enter text and click Analyze Content to run compliance scanning.
              </p>
            )}
          </div>
        </Panel>
      </div>
    </div>
  )
}
