import { useState } from 'react'
import type { NotificationItem } from '../../types/governance'
import { Bell, Check, AlertCircle, Info, AlertTriangle } from 'lucide-react'

interface NotificationPopoverProps {
  notifications: NotificationItem[]
  isOpen: boolean
  onClose: () => void
}

export function NotificationPopover({ notifications: initial, isOpen, onClose }: NotificationPopoverProps) {
  const [items, setItems] = useState(initial)

  if (!isOpen) return null

  const markAllRead = () => {
    setItems((prev) => prev.map((n) => ({ ...n, read: true })))
  }

  const unreadCount = items.filter((n) => !n.read).length

  return (
    <div className="absolute right-0 top-12 z-50 w-80 sm:w-96 rounded-2xl border border-slate-800 bg-slate-900 shadow-2xl overflow-hidden backdrop-blur">
      <div className="flex items-center justify-between border-b border-slate-800 p-4">
        <div className="flex items-center gap-2">
          <Bell size={16} className="text-brand-400" />
          <h3 className="text-sm font-semibold text-slate-100">System Alerts</h3>
          {unreadCount > 0 && (
            <span className="rounded-full bg-brand-500/20 px-2 py-0.5 text-xs font-semibold text-brand-300">
              {unreadCount} new
            </span>
          )}
        </div>
        {unreadCount > 0 && (
          <button
            onClick={markAllRead}
            className="flex items-center gap-1 text-xs text-brand-400 hover:text-brand-300"
          >
            <Check size={12} />
            Mark read
          </button>
        )}
      </div>

      <div className="max-h-80 overflow-y-auto divide-y divide-slate-800/60">
        {items.length > 0 ? (
          items.map((n) => (
            <div
              key={n.id}
              className={`p-3.5 transition hover:bg-slate-800/50 ${!n.read ? 'bg-brand-500/5' : ''}`}
            >
              <div className="flex items-start gap-2.5">
                <span className="mt-0.5 shrink-0">
                  {n.type === 'alert' ? (
                    <AlertCircle size={16} className="text-rose-400" />
                  ) : n.type === 'warning' ? (
                    <AlertTriangle size={16} className="text-amber-400" />
                  ) : (
                    <Info size={16} className="text-brand-400" />
                  )}
                </span>
                <div className="flex-1">
                  <div className="flex items-center justify-between">
                    <p className="text-xs font-semibold text-slate-200">{n.title}</p>
                    <span className="text-[10px] text-slate-500">{n.timestamp}</span>
                  </div>
                  <p className="mt-1 text-xs text-slate-400 leading-relaxed">{n.message}</p>
                </div>
              </div>
            </div>
          ))
        ) : (
          <p className="p-6 text-center text-xs text-slate-500">No active alerts.</p>
        )}
      </div>

      <div className="border-t border-slate-800 p-2 text-center">
        <button onClick={onClose} className="w-full rounded-lg py-1 text-xs text-slate-400 hover:text-slate-200">
          Close
        </button>
      </div>
    </div>
  )
}
