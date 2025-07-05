import React from 'react'
import type { Metadata } from 'next'
import { Inter, JetBrains_Mono } from 'next/font/google'
import './globals.css'
import { cn } from '@/lib/utils'
import { Providers } from './providers'
import { Header } from '@/components/layout/header'
import { Sidebar } from '@/components/layout/sidebar'
import { Toaster } from '@/components/ui/toaster'

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
})

const jetbrainsMono = JetBrains_Mono({
  subsets: ['latin'],
  variable: '--font-mono',
})

export const metadata: Metadata = {
  title: 'Autonoma - AI Webapp Creator',
  description: 'Create full-stack applications through natural language prompts with AI agents',
  keywords: ['AI', 'webapp creator', 'Next.js', 'FastAPI', 'automation', 'code generation'],
  authors: [{ name: 'Autonoma Team' }],
  openGraph: {
    title: 'Autonoma - AI Webapp Creator',
    description: 'Create full-stack applications through natural language prompts',
    type: 'website',
    locale: 'en_US',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Autonoma - AI Webapp Creator',
    description: 'Create full-stack applications through natural language prompts',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={cn(inter.variable, jetbrainsMono.variable)}>
      <body className={cn(
        'min-h-screen bg-background font-sans antialiased',
        'overflow-hidden'
      )}>
        <Providers>
          <div className="flex h-screen">
            <Sidebar />
            <div className="flex flex-1 flex-col">
              <Header />
              <main className="flex-1 overflow-hidden">
                {children}
              </main>
            </div>
          </div>
          <Toaster />
        </Providers>
      </body>
    </html>
  )
}