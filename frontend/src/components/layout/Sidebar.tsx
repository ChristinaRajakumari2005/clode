import { Bot, ShieldCheck } from 'lucide-react'
import { NavLink } from 'react-router-dom'
import { navItems } from '../../data/mockData'

export function Sidebar() {
  return (
    <aside className="hidden w-72 shrink-0 flex-col border-r border-slate-800 bg-slate-950/90 p-5 lg:flex">
      <div className="mb-6 flex items-center gap-3">
        <div className="rounded-lg bg-brand-500/20 p-2 text-brand-300">
          <ShieldCheck size={18} />
        </div>
        <div>
          <p className="text-sm font-semibold text-slate-100">AI Governance Copilot</p>
          <p className="text-xs text-slate-400">Enterprise Workspace</p>
        </div>
      </div>

      <nav className="space-y-1">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `block rounded-lg px-3 py-2 text-sm transition ${
                isActive
                  ? 'bg-brand-500/20 text-brand-200 ring-1 ring-brand-500/30'
                  : 'text-slate-300 hover:bg-slate-800/70 hover:text-slate-100'
              }`
            }
          >
            {item.label}
          </NavLink>
        ))}
      </nav>

      <div className="mt-auto rounded-xl border border-slate-800 bg-slate-900/80 p-3">
        <div className="flex items-center gap-2 text-slate-200">
          <Bot size={16} />
          <p className="text-sm font-medium">Policy Assistant</p>
        </div>
        <p className="mt-2 text-xs text-slate-400">
          Local-only mode enabled. Backend integrations are currently disabled.
        </p>
      </div>
    </aside>
  )
}
