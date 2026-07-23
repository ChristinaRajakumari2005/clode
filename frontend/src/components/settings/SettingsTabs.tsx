import { useState } from 'react'
import { Badge } from '../ui/Badge'
import { Button } from '../ui/Button'
import { Panel } from '../ui/Panel'
import { Sliders, Shield, Key, Database, Check, RefreshCw } from 'lucide-react'

export function SettingsTabs() {
  const [activeTab, setActiveTab] = useState<'general' | 'policies' | 'security' | 'retention'>('policies')
  const [saved, setSaved] = useState(false)

  // Policy threshold states
  const [privacySensitivity, setPrivacySensitivity] = useState(85)
  const [injectionSensitivity, setInjectionSensitivity] = useState(90)
  const [hallucinationThreshold, setHallucinationThreshold] = useState(60)
  const [toxicityThreshold, setToxicityThreshold] = useState(75)

  // Toggles
  const [gdprEnabled, setGdprEnabled] = useState(true)
  const [hipaaEnabled, setHipaaEnabled] = useState(true)
  const [pciEnabled, setPciEnabled] = useState(true)
  const [autoExport, setAutoExport] = useState(false)

  const handleSave = () => {
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  return (
    <div className="space-y-6">
      {/* Settings Navigation Tabs */}
      <div className="flex border-b border-slate-800 gap-6 overflow-x-auto pb-1">
        {[
          { id: 'policies', label: 'Policy Sensitivity & Rules', icon: <Sliders size={16} /> },
          { id: 'general', label: 'Workspace Configuration', icon: <Shield size={16} /> },
          { id: 'security', label: 'Security & API Credentials', icon: <Key size={16} /> },
          { id: 'retention', label: 'Audit Log Retention', icon: <Database size={16} /> },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={`flex items-center gap-2 border-b-2 pb-3 text-sm font-semibold transition whitespace-nowrap ${
              activeTab === tab.id
                ? 'border-brand-500 text-brand-300'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            {tab.icon}
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Contents */}
      {activeTab === 'policies' && (
        <div className="space-y-5">
          <Panel title="Regulatory Framework Profiles" subtitle="Active compliance evaluation baselines">
            <div className="grid gap-3 sm:grid-cols-3">
              <FrameworkToggle
                label="GDPR Pack"
                description="EU Citizen data & consent rules"
                enabled={gdprEnabled}
                onToggle={() => setGdprEnabled(!gdprEnabled)}
              />
              <FrameworkToggle
                label="HIPAA Baseline"
                description="PHI & medical record controls"
                enabled={hipaaEnabled}
                onToggle={() => setHipaaEnabled(!hipaaEnabled)}
              />
              <FrameworkToggle
                label="PCI-DSS 4.0"
                description="PAN credit card masking"
                enabled={pciEnabled}
                onToggle={() => setPciEnabled(!pciEnabled)}
              />
            </div>
          </Panel>

          <Panel title="Detection Sensitivity Thresholds" subtitle="Fine-tune algorithm trigger levels (0-100)">
            <div className="space-y-4">
              <SliderRow
                label="Privacy & PII Exposure"
                value={privacySensitivity}
                onChange={setPrivacySensitivity}
                description="Flags SSNs, emails, and address tokens."
              />
              <SliderRow
                label="Prompt Injection Resilience"
                value={injectionSensitivity}
                onChange={setInjectionSensitivity}
                description="Sensitivity to instruction overrides."
              />
              <SliderRow
                label="Hallucination Qualifier"
                value={hallucinationThreshold}
                onChange={setHallucinationThreshold}
                description="Detects unverified overconfident assertions."
              />
              <SliderRow
                label="Toxicity & Harm Filter"
                value={toxicityThreshold}
                onChange={setToxicityThreshold}
                description="Flags abusive, hate speech, or offensive content."
              />
            </div>
          </Panel>
        </div>
      )}

      {activeTab === 'general' && (
        <div className="space-y-5">
          <Panel title="Environment Baseline" subtitle="Manage workspace metadata & active instance mode">
            <div className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300">Workspace Label</label>
                <input
                  type="text"
                  defaultValue="Enterprise Governance Production"
                  className="mt-1.5 w-full rounded-xl border border-slate-800 bg-slate-950 px-3 py-2 text-sm text-slate-200 outline-none focus:border-brand-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300">Model Provider Subnet</label>
                <select className="mt-1.5 w-full rounded-xl border border-slate-800 bg-slate-950 px-3 py-2 text-sm text-slate-200 outline-none focus:border-brand-500">
                  <option>US-East (Isolated Sandbox)</option>
                  <option>EU-Central (GDPR Enclave)</option>
                  <option>Global Edge Direct</option>
                </select>
              </div>
            </div>
          </Panel>
        </div>
      )}

      {activeTab === 'security' && (
        <div className="space-y-5">
          <Panel title="API Tokens & Secrets" subtitle="Simulated integration credentials for gateway proxies">
            <div className="space-y-3">
              <div className="flex items-center justify-between rounded-xl border border-slate-800 bg-slate-950 p-3">
                <div>
                  <p className="text-sm font-medium text-slate-200">Production Proxy Token</p>
                  <p className="text-xs font-mono text-slate-500">ag_live_99214xxxxxxxxxxxxxxx</p>
                </div>
                <Button variant="secondary">
                  <RefreshCw size={14} className="mr-1.5 inline" /> Rotate Key
                </Button>
              </div>
            </div>
          </Panel>
        </div>
      )}

      {activeTab === 'retention' && (
        <div className="space-y-5">
          <Panel title="Audit Retention Schedule" subtitle="Configure automatic snapshotting and log purging">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-slate-200">Log Retention Window</p>
                  <p className="text-xs text-slate-400">Duration audit events are stored before archiving.</p>
                </div>
                <Badge label="90 Days" />
              </div>
              <FrameworkToggle
                label="Automate Weekly PDF Exports"
                description="Generates report snapshots every Sunday at 00:00 UTC."
                enabled={autoExport}
                onToggle={() => setAutoExport(!autoExport)}
              />
            </div>
          </Panel>
        </div>
      )}

      {/* Footer Save Button */}
      <div className="flex items-center justify-between border-t border-slate-800 pt-4">
        <span className="text-xs text-slate-500">All configurations enforced across prompt/response gateways</span>
        <Button onClick={handleSave}>
          {saved ? (
            <>
              <Check size={16} className="mr-1.5 inline" /> Saved!
            </>
          ) : (
            'Save Preferences'
          )}
        </Button>
      </div>
    </div>
  )
}

function FrameworkToggle({
  label,
  description,
  enabled,
  onToggle,
}: {
  label: string
  description: string
  enabled: boolean
  onToggle: () => void
}) {
  return (
    <div
      onClick={onToggle}
      className={`cursor-pointer rounded-xl border p-3.5 transition ${
        enabled ? 'border-brand-500/40 bg-brand-500/10' : 'border-slate-800 bg-slate-950/60'
      }`}
    >
      <div className="flex items-center justify-between">
        <span className="text-sm font-semibold text-slate-100">{label}</span>
        <span
          className={`h-4 w-4 rounded-full border transition ${
            enabled ? 'border-brand-400 bg-brand-500' : 'border-slate-600 bg-slate-800'
          }`}
        />
      </div>
      <p className="mt-1 text-xs text-slate-400">{description}</p>
    </div>
  )
}

function SliderRow({
  label,
  value,
  onChange,
  description,
}: {
  label: string
  value: number
  onChange: (val: number) => void
  description: string
}) {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-4">
      <div className="flex items-center justify-between">
        <div>
          <span className="text-sm font-semibold text-slate-200">{label}</span>
          <p className="text-xs text-slate-400">{description}</p>
        </div>
        <span className="rounded-lg bg-slate-800 px-2.5 py-1 text-xs font-mono text-brand-300">{value}%</span>
      </div>
      <input
        type="range"
        min="0"
        max="100"
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className="mt-3 w-full accent-brand-500 cursor-pointer"
      />
    </div>
  )
}
