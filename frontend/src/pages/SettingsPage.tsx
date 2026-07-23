import { SettingsTabs } from '../components/settings/SettingsTabs'

export function SettingsPage() {
  return (
    <div className="space-y-6">
      <header className="border-b border-slate-800/80 pb-5">
        <h1 className="text-2xl font-bold tracking-tight text-slate-100">Settings & Policy Control Center</h1>
        <p className="mt-1 text-xs text-slate-400">
          Manage workspace compliance baselines, detection thresholds, API keys, and audit retention policies.
        </p>
      </header>

      <SettingsTabs />
    </div>
  )
}

