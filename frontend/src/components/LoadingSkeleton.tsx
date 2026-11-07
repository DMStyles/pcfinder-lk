'use client'

export default function LoadingSkeleton() {
  return (
    <>
      {Array.from({ length: 6 }).map((_, i) => (
        <div
          key={i}
          className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-col gap-3 animate-pulse"
        >
          {/* Badges row */}
          <div className="flex items-center justify-between">
            <div className="h-5 w-20 bg-slate-800 rounded-full" />
            <div className="h-5 w-16 bg-slate-800 rounded-full" />
          </div>

          {/* Image + Title */}
          <div className="flex gap-3">
            <div className="flex-shrink-0 w-16 h-16 bg-slate-800 rounded-lg" />
            <div className="flex-1 space-y-2">
              <div className="h-4 bg-slate-800 rounded w-full" />
              <div className="h-4 bg-slate-800 rounded w-3/4" />
              <div className="h-3 bg-slate-800 rounded w-1/3 mt-1" />
            </div>
          </div>

          {/* Price */}
          <div className="h-7 w-32 bg-slate-800 rounded" />

          {/* Meta */}
          <div className="space-y-2">
            <div className="h-3.5 bg-slate-800 rounded w-28" />
            <div className="h-3.5 bg-slate-800 rounded w-24" />
            <div className="h-3.5 bg-slate-800 rounded w-32" />
            <div className="h-3.5 bg-slate-800 rounded w-20" />
          </div>

          {/* Button */}
          <div className="h-9 bg-slate-800 rounded-lg mt-auto" />
        </div>
      ))}
    </>
  )
}
