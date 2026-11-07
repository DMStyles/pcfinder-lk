export interface Listing {
  id: string
  title: string
  price_lkr: number | null
  price_display: string
  condition: 'Brand New' | 'Used / Secondhand' | 'Unknown'
  warranty: string
  source_platform: string
  seller_type: 'Verified Store' | 'Individual Seller'
  location: string
  url: string
  date_posted: string | null
  last_updated: string | null
  image_url: string | null
  category: string | null
}

export interface SearchResponse {
  query: string
  total: number
  results: Listing[]
  cached: boolean
  sources_queried: string[]
}

export interface SearchFilters {
  q: string
  condition: string
  min_price: string
  max_price: string
  location: string
  source_type: string
  warranty: string
  sort: string
}
