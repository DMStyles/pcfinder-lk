'use client'

import { Github, Cpu, ExternalLink } from 'lucide-react'

export default function Header() {
  return (
    <header className="sticky top-0 z-50 glassmorphism">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex items-center gap-3">
            <div className="flex items-center justify-center w-9 h-9 rounded-lg bg-gradient-to-br from-indigo-600 to-cyan-600 shadow-lg shadow-indigo-500/20">
              <Cpu className="w-5 h-5 text-white" />
            </div>
            <div className="flex flex-col leading-none">
              <div className="flex items-center gap-1.5">
                <span className="text-xl font-bold tracking-tight text-white">PCFinder</span>
                <span className="text-xl font-bold tracking-tight bg-gradient-to-r from-indigo-400 to-cyan-400 bg-clip-text text-transparent">
                  LK
                </span>
                <span className="text-lg" title="Sri Lanka">🇱🇰</span>
              </div>
              <span className="text-[10px] text-slate-500 font-medium tracking-wide hidden sm:block">
                Sri Lanka&apos;s PC Hardware Price Aggregator
              </span>
            </div>
          </div>

          {/* Nav links */}
          <nav className="flex items-center gap-1">
            <a
              href="https://github.com"
              target="_blank"
              rel="noopener noreferrer"
              className="btn-ghost"
              aria-label="View on GitHub"
            >
              <Github className="w-4 h-4" />
              <span className="hidden sm:inline text-sm">GitHub</span>
              <ExternalLink className="w-3 h-3 opacity-50 hidden sm:block" />
            </a>

            <div className="hidden sm:flex items-center gap-2 ml-2 pl-3 border-l border-slate-800">
              <div className="flex items-center gap-1.5 text-xs text-slate-500">
                <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                <span>Live</span>
              </div>
            </div>
          </nav>
        </div>
      </div>
    </header>
  )
}
