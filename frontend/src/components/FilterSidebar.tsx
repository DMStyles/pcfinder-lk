'use client'

import { SlidersHorizontal, X } from 'lucide-react'
import type { SearchFilters } from '@/types'
import { clsx } from '@/lib/utils'

interface FilterSidebarProps {
  filters: SearchFilters
  onFiltersChange: (filters: Partial<SearchFilters>) => void
  onApply: () => void
  onClear: () => void
  isMobileOpen?: boolean
  onMobileClose?: () => void
}

const CONDITIONS = [
  { value: 'all', label: 'All' },
  { value: 'brand_new', label: 'Brand New' },
  { value: 'used', label: 'Used / Secondhand' },
]

const LOCATIONS = [
  { value: 'all', label: 'All Locations' },
  { value: 'colombo', label: 'Colombo' },
  { value: 'gampaha', label: 'Gampaha' },
  { value: 'negombo', label: 'Negombo' },
  { value: 'western_province', label: 'Western Province' },
  { value: 'island_wide', label: 'Island-wide' },
]

const SOURCE_TYPES = [
  { value: 'all', label: 'All Sources' },
  { value: 'retail', label: 'Retail Stores Only' },
  { value: 'classified', label: 'Classifieds Only' },
]

const WARRANTY_OPTIONS = [
  { value: 'any', label: 'Any' },
  { value: 'has_warranty', label: 'Has Warranty' },
  { value: '1year', label: '1+ Year Warranty' },
  { value: 'official', label: 'Official Distributor' },
]

interface RadioGroupProps {
  label: string
  name: string
  options: { value: string; label: string }[]
  value: string
  onChange: (value: string) => void
}

function RadioGroup({ label, name, options, value, onChange }: RadioGroupProps) {
  return (
    <div>
      <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2.5">{label}</p>
      <div className="space-y-1.5">
        {options.map(option => (
          <label
            key={option.value}
            className="flex items-center gap-2.5 cursor-pointer group"
          >
            <div className="relative">
              <input
                type="radio"
                name={name}
                value={option.value}
                checked={value === option.value}
                onChange={() => onChange(option.value)}
                className="sr-only"
              />
              <div
                className={clsx(
                  'w-4 h-4 rounded-full border-2 transition-all duration-150 flex items-center justify-center',
                  value === option.value
                    ? 'border-indigo-500 bg-indigo-500'
                    : 'border-slate-600 bg-transparent group-hover:border-slate-400'
                )}
              >
                {value === option.value && (
                  <div className="w-1.5 h-1.5 rounded-full bg-white" />
                )}
              </div>
            </div>
            <span
              className={clsx(
                'text-sm transition-colors',
                value === option.value ? 'text-slate-100 font-medium' : 'text-slate-400 group-hover:text-slate-300'
              )}
            >
              {option.label}
            </span>
          </label>
        ))}
      </div>
    </div>
  )
}

function Divider() {
  return <div className="border-t border-slate-800" />
}

export default function FilterSidebar({
  filters,
  onFiltersChange,
  onApply,
  onClear,
  isMobileOpen = false,
  onMobileClose,
}: FilterSidebarProps) {
  const content = (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-5">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <SlidersHorizontal className="w-4 h-4 text-indigo-400" />
          <h2 className="text-sm font-semibold text-slate-200">Filters</h2>
        </div>
        {onMobileClose && (
          <button
            onClick={onMobileClose}
            className="lg:hidden p-1 rounded-lg text-slate-500 hover:text-slate-300 hover:bg-slate-800 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </div>

      <Divider />

      {/* Condition */}
      <RadioGroup
        label="Condition"
        name="condition"
        options={CONDITIONS}
        value={filters.condition || 'all'}
        onChange={v => onFiltersChange({ condition: v })}
      />

      <Divider />

      {/* Price Range */}
      <div>
        <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2.5">
          Price Range (LKR)
        </p>
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <span className="text-xs text-slate-500 w-7 flex-shrink-0">Min</span>
            <div className="relative flex-1">
              <span className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500 text-xs font-medium">Rs.</span>
              <input
                type="number"
                placeholder="0"
                value={filters.min_price}
                onChange={e => onFiltersChange({ min_price: e.target.value })}
                className="w-full pl-9 pr-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
                min="0"
              />
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-xs text-slate-500 w-7 flex-shrink-0">Max</span>
            <div className="relative flex-1">
              <span className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500 text-xs font-medium">Rs.</span>
              <input
                type="number"
                placeholder="Any"
                value={filters.max_price}
                onChange={e => onFiltersChange({ max_price: e.target.value })}
                className="w-full pl-9 pr-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
                min="0"
              />
            </div>
          </div>
        </div>
      </div>

      <Divider />

      {/* Location */}
      <div>
        <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2.5">
          Location
        </p>
        <select
          value={filters.location || 'all'}
          onChange={e => onFiltersChange({ location: e.target.value })}
          className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all appearance-none cursor-pointer"
          style={{
            backgroundImage: `url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%2364748b' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M6 8l4 4 4-4'/%3e%3c/svg%3e")`,
            backgroundPosition: 'right 0.5rem center',
            backgroundRepeat: 'no-repeat',
            backgroundSize: '1.5em 1.5em',
            paddingRight: '2.5rem',
          }}
        >
          {LOCATIONS.map(loc => (
            <option key={loc.value} value={loc.value} className="bg-slate-800">
              {loc.label}
            </option>
          ))}
        </select>
      </div>

      <Divider />

      {/* Source Type */}
      <RadioGroup
        label="Source Type"
        name="source_type"
        options={SOURCE_TYPES}
        value={filters.source_type || 'all'}
        onChange={v => onFiltersChange({ source_type: v })}
      />

      <Divider />

      {/* Warranty */}
      <RadioGroup
        label="Warranty"
        name="warranty"
        options={WARRANTY_OPTIONS}
        value={filters.warranty || 'any'}
        onChange={v => onFiltersChange({ warranty: v })}
      />

      <Divider />

      {/* Action buttons */}
      <div className="space-y-2 pt-1">
        <button
          onClick={onApply}
          className="btn-primary w-full justify-center py-2.5"
          type="button"
        >
          Apply Filters
        </button>
        <button
          onClick={onClear}
          className="w-full text-center text-sm text-slate-500 hover:text-slate-300 transition-colors py-1"
          type="button"
        >
          Clear All
        </button>
      </div>
    </div>
  )

  return (
    <>
      {/* Desktop sidebar */}
      <div className="hidden lg:block w-64 flex-shrink-0">
        {content}
      </div>

      {/* Mobile drawer overlay */}
      {isMobileOpen && (
        <div className="lg:hidden fixed inset-0 z-50 flex">
          <div
            className="fixed inset-0 bg-black/60 backdrop-blur-sm"
            onClick={onMobileClose}
          />
          <div className="relative ml-auto w-80 max-w-full h-full bg-slate-950 overflow-y-auto p-4 shadow-2xl animate-slide-down">
            {content}
          </div>
        </div>
      )}
    </>
  )
}
