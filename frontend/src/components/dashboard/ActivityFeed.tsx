import type { ActivityItem } from '../../types/governance'
import { Badge } from '../ui/Badge'
import { Activity, ShieldAlert, FileText, Settings, ShieldCheck } from 'lucide-react'

interface ActivityFeedProps {
  activities: ActivityItem[]
  onSelectActivity?: (activity: ActivityItem) => void
}

export function ActivityFeed({ activities, onSelectActivity }: ActivityFeedProps) {
  const getIcon = (type: ActivityItem['type']) => {
    switch (type) {
      case 'Prompt Scan':
        return <Activity size={16} className="text-amber-400" />
      case 'Response Scan':
        return <ShieldAlert size={16} className="text-rose-400" />
      case 'Policy Update':
        return <Settings size={16} className="text-brand-400" />
      case 'Report Generated':
        return <FileText size={16} className="text-cyan-400" />
      case 'Security Alert':
        return <ShieldCheck size={16} className="text-emerald-400" />
    }
  }

  return (
    <div className="space-y-3">
      {activities.map((item) => (
        <article
          key={item.id}
          onClick={() => onSelectActivity?.(item)}
          className="group flex flex-col gap-2 rounded-xl border border-slate-800 bg-slate-950/60 p-3.5 transition-all hover:border-slate-700 hover:bg-slate-900/80 cursor-pointer sm:flex-row sm:items-center sm:justify-between"
        >
          <div className="flex items-start gap-3">
            <div className="mt-0.5 rounded-lg border border-slate-800 bg-slate-900 p-2 group-hover:border-slate-700">
              {getIcon(item.type)}
            </div>
            <div>
              <div className="flex items-center gap-2 flex-wrap">
                <h4 className="text-sm font-semibold text-slate-200 group-hover:text-brand-300">{item.title}</h4>
                <Badge label={item.severity} level={item.severity} />
              </div>
              <p className="mt-1 text-xs text-slate-400 line-clamp-1">{item.details}</p>
              <div className="mt-2 flex items-center gap-3 text-[11px] text-slate-500">
                <span>Triggered by: {item.user}</span>
                <span>•</span>
                <span>{item.timestamp}</span>
              </div>
            </div>
          </div>
        </article>
      ))}
    </div>
  )
}
