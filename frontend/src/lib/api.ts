import type { SearchFilters, SearchResponse } from '@/types'
import { filtersToSearchParams } from '@/lib/utils'

const BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export async function searchListings(filters: SearchFilters): Promise<SearchResponse> {
  const params = filtersToSearchParams(filters)
  const url = `/api/search?${params.toString()}`

  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
    next: { revalidate: 60 },
  })

  if (!response.ok) {
    throw new Error(`Search failed: ${response.status} ${response.statusText}`)
  }

  return response.json()
}

export async function getAutocomplete(q: string): Promise<string[]> {
  if (!q || q.trim().length < 2) return []

  const params = new URLSearchParams({ q: q.trim() })
  const url = `${BASE}/api/autocomplete?${params.toString()}`

  try {
    const response = await fetch(url, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
      signal: AbortSignal.timeout(3000),
    })

    if (!response.ok) return []

    const data = await response.json()
    if (Array.isArray(data)) return data as string[]
    if (data?.suggestions && Array.isArray(data.suggestions)) return data.suggestions as string[]

    return []
  } catch {
    return []
  }
}
