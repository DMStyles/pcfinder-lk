import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
})

export const metadata: Metadata = {
  title: 'PCFinder LK — Sri Lanka PC Hardware Price Aggregator',
  description:
    'Find the best prices on PC hardware in Sri Lanka. We aggregate listings from ikman, Facebook Marketplace, Nanotek, Redline, Barclays, and more to help you find CPUs, GPUs, RAM, motherboards, and other PC components at the best prices.',
  keywords: [
    'PC hardware Sri Lanka',
    'computer parts Sri Lanka',
    'GPU price Sri Lanka',
    'CPU price LKR',
    'gaming PC components',
    'ikman tech',
    'Nanotek Sri Lanka',
    'Redline computers',
  ],
  authors: [{ name: 'PCFinder LK' }],
  themeColor: '#0f172a',
  openGraph: {
    title: 'PCFinder LK — Sri Lanka PC Hardware Price Aggregator',
    description: 'Find the best PC hardware deals in Sri Lanka from multiple sources',
    type: 'website',
    locale: 'en_LK',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'PCFinder LK — Sri Lanka PC Hardware Price Aggregator',
    description: 'Find the best PC hardware deals in Sri Lanka',
  },
  robots: {
    index: true,
    follow: true,
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.variable} font-sans min-h-screen bg-slate-950 text-slate-200`}>
        {children}
      </body>
    </html>
  )
}
