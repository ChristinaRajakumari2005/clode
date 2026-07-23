import {
  ShieldCheck,
  LayoutDashboard,
  Terminal,
  MessageSquareText,
  FileSpreadsheet,
  Sliders,
  ChevronDown,
  Activity,
  Cpu,
} from 'lucide-react'
import { NavLink } from 'react-router-dom'
import { navItems } from '../../data/mockData'

export function Sidebar() {
  const getNavIcon = (iconName?: string) => {
    switch (iconName) {
      case 'LayoutDashboard':
        return <LayoutDashboard size={18} />
      case 'Terminal':
        return <Terminal size={18} />
      case 'MessageSquareText':
        return <MessageSquareText size={18} />
      case 'ShieldCheck':
        return <ShieldCheck size={18} />
      case 'FileSpreadsheet':
        return <FileSpreadsheet size={18} />
      case 'Sliders':
        return <Sliders size={18} />
      default:
        return <Activity size={18} />
    }
  }

  // Group items by category
  const categories = ['Overview', 'Analyzers', 'Governance', 'System'] as const

  return (
    <aside className="hidden w-72 shrink-0 flex-col border-r border-slate-800/80 bg-slate-950/95 p-5 lg:flex select-none">
      {/* Brand Header & Workspace Switcher */}
      <div className="mb-6 rounded-xl border border-slate-800/80 bg-slate-900/60 p-3 transition hover:border-slate-700">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="rounded-xl bg-gradient-to-br from-brand-500/30 to-cyan-500/20 p-2 text-brand-300 ring-1 ring-brand-500/40">
              <ShieldCheck size={20} />
            </div>
            <div>
              <p className="text-sm font-bold tracking-tight text-slate-100">AI Governance</p>
              <p className="text-[11px] font-medium text-brand-400">Enterprise Enclave</p>
            </div>
          </div>
          <ChevronDown size={14} className="text-slate-400" />
        </div>
      </div>

      {/* Nav Section by Category */}
      <nav className="flex-1 space-y-5 overflow-y-auto pr-1">
        {categories.map((cat) => {
          const items = navItems.filter((i) => i.category === cat)
          if (items.length === 0) return null

          return (
            <div key={cat}>
              <p className="px-3 text-[10px] font-bold uppercase tracking-wider text-slate-500 mb-1.5">{cat}</p>
              <div className="space-y-1">
                {items.map((item) => (
                  <NavLink
                    key={item.path}
                    to={item.path}
                    className={({ isActive }) =>
                      `flex items-center gap-3 rounded-xl px-3 py-2.5 text-xs font-medium transition duration-150 ${
                        isActive
                          ? 'bg-gradient-to-r from-brand-500/20 to-brand-500/5 text-brand-200 ring-1 ring-brand-500/30 shadow-sm'
                          : 'text-slate-400 hover:bg-slate-900/80 hover:text-slate-100'
                      }`
                    }
                  >
                    <span className="shrink-0">{getNavIcon(item.icon)}</span>
                    <span>{item.label}</span>
                  </NavLink>
                ))}
              </div>
            </div>
          )
        })}
      </nav>

      {/* Footer Status Pill */}
      <div className="mt-auto rounded-xl border border-slate-800/80 bg-slate-900/60 p-3.5">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="relative flex h-2 w-2">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75" />
              <span className="relative inline-flex h-2 w-2 rounded-full bg-emerald-500" />
            </span>
            <p className="text-xs font-semibold text-slate-200">Shield Active</p>
          </div>
          <Cpu size={14} className="text-slate-500" />
        </div>
        <p className="mt-1.5 text-[11px] text-slate-400 leading-snug">
          Policy Engine v2.4 running in high-throughput local mode.
        </p>
      </div>
    </aside>
  )
}

