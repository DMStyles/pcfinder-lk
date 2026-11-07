'use client'

import { Search, PackageOpen, X } from 'lucide-react'

interface EmptyStateProps {
  query?: string
  onClearFilters?: () => void
  hasFilters?: boolean
}

const POPULAR_SUGGESTIONS = [
  'RTX 3060',
  'Ryzen 5 5600',
  'GTX 1660 Super',
  'DDR4 16GB',
  'i5-12400F',
  'RX 6600',
]

export default function EmptyState({ query, onClearFilters, hasFilters }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-20 px-6 text-center">
      {/* Icon */}
      <div className="relative mb-6">
        <div className="w-20 h-20 rounded-2xl bg-slate-800/60 border border-slate-700/60 flex items-center justify-center">
          {query ? (
            <Search className="w-9 h-9 text-slate-600" />
          ) : (
            <PackageOpen className="w-9 h-9 text-slate-600" />
          )}
        </div>
        <div className="absolute -top-1 -right-1 w-6 h-6 rounded-full bg-slate-900 border border-slate-700 flex items-center justify-center">
          <X className="w-3 h-3 text-slate-500" />
        </div>
      </div>

      {/* Title */}
      <h3 className="text-lg font-semibold text-slate-200 mb-2">
        {query ? (
          <>No listings found for &ldquo;<span className="text-indigo-400">{query}</span>&rdquo;</>
        ) : (
          'No listings found'
        )}
      </h3>

      {/* Subtitle */}
      <p className="text-sm text-slate-500 max-w-sm mb-6">
        {hasFilters
          ? 'Try removing some filters or broadening your search.'
          : 'We couldn\'t find any PC hardware matching your search. Try a different query or browse popular searches below.'}
      </p>

      {/* Suggestions */}
      <div className="mb-6">
        <p className="text-xs text-slate-600 mb-3 uppercase tracking-wider font-medium">
          Try searching for
        </p>
        <div className="flex flex-wrap justify-center gap-2">
          {POPULAR_SUGGESTIONS.map(suggestion => (
            <span
              key={suggestion}
              className="px-3 py-1.5 bg-slate-800 border border-slate-700 rounded-full text-xs text-slate-400 hover:text-slate-200 hover:border-slate-600 cursor-default transition-colors"
            >
              {suggestion}
            </span>
          ))}
        </div>
      </div>

      {/* Clear filters */}
      {hasFilters && onClearFilters && (
        <button
          onClick={onClearFilters}
          className="btn-secondary text-sm"
          type="button"
        >
          <X className="w-4 h-4" />
          Clear All Filters
        </button>
      )}
    </div>
  )
}
