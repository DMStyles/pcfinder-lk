'use client'

import { ArrowUpDown, ChevronDown } from 'lucide-react'
import type { SearchFilters } from '@/types'
import { clsx } from '@/lib/utils'

interface SortBarProps {
  total: number
  query: string
  sort: SearchFilters['sort']
  onSortChange: (sort: string) => void
  viewMode?: 'grid' | 'list'
  onViewModeChange?: (mode: 'grid' | 'list') => void
  isLoading?: boolean
  sourcesQueried?: string[]
  cached?: boolean
}

const SORT_OPTIONS = [
  { value: 'relevance', label: 'Relevance' },
  { value: 'price_asc', label: 'Price: Low → High' },
  { value: 'price_desc', label: 'Price: High → Low' },
  { value: 'recent', label: 'Recently Added' },
]

export default function SortBar({
  total,
  query,
  sort,
  onSortChange,
  viewMode = 'grid',
  onViewModeChange,
  isLoading,
  sourcesQueried = [],
  cached,
}: SortBarProps) {
  const currentSortLabel = SORT_OPTIONS.find(o => o.value === sort)?.label ?? 'Relevance'

  return (
    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 py-3 px-1">
      {/* Results count */}
      <div className="flex items-center gap-2 flex-wrap">
        {isLoading ? (
          <div className="h-5 w-48 bg-slate-800 rounded animate-pulse" />
        ) : (
          <>
            <p className="text-sm text-slate-300">
              <span className="font-semibold text-white">{total.toLocaleString()}</span>
              {' '}listing{total !== 1 ? 's' : ''} found
              {query && (
                <> for <span className="text-indigo-400 font-medium">&ldquo;{query}&rdquo;</span></>
              )}
            </p>
            {cached && (
              <span className="badge-base text-[10px] bg-slate-800/60 text-slate-500 border-slate-700/60 px-1.5">
                cached
              </span>
            )}
          </>
        )}

        {/* Sources queried */}
        {sourcesQueried.length > 0 && !isLoading && (
          <div className="flex items-center gap-1 text-xs text-slate-600 ml-1">
            <span>from</span>
            <span className="text-slate-500">{sourcesQueried.join(', ')}</span>
          </div>
        )}
      </div>

      {/* Controls */}
      <div className="flex items-center gap-2">
        {/* Sort dropdown */}
        <div className="flex items-center gap-1.5">
          <ArrowUpDown className="w-3.5 h-3.5 text-slate-500" />
          <span className="text-xs text-slate-500 hidden sm:inline">Sort:</span>
          <div className="relative">
            <select
              value={sort || 'relevance'}
              onChange={e => onSortChange(e.target.value)}
              className="appearance-none pl-2 pr-7 py-1.5 bg-slate-800 border border-slate-700 rounded-lg text-sm text-slate-300 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent cursor-pointer transition-all"
              style={{
                backgroundImage: `url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%2364748b' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M6 8l4 4 4-4'/%3e%3c/svg%3e")`,
                backgroundPosition: 'right 0.3rem center',
                backgroundRepeat: 'no-repeat',
                backgroundSize: '1.2em 1.2em',
              }}
            >
              {SORT_OPTIONS.map(opt => (
                <option key={opt.value} value={opt.value} className="bg-slate-800">
                  {opt.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* View toggle */}
        {onViewModeChange && (
          <div className="flex rounded-lg border border-slate-700 overflow-hidden">
            <button
              onClick={() => onViewModeChange('grid')}
              className={clsx(
                'px-2.5 py-1.5 text-xs transition-colors',
                viewMode === 'grid'
                  ? 'bg-slate-700 text-slate-200'
                  : 'bg-transparent text-slate-500 hover:text-slate-300'
              )}
              aria-label="Grid view"
              title="Grid view"
            >
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 16 16">
                <rect x="1" y="1" width="6" height="6" rx="1" />
                <rect x="9" y="1" width="6" height="6" rx="1" />
                <rect x="1" y="9" width="6" height="6" rx="1" />
                <rect x="9" y="9" width="6" height="6" rx="1" />
              </svg>
            </button>
            <button
              onClick={() => onViewModeChange('list')}
              className={clsx(
                'px-2.5 py-1.5 text-xs transition-colors border-l border-slate-700',
                viewMode === 'list'
                  ? 'bg-slate-700 text-slate-200'
                  : 'bg-transparent text-slate-500 hover:text-slate-300'
              )}
              aria-label="List view"
              title="List view"
            >
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 16 16">
                <rect x="1" y="2" width="14" height="2.5" rx="1" />
                <rect x="1" y="6.75" width="14" height="2.5" rx="1" />
                <rect x="1" y="11.5" width="14" height="2.5" rx="1" />
              </svg>
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
