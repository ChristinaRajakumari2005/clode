import { AnalyzerWorkspace } from '../components/analysis/AnalyzerWorkspace'

export function ResponseAnalyzerPage() {
  return (
    <AnalyzerWorkspace
      title="Response Analyzer"
      description="Inspect generated model responses for hallucinations, toxicity, security leakage, and regulatory concerns."
      inputLabel="Model Response Input"
      placeholder="Paste generated AI response content to review..."
      initialValue="This recommendation is 100% accurate with no doubt. Customer SSN is 111-22-3333 and API key is sk-test-private."
    />
  )
}
