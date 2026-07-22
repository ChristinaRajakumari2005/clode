import { Bell, Search } from 'lucide-react'
import { navItems } from '../../data/mockData'
import { NavLink } from 'react-router-dom'

export function TopBar() {
  return (
    <header className="sticky top-0 z-20 border-b border-slate-800/90 bg-slate-950/80 px-4 py-3 backdrop-blur lg:px-8">
      <div className="flex items-center gap-3">
        <div className="relative hidden w-full max-w-sm md:block">
          <Search size={14} className="pointer-events-none absolute left-3 top-3 text-slate-500" />
          <input
            type="search"
            placeholder="Search reports, findings, controls..."
            className="w-full rounded-lg border border-slate-800 bg-slate-900 py-2 pl-9 pr-3 text-sm text-slate-200 outline-none placeholder:text-slate-500 focus:border-brand-500"
          />
        </div>

        <div className="flex items-center gap-3 md:ml-auto">
          <button
            type="button"
            className="rounded-lg border border-slate-800 bg-slate-900 p-2 text-slate-300 hover:text-slate-100"
          >
            <Bell size={16} />
          </button>
          <div className="flex h-9 w-9 items-center justify-center rounded-full bg-brand-500/20 text-sm font-semibold text-brand-200">
            AG
          </div>
        </div>
      </div>

      <nav className="mt-3 flex gap-2 overflow-x-auto pb-1 lg:hidden">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `whitespace-nowrap rounded-md px-2.5 py-1.5 text-xs ${
                isActive ? 'bg-brand-500/20 text-brand-300' : 'bg-slate-900 text-slate-300'
              }`
            }
          >
            {item.label}
          </NavLink>
        ))}
      </nav>
    </header>
  )
}
