'use client'

import { useState, useEffect, useCallback, useRef } from 'react'
import { SlidersHorizontal, AlertCircle, RefreshCw, Cpu, Zap, ChevronRight } from 'lucide-react'
import Header from '@/components/Header'
import SearchBar from '@/components/SearchBar'
import FilterSidebar from '@/components/FilterSidebar'
import ListingCard from '@/components/ListingCard'
import SortBar from '@/components/SortBar'
import LoadingSkeleton from '@/components/LoadingSkeleton'
import EmptyState from '@/components/EmptyState'
import type { SearchFilters, SearchResponse } from '@/types'
import { searchListings } from '@/lib/api'
import { clsx } from '@/lib/utils'

const DEFAULT_FILTERS: SearchFilters = {
  q: '',
  condition: 'all',
  min_price: '',
  max_price: '',
  location: 'all',
  source_type: 'all',
  warranty: 'any',
  sort: 'relevance',
}

const POPULAR_CHIPS = [
  'Ryzen 5 5600',
  'RTX 3060',
  'GTX 1660 Super',
  'DDR4 16GB',
  'i5-12400F',
  'RX 6600',
]

const SOURCE_LOGOS: { name: string; color: string }[] = [
  { name: 'ikman', color: 'text-orange-400' },
  { name: 'Nanotek', color: 'text-indigo-400' },
  { name: 'Redline', color: 'text-red-400' },
  { name: 'Barclays', color: 'text-emerald-400' },
  { name: 'MD Computers', color: 'text-teal-400' },
  { name: 'Pentium City', color: 'text-purple-400' },
  { name: 'PC Builders LK', color: 'text-rose-400' },
  { name: 'Winsoft', color: 'text-sky-400' },
  { name: 'MSK', color: 'text-amber-400' },
  { name: 'Chama', color: 'text-yellow-400' },
  { name: 'FB Marketplace', color: 'text-blue-400' },
]

function hasActiveFilters(filters: SearchFilters): boolean {
  return (
    filters.condition !== 'all' ||
    filters.min_price !== '' ||
    filters.max_price !== '' ||
    filters.location !== 'all' ||
    filters.source_type !== 'all' ||
    filters.warranty !== 'any'
  )
}

