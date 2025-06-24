'use client'

import { motion } from 'framer-motion'
import Link from 'next/link'
import { 
  ArrowLeftIcon,
  QuestionMarkCircleIcon,
  BookOpenIcon,
  ChatBubbleLeftRightIcon,
  EnvelopeIcon
} from '@heroicons/react/24/outline'

export default function HelpPage() {
  return (
    <div className="min-h-screen bg-secondary-50">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-16"
        >
          <Link 
            href="/"
            className="inline-flex items-center text-primary-600 hover:text-primary-700 mb-8"
          >
            <ArrowLeftIcon className="h-4 w-4 mr-2" />
            Back to Home
          </Link>
          <h1 className="text-4xl font-bold text-secondary-900 mb-6">Help Center</h1>
          <p className="text-xl text-secondary-600">Find answers to common questions and get support</p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div className="bg-white rounded-xl p-8 border border-secondary-200">
            <QuestionMarkCircleIcon className="h-12 w-12 text-primary-600 mb-4" />
            <h3 className="text-xl font-semibold text-secondary-900 mb-4">Frequently Asked Questions</h3>
            <p className="text-secondary-600 mb-6">Browse our comprehensive FAQ section for quick answers.</p>
            <Link href="/faq" className="text-primary-600 hover:text-primary-700 font-medium">
              View FAQ →
            </Link>
          </div>

          <div className="bg-white rounded-xl p-8 border border-secondary-200">
            <BookOpenIcon className="h-12 w-12 text-primary-600 mb-4" />
            <h3 className="text-xl font-semibold text-secondary-900 mb-4">Documentation</h3>
            <p className="text-secondary-600 mb-6">Detailed guides and tutorials to help you get the most out of our platform.</p>
            <Link href="/docs" className="text-primary-600 hover:text-primary-700 font-medium">
              Read Docs →
            </Link>
          </div>

          <div className="bg-white rounded-xl p-8 border border-secondary-200">
            <ChatBubbleLeftRightIcon className="h-12 w-12 text-primary-600 mb-4" />
            <h3 className="text-xl font-semibold text-secondary-900 mb-4">Community Support</h3>
            <p className="text-secondary-600 mb-6">Connect with other users and get help from the community.</p>
            <Link href="/community" className="text-primary-600 hover:text-primary-700 font-medium">
              Join Community →
            </Link>
          </div>

          <div className="bg-white rounded-xl p-8 border border-secondary-200">
            <EnvelopeIcon className="h-12 w-12 text-primary-600 mb-4" />
            <h3 className="text-xl font-semibold text-secondary-900 mb-4">Contact Support</h3>
            <p className="text-secondary-600 mb-6">Need direct help? Reach out to our support team.</p>
            <Link href="/contact" className="text-primary-600 hover:text-primary-700 font-medium">
              Contact Us →
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
} 