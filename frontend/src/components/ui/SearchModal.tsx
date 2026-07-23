import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Search, X, FileText, Shield, Sliders, ArrowRight } from 'lucide-react'


interface SearchModalProps {
  isOpen: boolean
  onClose: () => void
}

export function SearchModal({ isOpen, onClose }: SearchModalProps) {
  const [query, setQuery] = useState('')
  const navigate = useNavigate()

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault()
        if (isOpen) onClose()
      }

      if (e.key === 'Escape' && isOpen) {
        onClose()
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [isOpen, onClose])

  if (!isOpen) return null

  const items = [
    { label: 'Prompt Analyzer Workspace', category: 'Analyzers', path: '/prompt-analyzer', icon: <Shield size={16} /> },
    { label: 'Response Safety Inspector', category: 'Analyzers', path: '/response-analyzer', icon: <Shield size={16} /> },
    { label: 'GDPR & HIPAA Compliance Engine', category: 'Governance', path: '/compliance-engine', icon: <FileText size={16} /> },
    { label: 'Quarterly Audit Reports Registry', category: 'Reports', path: '/audit-reports', icon: <FileText size={16} /> },
    { label: 'Workspace Policy & Threshold Settings', category: 'System', path: '/settings', icon: <Sliders size={16} /> },
  ]

  const filtered = items.filter(
    (i) => i.label.toLowerCase().includes(query.toLowerCase()) || i.category.toLowerCase().includes(query.toLowerCase())
  )

  const handleSelect = (path: string) => {
    navigate(path)
    onClose()
  }

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center bg-slate-950/80 p-4 backdrop-blur-sm pt-20">
      <div className="w-full max-w-xl overflow-hidden rounded-2xl border border-slate-800 bg-slate-900 shadow-2xl">
        <div className="flex items-center border-b border-slate-800 px-4 py-3">
          <Search size={18} className="text-slate-400 mr-3" />
          <input
            type="text"
            autoFocus
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Type a command, report name, or page..."
            className="w-full bg-transparent text-sm text-slate-100 placeholder:text-slate-500 outline-none"
          />
          <button onClick={onClose} className="rounded-lg p-1 text-slate-400 hover:text-slate-200">
            <X size={18} />
          </button>
        </div>

        <div className="max-h-80 overflow-y-auto p-2">
          {filtered.length > 0 ? (
            filtered.map((item) => (
              <button
                key={item.path}
                onClick={() => handleSelect(item.path)}
                className="flex w-full items-center justify-between rounded-xl px-3 py-2.5 text-left text-sm text-slate-300 hover:bg-slate-800 hover:text-slate-100 transition"
              >
                <div className="flex items-center gap-3">
                  <span className="text-slate-400">{item.icon}</span>
                  <span>{item.label}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="rounded bg-slate-800 px-2 py-0.5 text-[10px] text-slate-400">{item.category}</span>
                  <ArrowRight size={14} className="text-slate-500" />
                </div>
              </button>
            ))
          ) : (
            <p className="p-4 text-center text-xs text-slate-500">No matching routes or controls found.</p>
          )}
        </div>

        <div className="flex items-center justify-between border-t border-slate-800 px-4 py-2 text-[11px] text-slate-500">
          <span>Navigate with arrows or mouse</span>
          <kbd className="rounded border border-slate-700 bg-slate-800 px-1.5 py-0.5 text-[10px]">ESC to close</kbd>
        </div>
      </div>
    </div>
  )
}
