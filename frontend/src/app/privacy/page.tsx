'use client'

import { motion } from 'framer-motion'
import Link from 'next/link'
import { ArrowLeftIcon } from '@heroicons/react/24/outline'

export default function PrivacyPage() {
  return (
    <div className="min-h-screen bg-secondary-50">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <Link 
            href="/"
            className="inline-flex items-center text-primary-600 hover:text-primary-700 mb-8"
          >
            <ArrowLeftIcon className="h-4 w-4 mr-2" />
            Back to Home
          </Link>
          <h1 className="text-4xl font-bold text-secondary-900 mb-4">Privacy Policy</h1>
          <p className="text-secondary-600">Last updated: {new Date().toLocaleDateString()}</p>
        </motion.div>

        <div className="bg-white rounded-xl p-8 border border-secondary-200">
          <div className="prose prose-lg max-w-none">
            <h2>Information We Collect</h2>
            <p>We collect information you provide directly to us, such as when you create an account, upload documents, or contact us for support.</p>
            
            <h2>How We Use Your Information</h2>
            <p>We use the information we collect to provide, maintain, and improve our services, process transactions, and communicate with you.</p>
            
            <h2>Information Sharing</h2>
            <p>We do not sell, trade, or otherwise transfer your personal information to third parties without your consent, except as described in this policy.</p>
            
            <h2>Data Security</h2>
            <p>We implement appropriate security measures to protect your personal information against unauthorized access, alteration, disclosure, or destruction.</p>
            
            <h2>Contact Us</h2>
            <p>If you have any questions about this Privacy Policy, please contact us at privacy@homework-analyzer.com.</p>
          </div>
        </div>
      </div>
    </div>
  )
} 