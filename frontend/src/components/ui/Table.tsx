import type { ReactNode } from 'react'

interface TableProps {
  columns: string[]
  rows: ReactNode[][]
}

export function Table({ columns, rows }: TableProps) {
  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-slate-800 text-left">
        <thead>
          <tr>
            {columns.map((column) => (
              <th
                key={column}
                className="px-3 py-2 text-xs font-medium uppercase tracking-wide text-slate-400"
              >
                {column}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-800">
          {rows.map((row, rowIndex) => (
            <tr key={rowIndex} className="hover:bg-slate-800/30">
              {row.map((cell, cellIndex) => (
                <td key={`${rowIndex}-${cellIndex}`} className="px-3 py-3 text-sm text-slate-200">
                  {cell}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
