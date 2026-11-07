'use client'

import { MapPin, Clock, Shield, Store, User, ExternalLink, Cpu, Tag } from 'lucide-react'
import type { Listing } from '@/types'
import { formatRelativeTime, formatPrice, clsx } from '@/lib/utils'
import SourceBadge from './SourceBadge'

interface ListingCardProps {
  listing: Listing
}

function ConditionBadge({ condition }: { condition: Listing['condition'] }) {
  const styles: Record<Listing['condition'], string> = {
    'Brand New': 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30',
    'Used / Secondhand': 'bg-amber-500/15 text-amber-400 border-amber-500/30',
    'Unknown': 'bg-slate-500/15 text-slate-400 border-slate-500/30',
  }

  return (
    <span className={clsx('badge-base text-[10px] px-1.5 py-0.5', styles[condition])}>
      {condition === 'Brand New' ? 'Brand New' : condition === 'Used / Secondhand' ? 'Used' : 'Unknown'}
    </span>
  )
}

function ImagePlaceholder({ title }: { title: string }) {
  const initial = title.trim()[0]?.toUpperCase() ?? 'P'

  return (
    <div className="w-full h-full flex flex-col items-center justify-center bg-gradient-to-br from-slate-800 to-slate-900 rounded-lg">
      <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-600/40 to-cyan-600/40 flex items-center justify-center mb-1.5 border border-indigo-500/20">
        <Cpu className="w-5 h-5 text-indigo-400 opacity-70" />
      </div>
      <span className="text-xs text-slate-600 font-medium">{initial}</span>
    </div>
  )
}

export default function ListingCard({ listing }: ListingCardProps) {
  const hasWarranty = listing.warranty &&
    listing.warranty.toLowerCase() !== 'no warranty' &&
    listing.warranty.toLowerCase() !== 'none' &&
    listing.warranty.toLowerCase() !== 'unknown' &&
    listing.warranty.toLowerCase() !== ''

  const dateDisplay = formatRelativeTime(listing.date_posted ?? listing.last_updated)

  return (
    <article className="bg-slate-900 border border-slate-800 hover:border-indigo-500/40 rounded-xl p-4 transition-all duration-200 hover:shadow-lg hover:shadow-indigo-500/10 flex flex-col gap-3 group">
      {/* Top badges row */}
      <div className="flex items-center justify-between gap-2 flex-wrap">
        <SourceBadge source={listing.source_platform} />
        <ConditionBadge condition={listing.condition} />
      </div>

      {/* Image + Title row */}
      <div className="flex gap-3">
        {/* Image thumbnail */}
        <div className="flex-shrink-0 w-16 h-16 rounded-lg overflow-hidden border border-slate-800">
          {listing.image_url ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img
              src={listing.image_url}
              alt={listing.title}
              className="w-full h-full object-cover"
              loading="lazy"
              onError={e => {
                const target = e.currentTarget
                target.style.display = 'none'
                const parent = target.parentElement
                if (parent) {
                  parent.innerHTML = ''
                  const placeholder = document.createElement('div')
                  placeholder.className = 'w-full h-full flex items-center justify-center bg-gradient-to-br from-slate-800 to-slate-900'
                  parent.appendChild(placeholder)
                }
              }}
            />
          ) : (
            <ImagePlaceholder title={listing.title} />
          )}
        </div>

        {/* Title */}
        <div className="flex-1 min-w-0">
          <h3
            className="text-sm font-semibold text-white leading-snug line-clamp-2 group-hover:text-indigo-200 transition-colors"
            title={listing.title}
          >
            {listing.title}
          </h3>
          {listing.category && (
            <div className="flex items-center gap-1 mt-1">
              <Tag className="w-3 h-3 text-slate-600" />
              <span className="text-[10px] text-slate-500">{listing.category}</span>
            </div>
          )}
        </div>
      </div>

      {/* Price */}
      <div className="flex items-baseline gap-2">
        <span className="text-xl font-bold text-indigo-400 tracking-tight">
          {listing.price_display || formatPrice(listing.price_lkr)}
        </span>
      </div>

      {/* Meta info */}
      <div className="space-y-1.5">
        {/* Warranty */}
        <div className="flex items-center gap-1.5">
          <Shield className={clsx('w-3.5 h-3.5 flex-shrink-0', hasWarranty ? 'text-emerald-400' : 'text-slate-600')} />
          <span className={clsx('text-xs', hasWarranty ? 'text-emerald-400' : 'text-slate-600')}>
            {listing.warranty && listing.warranty.toLowerCase() !== '' && listing.warranty.toLowerCase() !== 'unknown'
              ? listing.warranty
              : 'No warranty info'}
          </span>
        </div>

        {/* Location */}
        <div className="flex items-center gap-1.5">
          <MapPin className="w-3.5 h-3.5 text-slate-500 flex-shrink-0" />
          <span className="text-xs text-slate-400 truncate">{listing.location || 'Location unknown'}</span>
        </div>

        {/* Seller type */}
        <div className="flex items-center gap-1.5">
          {listing.seller_type === 'Verified Store' ? (
            <Store className="w-3.5 h-3.5 text-cyan-500 flex-shrink-0" />
          ) : (
            <User className="w-3.5 h-3.5 text-slate-500 flex-shrink-0" />
          )}
          <span
            className={clsx(
              'text-xs',
              listing.seller_type === 'Verified Store' ? 'text-cyan-400' : 'text-slate-400'
            )}
          >
            {listing.seller_type}
          </span>
        </div>

        {/* Date */}
        <div className="flex items-center gap-1.5">
          <Clock className="w-3.5 h-3.5 text-slate-600 flex-shrink-0" />
          <span className="text-xs text-slate-500">{dateDisplay}</span>
        </div>
      </div>

      {/* View listing button */}
      <a
        href={listing.url}
        target="_blank"
        rel="noopener noreferrer"
        className="mt-auto flex items-center justify-center gap-2 w-full py-2 px-4 rounded-lg border border-slate-700 hover:border-indigo-500/60 hover:bg-indigo-500/10 text-slate-400 hover:text-indigo-300 text-sm font-medium transition-all duration-200 group/btn"
        onClick={e => e.stopPropagation()}
      >
        View Listing
        <ExternalLink className="w-3.5 h-3.5 transition-transform group-hover/btn:translate-x-0.5" />
      </a>
    </article>
  )
}
