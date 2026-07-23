import { useNavigate } from 'react-router-dom'
import { Terminal, MessageSquareText, ShieldCheck, FileSpreadsheet, Sliders } from 'lucide-react'


export function QuickActions() {
  const navigate = useNavigate()

  const actions = [
    {
      title: 'Analyze Prompt',
      subtitle: 'Inspect prompt injection & PII',
      icon: <Terminal size={18} className="text-brand-400" />,
      path: '/prompt-analyzer',
      color: 'hover:border-brand-500/50 hover:bg-brand-500/10',
    },
    {
      title: 'Inspect Response',
      subtitle: 'Verify hallucinations & secrets',
      icon: <MessageSquareText size={18} className="text-cyan-400" />,
      path: '/response-analyzer',
      color: 'hover:border-cyan-500/50 hover:bg-cyan-500/10',
    },
    {
      title: 'Compliance Engine',
      subtitle: 'Check GDPR, HIPAA & PCI-DSS',
      icon: <ShieldCheck size={18} className="text-emerald-400" />,
      path: '/compliance-engine',
      color: 'hover:border-emerald-500/50 hover:bg-emerald-500/10',
    },
    {
      title: 'Export Audit Report',
      subtitle: 'Generate evidence snapshot',
      icon: <FileSpreadsheet size={18} className="text-purple-400" />,
      path: '/audit-reports',
      color: 'hover:border-purple-500/50 hover:bg-purple-500/10',
    },
    {
      title: 'Configure Policies',
      subtitle: 'Adjust detection thresholds',
      icon: <Sliders size={18} className="text-amber-400" />,
      path: '/settings',
      color: 'hover:border-amber-500/50 hover:bg-amber-500/10',
    },
  ]

  return (
    <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
      {actions.map((act) => (
        <button
          key={act.path}
          type="button"
          onClick={() => navigate(act.path)}
          className={`flex flex-col text-left rounded-xl border border-slate-800 bg-slate-950/70 p-3.5 transition-all ${act.color}`}
        >
          <div className="flex items-center justify-between">
            <div className="rounded-lg border border-slate-800 bg-slate-900 p-2">{act.icon}</div>
          </div>
          <p className="mt-3 text-sm font-semibold text-slate-100">{act.title}</p>
          <p className="mt-1 text-xs text-slate-400">{act.subtitle}</p>
        </button>
      ))}
    </div>
  )
}
