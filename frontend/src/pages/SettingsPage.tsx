import { useState } from 'react'
import { Badge } from '../components/ui/Badge'
import { Button } from '../components/ui/Button'
import { Panel } from '../components/ui/Panel'

export function SettingsPage() {
  const [privacyScan, setPrivacyScan] = useState(true)
  const [securityScan, setSecurityScan] = useState(true)
  const [toxicityScan, setToxicityScan] = useState(true)

  return (
    <div className="space-y-5">
      <header>
        <h1 className="text-2xl font-semibold text-slate-100">Settings</h1>
        <p className="mt-2 text-sm text-slate-400">
          Configure policy packs, scanning behavior, and dashboard preferences.
        </p>
      </header>

      <Panel title="Policy Profile" subtitle="Current workspace policy baseline">
        <div className="flex flex-wrap gap-2">
          <Badge label="GDPR Pack: Active" />
          <Badge label="SOC2 Controls: Active" />
          <Badge label="PII Detection: Strict" />
          <Badge label="Audit Retention: 90 Days" />
        </div>
      </Panel>

      <Panel title="Analyzer Controls" subtitle="Enable or disable category-level checks">
        <div className="space-y-3">
          <ToggleRow
            label="Privacy & PII Detection"
            description="Detect and flag personal data leakage patterns."
            value={privacyScan}
            onChange={setPrivacyScan}
          />
          <ToggleRow
            label="Security Secrets Detection"
            description="Identify possible credential or key material in content."
            value={securityScan}
            onChange={setSecurityScan}
          />
          <ToggleRow
            label="Toxicity and Harm Filters"
            description="Detect abusive and harmful language indicators."
            value={toxicityScan}
            onChange={setToxicityScan}
          />
        </div>
      </Panel>

      <div className="flex justify-end">
        <Button>Save Preferences</Button>
      </div>
    </div>
  )
}

interface ToggleRowProps {
  label: string
  description: string
  value: boolean
  onChange: (value: boolean) => void
}

function ToggleRow({ label, description, value, onChange }: ToggleRowProps) {
  return (
    <div className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-slate-800 bg-slate-950/60 p-3">
      <div>
        <p className="text-sm font-medium text-slate-200">{label}</p>
        <p className="text-xs text-slate-400">{description}</p>
      </div>
      <button
        type="button"
        onClick={() => onChange(!value)}
        className={`h-7 w-12 rounded-full p-1 transition ${
          value ? 'bg-brand-500' : 'bg-slate-700'
        }`}
      >
        <span
          className={`block h-5 w-5 rounded-full bg-white transition ${value ? 'translate-x-5' : ''}`}
        />
      </button>
    </div>
  )
}
