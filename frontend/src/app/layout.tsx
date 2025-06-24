import './globals.css'
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import Header from '../components/layout/Header'
import Footer from '../components/Footer'
import NotificationSystem from '../components/ui/NotificationSystem'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Homework Analyzer - AI-Powered Learning Platform',
  description: 'Transform your learning experience with AI-powered document analysis, knowledge extraction, and intelligent insights.',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <div className="min-h-screen flex flex-col bg-secondary-50">
          <Header />
          <main className="flex-1">
            {children}
          </main>
          <Footer />
          <NotificationSystem />
        </div>
      </body>
    </html>
  )
}