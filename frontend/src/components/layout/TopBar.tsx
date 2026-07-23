import { useState } from 'react'
import { Bell, Search, Command } from 'lucide-react'
import { navItems, notificationsList } from '../../data/mockData'
import { NavLink } from 'react-router-dom'
import { SearchModal } from '../ui/SearchModal'
import { NotificationPopover } from '../ui/NotificationPopover'

export function TopBar() {
  const [isSearchOpen, setIsSearchOpen] = useState(false)
  const [isNotifOpen, setIsNotifOpen] = useState(false)

  const unreadCount = notificationsList.filter((n) => !n.read).length

  return (
    <header className="sticky top-0 z-20 border-b border-slate-800/80 bg-slate-950/80 px-4 py-3 backdrop-blur-md lg:px-8">
      <div className="flex items-center gap-3">
        {/* Quick Search Button / Command Palette Launcher */}
        <button
          onClick={() => setIsSearchOpen(true)}
          className="relative flex w-full max-w-md items-center justify-between rounded-xl border border-slate-800/90 bg-slate-900/80 px-3.5 py-2 text-xs text-slate-400 transition hover:border-slate-700 hover:text-slate-200"
        >
          <div className="flex items-center gap-2.5">
            <Search size={14} className="text-slate-400" />
            <span>Search reports, compliance controls, policies...</span>
          </div>
          <span className="hidden sm:flex items-center gap-0.5 rounded border border-slate-700/80 bg-slate-800/80 px-1.5 py-0.5 text-[10px] font-semibold text-slate-300">
            <Command size={10} /> K
          </span>
        </button>

        {/* Right side actions */}
        <div className="relative flex items-center gap-3 ml-auto">
          {/* Notification Bell */}
          <div className="relative">
            <button
              type="button"
              onClick={() => setIsNotifOpen(!isNotifOpen)}
              className="relative rounded-xl border border-slate-800 bg-slate-900/80 p-2.5 text-slate-300 transition hover:border-slate-700 hover:text-slate-100"
            >
              <Bell size={16} />
              {unreadCount > 0 && (
                <span className="absolute -right-1 -top-1 flex h-4 w-4 items-center justify-center rounded-full bg-brand-500 text-[10px] font-bold text-white ring-2 ring-slate-950">
                  {unreadCount}
                </span>
              )}
            </button>

            <NotificationPopover
              notifications={notificationsList}
              isOpen={isNotifOpen}
              onClose={() => setIsNotifOpen(false)}
            />
          </div>

          {/* User Profile Badge */}
          <div className="flex items-center gap-2.5 rounded-xl border border-slate-800/80 bg-slate-900/60 p-1.5 pr-3">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-brand-500 to-brand-700 text-xs font-bold text-white shadow-sm">
              AG
            </div>
            <div className="hidden sm:block text-left">
              <p className="text-xs font-semibold text-slate-200 leading-none">Security Office</p>
              <p className="text-[10px] text-slate-400 leading-none mt-1">Admin Tier</p>
            </div>
          </div>
        </div>
      </div>

      {/* Mobile Navigation Row */}
      <nav className="mt-3 flex gap-2 overflow-x-auto pb-1 lg:hidden">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `whitespace-nowrap rounded-lg px-3 py-1.5 text-xs font-medium ${
                isActive ? 'bg-brand-500/20 text-brand-300 ring-1 ring-brand-500/40' : 'bg-slate-900 text-slate-400'
              }`
            }
          >
            {item.label}
          </NavLink>
        ))}
      </nav>

      {/* Command Palette Modal */}
      <SearchModal isOpen={isSearchOpen} onClose={() => setIsSearchOpen(false)} />
    </header>
  )
}

