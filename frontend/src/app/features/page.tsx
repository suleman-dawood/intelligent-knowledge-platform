'use client'

import { motion } from 'framer-motion'
import Link from 'next/link'
import { 
  SparklesIcon,
  BookOpenIcon,
  ShareIcon,
  LightBulbIcon,
  ChartBarIcon,
  UserGroupIcon,
  ArrowLeftIcon
} from '@heroicons/react/24/outline'

export default function FeaturesPage() {
  const features = [
    {
      icon: SparklesIcon,
      title: 'AI-Powered Analysis',
      description: 'Advanced AI algorithms analyze your documents to extract key concepts, generate summaries, and provide intelligent insights.',
      features: ['Document parsing', 'Concept extraction', 'Smart summaries', 'Entity recognition']
    },
    {
      icon: BookOpenIcon,
      title: 'Multi-Format Support',
      description: 'Upload PDFs, Word documents, Excel sheets, and more. Our system processes various file formats seamlessly.',
      features: ['PDF processing', 'Word documents', 'Excel spreadsheets', 'Text files']
    },
    {
      icon: ShareIcon,
      title: 'Knowledge Graph',
      description: 'Visualize connections between concepts and topics through our interactive knowledge graph visualization.',
      features: ['Interactive graphs', 'Concept mapping', 'Relationship analysis', 'Visual exploration']
    },
    {
      icon: LightBulbIcon,
      title: 'Smart Insights',
      description: 'Get personalized recommendations and discover new learning paths based on your uploaded content.',
      features: ['Personalized recommendations', 'Learning paths', 'Content suggestions', 'Progress tracking']
    },
    {
      icon: ChartBarIcon,
      title: 'Analytics & Reporting',
      description: 'Monitor your learning progress and see detailed analytics about your study patterns and performance.',
      features: ['Progress tracking', 'Performance metrics', 'Study patterns', 'Custom reports']
    },
    {
      icon: UserGroupIcon,
      title: 'Collaborative Learning',
      description: 'Share insights with classmates, create study groups, and learn together in a collaborative environment.',
      features: ['Study groups', 'Content sharing', 'Collaborative notes', 'Team insights']
    }
  ]

  return (
    <div className="min-h-screen bg-secondary-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Header */}
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
          <h1 className="text-4xl md:text-5xl font-bold text-secondary-900 mb-6">
            Powerful Features
          </h1>
          <p className="text-xl text-secondary-600 max-w-3xl mx-auto leading-relaxed">
            Discover all the tools and capabilities that make our platform the ultimate learning companion for students and researchers.
          </p>
        </motion.div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => {
            const Icon = feature.icon
            return (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="bg-white rounded-2xl p-8 shadow-sm border border-secondary-200 hover:shadow-lg transition-all duration-300"
              >
                <div className="flex items-center mb-6">
                  <div className="w-12 h-12 bg-primary-100 rounded-xl flex items-center justify-center mr-4">
                    <Icon className="h-6 w-6 text-primary-600" />
                  </div>
                  <h3 className="text-xl font-semibold text-secondary-900">{feature.title}</h3>
                </div>
                
                <p className="text-secondary-600 mb-6 leading-relaxed">
                  {feature.description}
                </p>
                
                <ul className="space-y-2">
                  {feature.features.map((item, itemIndex) => (
                    <li key={itemIndex} className="flex items-center text-sm text-secondary-700">
                      <div className="w-1.5 h-1.5 bg-primary-600 rounded-full mr-3"></div>
                      {item}
                    </li>
                  ))}
                </ul>
              </motion.div>
            )
          })}
        </div>

        {/* CTA Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8 }}
          className="text-center mt-16"
        >
          <div className="bg-gradient-to-r from-primary-600 to-primary-700 rounded-2xl p-12">
            <h2 className="text-3xl font-bold text-white mb-4">
              Ready to Get Started?
            </h2>
            <p className="text-primary-100 mb-8 text-lg">
              Join thousands of learners who are already transforming their study experience.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                href="/signup"
                className="inline-flex items-center px-8 py-3 bg-white text-primary-600 font-semibold rounded-xl hover:bg-primary-50 transition-colors"
              >
                Start Free Trial
              </Link>
              <Link
                href="/contact"
                className="inline-flex items-center px-8 py-3 bg-primary-500 text-white font-semibold rounded-xl hover:bg-primary-400 transition-colors border border-primary-400"
              >
                Contact Sales
              </Link>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  )
} 