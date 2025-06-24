'use client'

import { motion } from 'framer-motion'
import Link from 'next/link'
import { ArrowLeftIcon } from '@heroicons/react/24/outline'

export default function TermsPage() {
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
          <h1 className="text-4xl font-bold text-secondary-900 mb-4">Terms of Service</h1>
          <p className="text-secondary-600">Last updated: {new Date().toLocaleDateString()}</p>
        </motion.div>

        <div className="bg-white rounded-xl p-8 border border-secondary-200">
          <div className="prose prose-lg max-w-none">
            <h2>Acceptance of Terms</h2>
            <p>By accessing and using this service, you accept and agree to be bound by the terms and provision of this agreement.</p>
            
            <h2>Use License</h2>
            <p>Permission is granted to temporarily use our service for personal, non-commercial transitory viewing only.</p>
            
            <h2>Disclaimer</h2>
            <p>The materials on our website are provided on an 'as is' basis. We make no warranties, expressed or implied.</p>
            
            <h2>Limitations</h2>
            <p>In no event shall our company or its suppliers be liable for any damages arising out of the use or inability to use the materials on our website.</p>
            
            <h2>Accuracy of Materials</h2>
            <p>The materials appearing on our website could include technical, typographical, or photographic errors.</p>
            
            <h2>Links</h2>
            <p>We have not reviewed all of the sites linked to our website and are not responsible for the contents of any such linked site.</p>
            
            <h2>Modifications</h2>
            <p>We may revise these terms of service at any time without notice. By using this website, you are agreeing to be bound by the then current version of these terms of service.</p>
          </div>
        </div>
      </div>
    </div>
  )
} 