export default function HomePage() {
  const [filters, setFilters] = useState<SearchFilters>(DEFAULT_FILTERS)
  const [pendingFilters, setPendingFilters] = useState<SearchFilters>(DEFAULT_FILTERS)
  const [searchInput, setSearchInput] = useState('')
  const [results, setResults] = useState<SearchResponse | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [hasSearched, setHasSearched] = useState(false)
  const [isMobileFilterOpen, setIsMobileFilterOpen] = useState(false)
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')
  const abortRef = useRef<AbortController | null>(null)

  const doSearch = useCallback(async (activeFilters: SearchFilters) => {
    if (!activeFilters.q.trim()) return

    // Cancel any in-flight request
    if (abortRef.current) abortRef.current.abort()
    abortRef.current = new AbortController()

    setIsLoading(true)
    setError(null)
    setHasSearched(true)

    try {
      const data = await searchListings(activeFilters)
      setResults(data)
    } catch (err: unknown) {
      if (err instanceof Error && err.name === 'AbortError') return
      const msg = err instanceof Error ? err.message : 'An unexpected error occurred'
      setError(msg)
      setResults(null)
    } finally {
      setIsLoading(false)
    }
  }, [])

  function handleSearch(q: string) {
    const trimmed = q.trim()
    if (!trimmed) return
    setSearchInput(trimmed)
    const newFilters = { ...pendingFilters, q: trimmed }
    setFilters(newFilters)
    setPendingFilters(newFilters)
    doSearch(newFilters)
  }

  function handleChipClick(chip: string) {
    setSearchInput(chip)
    const newFilters = { ...pendingFilters, q: chip }
    setFilters(newFilters)
    setPendingFilters(newFilters)
    doSearch(newFilters)
  }

  function handleFilterChange(partial: Partial<SearchFilters>) {
    setPendingFilters(prev => ({ ...prev, ...partial }))
  }

  function handleApplyFilters() {
    const newFilters = { ...pendingFilters, q: searchInput || pendingFilters.q }
    setFilters(newFilters)
    setIsMobileFilterOpen(false)
    if (newFilters.q.trim()) {
      doSearch(newFilters)
    }
  }

  function handleClearFilters() {
    const cleared = { ...DEFAULT_FILTERS, q: filters.q }
    setFilters(cleared)
    setPendingFilters(cleared)
    if (cleared.q.trim()) {
      doSearch(cleared)
    }
    setIsMobileFilterOpen(false)
  }

  function handleSortChange(sort: string) {
    const newFilters = { ...filters, sort }
    setFilters(newFilters)
    setPendingFilters(newFilters)
    if (newFilters.q.trim()) {
      doSearch(newFilters)
    }
  }

  function handleRetry() {
    doSearch(filters)
  }

  const activeFilterCount = Object.entries(pendingFilters).filter(([key, val]) => {
    if (key === 'q' || key === 'sort') return false
    if (key === 'condition' && val === 'all') return false
    if (key === 'location' && val === 'all') return false
    if (key === 'source_type' && val === 'all') return false
    if (key === 'warranty' && val === 'any') return false
    if ((key === 'min_price' || key === 'max_price') && val === '') return false
    return true
  }).length

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col">
      <Header />

      {/* Hero section */}
      <section className="relative overflow-hidden">
        {/* Background glow */}
        <div className="absolute inset-0 bg-hero-gradient pointer-events-none" />
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[400px] bg-indigo-600/5 rounded-full blur-3xl pointer-events-none" />

        <div className="relative max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 pt-14 pb-10">
          {/* Badge */}
          <div className="flex justify-center mb-5">
            <span className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-medium">
              <Zap className="w-3 h-3" />
              Aggregating from {SOURCE_LOGOS.length}+ sources
            </span>
          </div>

          {/* Headline */}
          <h1 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold text-center tracking-tight mb-4 leading-tight">
            Find the Best{' '}
            <span className="text-gradient-primary">PC Deals</span>
            <br />
            in Sri Lanka 🇱🇰
          </h1>

          {/* Subheading */}
          <p className="text-center text-slate-400 text-base sm:text-lg mb-8 max-w-2xl mx-auto leading-relaxed">
            We search{' '}
            {SOURCE_LOGOS.map((s, i) => (
              <span key={s.name}>
                <span className={clsx('font-medium', s.color)}>{s.name}</span>
                {i < SOURCE_LOGOS.length - 2 ? ', ' : i === SOURCE_LOGOS.length - 2 ? ' & ' : ''}
              </span>
            ))}{' '}
            so you don&apos;t have to.
          </p>

          {/* Search bar */}
          <div className="max-w-2xl mx-auto">
            <SearchBar
              value={searchInput}
              onChange={setSearchInput}
              onSearch={handleSearch}
              isLoading={isLoading}
            />
          </div>

          {/* Popular chips */}
          <div className="flex flex-wrap justify-center gap-2 mt-5">
            <span className="text-xs text-slate-600 self-center mr-1">Popular:</span>
            {POPULAR_CHIPS.map(chip => (
              <button
                key={chip}
                onClick={() => handleChipClick(chip)}
                className={clsx(
                  'px-3 py-1.5 rounded-full text-xs font-medium border transition-all duration-200',
                  filters.q === chip && hasSearched
                    ? 'bg-indigo-600/20 border-indigo-500/60 text-indigo-300'
                    : 'bg-slate-900 border-slate-700 text-slate-400 hover:border-slate-500 hover:text-slate-300 hover:bg-slate-800'
                )}
                type="button"
              >
                {chip}
              </button>
            ))}
          </div>
        </div>
      </section>

      {/* Main content area */}
      {hasSearched && (
        <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 pb-16">
          {/* Mobile filter toggle */}
          <div className="lg:hidden mb-4">
            <button
              onClick={() => setIsMobileFilterOpen(true)}
              className="btn-secondary"
              type="button"
            >
              <SlidersHorizontal className="w-4 h-4" />
              Filters
              {activeFilterCount > 0 && (
                <span className="ml-1 w-5 h-5 rounded-full bg-indigo-600 text-white text-xs flex items-center justify-center font-bold">
                  {activeFilterCount}
                </span>
              )}
            </button>
          </div>

          <div className="flex gap-6 items-start">
            {/* Filter sidebar */}
            <FilterSidebar
              filters={pendingFilters}
              onFiltersChange={handleFilterChange}
              onApply={handleApplyFilters}
              onClear={handleClearFilters}
              isMobileOpen={isMobileFilterOpen}
              onMobileClose={() => setIsMobileFilterOpen(false)}
            />

            {/* Results area */}
            <div className="flex-1 min-w-0">
              {/* Sort bar */}
              {!error && (
                <SortBar
                  total={results?.total ?? 0}
                  query={results?.query ?? filters.q}
                  sort={filters.sort}
                  onSortChange={handleSortChange}
                  viewMode={viewMode}
                  onViewModeChange={setViewMode}
                  isLoading={isLoading}
                  sourcesQueried={results?.sources_queried ?? []}
                  cached={results?.cached}
                />
              )}

              {/* Error state */}
              {error && !isLoading && (
                <div className="flex flex-col items-center justify-center py-20 text-center">
                  <div className="w-16 h-16 rounded-2xl bg-red-500/10 border border-red-500/20 flex items-center justify-center mb-4">
                    <AlertCircle className="w-8 h-8 text-red-400" />
                  </div>
                  <h3 className="text-lg font-semibold text-slate-200 mb-2">Something went wrong</h3>
                  <p className="text-sm text-slate-500 max-w-sm mb-6">{error}</p>
                  <button onClick={handleRetry} className="btn-secondary" type="button">
                    <RefreshCw className="w-4 h-4" />
                    Try again
                  </button>
                </div>
              )}

              {/* Results grid */}
              {!error && (
                <div
                  className={clsx(
                    'grid gap-4',
                    viewMode === 'grid'
                      ? 'grid-cols-1 sm:grid-cols-2 xl:grid-cols-3'
                      : 'grid-cols-1'
                  )}
                >
                  {isLoading ? (
                    <LoadingSkeleton />
                  ) : results && results.results.length > 0 ? (
                    results.results.map(listing => (
                      <ListingCard key={listing.id} listing={listing} />
                    ))
                  ) : !isLoading && results && results.results.length === 0 ? (
                    <div className="col-span-full">
                      <EmptyState
                        query={filters.q}
                        hasFilters={hasActiveFilters(filters)}
                        onClearFilters={handleClearFilters}
                      />
                    </div>
                  ) : null}
                </div>
              )}
            </div>
          </div>
        </main>
      )}

      {/* Landing state (before first search) */}
      {!hasSearched && (
        <section className="flex-1 flex flex-col items-center justify-center pb-24 px-4">
          <div className="max-w-3xl w-full">
            {/* Feature tiles */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-4">
              {[
                {
                  icon: <Cpu className="w-6 h-6 text-indigo-400" />,
                  title: 'All Categories',
                  desc: 'CPUs, GPUs, RAM, Storage, PSUs, Motherboards & more',
                  bg: 'from-indigo-600/10 to-indigo-600/5',
                  border: 'border-indigo-500/20',
                },
                {
                  icon: <Zap className="w-6 h-6 text-cyan-400" />,
                  title: 'Real-time Prices',
                  desc: 'Up-to-date listings from multiple Sri Lankan platforms',
                  bg: 'from-cyan-600/10 to-cyan-600/5',
                  border: 'border-cyan-500/20',
                },
                {
                  icon: <SlidersHorizontal className="w-6 h-6 text-purple-400" />,
                  title: 'Smart Filters',
                  desc: 'Filter by condition, price, location, warranty & seller',
                  bg: 'from-purple-600/10 to-purple-600/5',
                  border: 'border-purple-500/20',
                },
              ].map(feature => (
                <div
                  key={feature.title}
                  className={clsx(
                    'rounded-xl p-5 border bg-gradient-to-br',
                    feature.bg,
                    feature.border
                  )}
                >
                  <div className="mb-3">{feature.icon}</div>
                  <h3 className="text-sm font-semibold text-slate-200 mb-1">{feature.title}</h3>
                  <p className="text-xs text-slate-500 leading-relaxed">{feature.desc}</p>
                </div>
              ))}
            </div>

            {/* Source list */}
            <div className="mt-8 p-4 bg-slate-900/50 border border-slate-800 rounded-xl">
              <p className="text-xs text-slate-600 font-medium uppercase tracking-wider mb-3 text-center">
                Aggregating from
              </p>
              <div className="flex flex-wrap justify-center gap-3">
                {SOURCE_LOGOS.map(s => (
                  <span
                    key={s.name}
                    className={clsx('text-sm font-semibold', s.color)}
                  >
                    {s.name}
                  </span>
                ))}
                <span className="text-sm font-semibold text-slate-600">& more</span>
              </div>
            </div>
          </div>
        </section>
      )}

      {/* Footer */}
      <footer className="border-t border-slate-800 py-6 mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-slate-600">
            <div className="flex items-center gap-2">
              <span className="font-bold text-slate-500">PCFinder LK</span>
              <span>🇱🇰</span>
              <span>Sri Lanka&apos;s PC Hardware Price Aggregator</span>
            </div>
            <div className="flex items-center gap-4">
              <span>Not affiliated with any listed platforms</span>
              <span className="text-slate-700">•</span>
              <span>Prices may vary</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}
