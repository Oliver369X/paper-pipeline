import { cn } from '@/lib/utils'
import type { ButtonHTMLAttributes } from 'react'

export function Button({
  className,
  variant = 'default',
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: 'default' | 'outline' | 'ghost' | 'destructive'
}) {
  return (
    <button
      type="button"
      className={cn(
        'inline-flex items-center justify-center rounded-md px-3 py-2 text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-violet-400 focus-visible:ring-offset-2 focus-visible:ring-offset-zinc-950 disabled:opacity-50',
        variant === 'default' &&
          'bg-violet-600 text-white hover:bg-violet-500',
        variant === 'outline' &&
          'border border-zinc-600 bg-transparent hover:bg-zinc-800',
        variant === 'ghost' && 'hover:bg-zinc-800',
        variant === 'destructive' && 'bg-red-700 text-white hover:bg-red-600',
        className,
      )}
      {...props}
    />
  )
}
