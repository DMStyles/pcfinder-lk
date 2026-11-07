'use client'

import { getSourceColors } from '@/lib/utils'
import { clsx } from '@/lib/utils'

interface SourceBadgeProps {
  source: string
  size?: 'sm' | 'md'
  className?: string
}

const SOURCE_DISPLAY_NAMES: Record<string, string> = {
  'Facebook Marketplace': 'FB Marketplace',
}

export default function SourceBadge({ source, size = 'sm', className }: SourceBadgeProps) {
  const colors = getSourceColors(source)
  const displayName = SOURCE_DISPLAY_NAMES[source] ?? source

  return (
    <span
      className={clsx(
        'badge-base',
        colors.bg,
        colors.text,
        colors.border,
        size === 'sm' ? 'text-[10px] px-1.5 py-0.5' : 'text-xs px-2 py-1',
        className
      )}
    >
      <span className={clsx('w-1.5 h-1.5 rounded-full flex-shrink-0', colors.dot)} />
      {displayName}
    </span>
  )
}
