'use client'

import { useEffect, useRef, useState, useCallback } from 'react'
import { Search, X, Loader2 } from 'lucide-react'
import { getAutocomplete } from '@/lib/api'
import { clsx } from '@/lib/utils'

interface SearchBarProps {
  value: string
  onChange: (value: string) => void
  onSearch: (query: string) => void
  isLoading?: boolean
}

export default function SearchBar({ value, onChange, onSearch, isLoading }: SearchBarProps) {
  const [suggestions, setSuggestions] = useState<string[]>([])
  const [showDropdown, setShowDropdown] = useState(false)
  const [selectedIndex, setSelectedIndex] = useState(-1)
  const [isFocused, setIsFocused] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)
  const dropdownRef = useRef<HTMLDivElement>(null)
  const debounceRef = useRef<NodeJS.Timeout | null>(null)

  const fetchSuggestions = useCallback(async (q: string) => {
    if (q.trim().length < 2) {
      setSuggestions([])
      setShowDropdown(false)
      return
    }
    try {
      const results = await getAutocomplete(q)
      setSuggestions(results)
      setShowDropdown(results.length > 0)
      setSelectedIndex(-1)
    } catch {
      setSuggestions([])
      setShowDropdown(false)
    }
  }, [])

  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current)
    debounceRef.current = setTimeout(() => {
      if (isFocused) fetchSuggestions(value)
    }, 300)
    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current)
    }
  }, [value, isFocused, fetchSuggestions])

  // Close dropdown on outside click
  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(e.target as Node) &&
        inputRef.current &&
        !inputRef.current.contains(e.target as Node)
      ) {
        setShowDropdown(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  function handleKeyDown(e: React.KeyboardEvent<HTMLInputElement>) {
    if (!showDropdown || suggestions.length === 0) {
      if (e.key === 'Enter') {
        handleSearch(value)
      }
      return
    }

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault()
        setSelectedIndex(prev => Math.min(prev + 1, suggestions.length - 1))
        break
      case 'ArrowUp':
        e.preventDefault()
        setSelectedIndex(prev => Math.max(prev - 1, -1))
        break
      case 'Enter':
        e.preventDefault()
        if (selectedIndex >= 0 && suggestions[selectedIndex]) {
          handleSelectSuggestion(suggestions[selectedIndex])
        } else {
          handleSearch(value)
        }
        break
      case 'Escape':
        setShowDropdown(false)
        setSelectedIndex(-1)
        inputRef.current?.blur()
        break
    }
  }

  function handleSelectSuggestion(suggestion: string) {
    onChange(suggestion)
    setShowDropdown(false)
    setSuggestions([])
    setSelectedIndex(-1)
    onSearch(suggestion)
  }

  function handleSearch(q: string) {
    setShowDropdown(false)
    onSearch(q.trim())
  }

  function handleClear() {
    onChange('')
    setSuggestions([])
    setShowDropdown(false)
    setSelectedIndex(-1)
    inputRef.current?.focus()
  }

  return (
    <div className="relative w-full">
      <div
        className={clsx(
          'relative flex items-center rounded-xl border transition-all duration-200',
          isFocused
            ? 'border-indigo-500 shadow-lg shadow-indigo-500/20 bg-slate-900'
            : 'border-slate-700 bg-slate-900 hover:border-slate-600'
        )}
      >
        {/* Search icon / loader */}
        <div className="absolute left-4 flex items-center justify-center text-slate-400">
          {isLoading ? (
            <Loader2 className="w-5 h-5 animate-spin text-indigo-400" />
          ) : (
            <Search className="w-5 h-5" />
          )}
        </div>

        {/* Input */}
        <input
          ref={inputRef}
          type="text"
          value={value}
          onChange={e => onChange(e.target.value)}
          onKeyDown={handleKeyDown}
          onFocus={() => {
            setIsFocused(true)
            if (suggestions.length > 0) setShowDropdown(true)
          }}
          onBlur={() => setIsFocused(false)}
          placeholder="Search CPUs, GPUs, RAM, Motherboards..."
          className="w-full pl-12 pr-28 py-4 bg-transparent text-white placeholder-slate-500 text-base focus:outline-none rounded-xl"
          autoComplete="off"
          spellCheck={false}
          aria-label="Search PC hardware"
          aria-autocomplete="list"
          aria-expanded={showDropdown}
          role="combobox"
        />

        {/* Clear + Search buttons */}
        <div className="absolute right-2 flex items-center gap-1.5">
          {value && (
            <button
              onClick={handleClear}
              className="p-1.5 text-slate-500 hover:text-slate-300 transition-colors rounded-lg hover:bg-slate-800"
              aria-label="Clear search"
              type="button"
            >
              <X className="w-4 h-4" />
            </button>
          )}
          <button
            onClick={() => handleSearch(value)}
            disabled={isLoading}
            className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-60 text-white font-medium text-sm rounded-lg transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 focus:ring-offset-slate-900"
            type="button"
            aria-label="Search"
          >
            <Search className="w-4 h-4" />
            <span className="hidden sm:inline">Search</span>
          </button>
        </div>
      </div>

      {/* Autocomplete dropdown */}
      {showDropdown && suggestions.length > 0 && (
        <div
          ref={dropdownRef}
          className="absolute top-full left-0 right-0 mt-2 bg-slate-900 border border-slate-700 rounded-xl shadow-xl shadow-black/50 z-50 overflow-hidden animate-slide-down"
          role="listbox"
          aria-label="Search suggestions"
        >
          {suggestions.map((suggestion, index) => (
            <button
              key={suggestion}
              onClick={() => handleSelectSuggestion(suggestion)}
              className={clsx(
                'w-full text-left px-4 py-3 flex items-center gap-3 text-sm transition-colors',
                index === selectedIndex
                  ? 'bg-indigo-600/20 text-indigo-300'
                  : 'text-slate-300 hover:bg-slate-800'
              )}
              role="option"
              aria-selected={index === selectedIndex}
              type="button"
            >
              <Search className="w-4 h-4 text-slate-500 flex-shrink-0" />
              <span>{suggestion}</span>
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
