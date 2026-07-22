import clsx from 'clsx'
import type { ButtonHTMLAttributes } from 'react'

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary'
}

export function Button({ className, variant = 'primary', ...props }: ButtonProps) {
  return (
    <button
      className={clsx(
        'rounded-lg px-4 py-2 text-sm font-medium transition focus:outline-none focus-visible:ring-2 focus-visible:ring-brand-500',
        variant === 'primary'
          ? 'bg-brand-500 text-white hover:bg-brand-400'
          : 'bg-slate-800 text-slate-200 ring-1 ring-slate-700 hover:bg-slate-700',
        className,
      )}
      {...props}
    />
  )
}
