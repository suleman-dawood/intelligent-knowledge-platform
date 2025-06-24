'use client'

import { useState } from 'react'
import Link from 'next/link'
import { motion } from 'framer-motion'
import { 
  MagnifyingGlassIcon, 
  DocumentTextIcon, 
  ShareIcon, 
  CogIcon,
  SparklesIcon,
  AcademicCapIcon,
  BookOpenIcon,
  LightBulbIcon,
  ChartBarIcon,
  UserGroupIcon,
  DocumentDuplicateIcon,
  ArrowRightIcon
} from '@heroicons/react/24/outline'
import SearchBox from '@/components/SearchBox'

export default function Home() {
  const [query, setQuery] = useState('')
  
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    if (query.trim()) {
      window.location.href = `/search?q=${encodeURIComponent(query)}`
    }
  }
  
  const features = [
    {
      icon: SparklesIcon,
      title: 'AI-Powered Analysis',
      description: 'Advanced AI algorithms analyze your documents to extract key concepts, generate summaries, and provide intelligent insights.',
      color: 'bg-primary-100 text-primary-600'
    },
    {
      icon: BookOpenIcon,
      title: 'Multi-Format Support',
      description: 'Upload PDFs, Word documents, Excel sheets, and more. Our system processes various file formats seamlessly.',
      color: 'bg-success-100 text-success-600'
    },
    {
      icon: ShareIcon,
      title: 'Knowledge Graph',
      description: 'Visualize connections between concepts and topics through our interactive knowledge graph visualization.',
      color: 'bg-warning-100 text-warning-600'
    },
    {
      icon: LightBulbIcon,
      title: 'Smart Insights',
      description: 'Get personalized recommendations and discover new learning paths based on your uploaded content.',
      color: 'bg-error-100 text-error-600'
    },
    {
      icon: ChartBarIcon,
      title: 'Progress Tracking',
      description: 'Monitor your learning progress and see detailed analytics about your study patterns and performance.',
      color: 'bg-info-100 text-info-600'
    },
    {
      icon: UserGroupIcon,
      title: 'Collaborative Learning',
      description: 'Share insights with classmates, create study groups, and learn together in a collaborative environment.',
      color: 'bg-secondary-100 text-secondary-600'
    }
  ]

  const stats = [
    { label: 'Documents Processed', value: '50,000+', icon: DocumentDuplicateIcon },
    { label: 'Concepts Extracted', value: '125,000+', icon: LightBulbIcon },
    { label: 'Knowledge Connections', value: '350,000+', icon: ShareIcon },
    { label: 'Active Learners', value: '2,500+', icon: AcademicCapIcon },
  ]
  
  return (
    <div className="min-h-screen bg-secondary-50">
      {/* Hero Section */}
      <div className="relative bg-gradient-to-br from-primary-600 via-primary-700 to-primary-800 overflow-hidden">
        <div className="absolute inset-0 bg-black opacity-10"></div>
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 lg:py-32">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center"
          >
            <h1 className="text-4xl md:text-6xl lg:text-7xl font-bold text-white mb-6">
              <span className="block">Transform Your</span>
              <span className="block bg-gradient-to-r from-yellow-300 to-orange-300 bg-clip-text text-transparent">
                Learning Experience
              </span>
        </h1>
            <p className="max-w-3xl mx-auto text-xl md:text-2xl text-primary-100 mb-12 leading-relaxed">
              Upload your homework, research papers, and study materials. Let AI extract insights, 
              create knowledge maps, and accelerate your learning journey.
            </p>
            
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.2 }}
              className="max-w-2xl mx-auto mb-12"
            >
          <SearchBox 
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onSubmit={handleSearch}
                placeholder="Search your knowledge base or ask a question..."
            fullWidth
                className="shadow-2xl"
              />
            </motion.div>
            
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.4 }}
              className="flex flex-col sm:flex-row gap-4 justify-center items-center"
            >
              <Link 
                href="/search" 
                className="inline-flex items-center px-8 py-4 bg-white text-primary-700 font-semibold rounded-xl hover:bg-primary-50 transition-all duration-200 shadow-lg hover:shadow-xl transform hover:-translate-y-1"
              >
                <MagnifyingGlassIcon className="h-5 w-5 mr-2" />
                Start Searching
                <ArrowRightIcon className="h-4 w-4 ml-2" />
              </Link>
              <Link 
                href="/content" 
                className="inline-flex items-center px-8 py-4 bg-primary-500 text-white font-semibold rounded-xl hover:bg-primary-400 transition-all duration-200 shadow-lg hover:shadow-xl transform hover:-translate-y-1"
              >
                <DocumentTextIcon className="h-5 w-5 mr-2" />
                Upload Content
                <ArrowRightIcon className="h-4 w-4 ml-2" />
              </Link>
            </motion.div>
          </motion.div>
        </div>
        
        {/* Decorative elements */}
        <div className="absolute top-0 left-0 w-full h-full overflow-hidden">
          <div className="absolute -top-40 -right-40 w-80 h-80 bg-primary-300 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse"></div>
          <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-yellow-300 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse"></div>
        </div>
      </div>
      
      {/* Features Section */}
      <div className="py-24 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl md:text-5xl font-bold text-secondary-900 mb-6">
              Powerful Learning Tools
          </h2>
            <p className="max-w-3xl mx-auto text-xl text-secondary-600 leading-relaxed">
              Our AI-powered platform combines cutting-edge technology with intuitive design 
              to create the ultimate learning companion for students and researchers.
            </p>
          </motion.div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => {
              const Icon = feature.icon;
              return (
                <motion.div
                  key={feature.title}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: index * 0.1 }}
                  viewport={{ once: true }}
                  className="bg-white rounded-2xl p-8 shadow-sm border border-secondary-200 hover:shadow-lg transition-all duration-300 transform hover:-translate-y-1"
                >
                  <div className={`inline-flex items-center justify-center w-12 h-12 rounded-xl ${feature.color} mb-6`}>
                    <Icon className="h-6 w-6" />
                </div>
                  <h3 className="text-xl font-semibold text-secondary-900 mb-4">
                    {feature.title}
                  </h3>
                  <p className="text-secondary-600 leading-relaxed">
                    {feature.description}
                  </p>
                </motion.div>
              );
            })}
          </div>
        </div>
      </div>
      
      {/* Stats Section */}
      <div className="bg-white py-24 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl font-bold text-secondary-900 mb-4">
              Trusted by Learners Worldwide
            </h2>
            <p className="text-xl text-secondary-600">
              Join thousands of students and researchers who are accelerating their learning
            </p>
          </motion.div>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
            {stats.map((stat, index) => {
              const Icon = stat.icon;
              return (
                <motion.div
                  key={stat.label}
                  initial={{ opacity: 0, scale: 0.9 }}
                  whileInView={{ opacity: 1, scale: 1 }}
                  transition={{ duration: 0.6, delay: index * 0.1 }}
                  viewport={{ once: true }}
                  className="text-center"
                >
                  <div className="inline-flex items-center justify-center w-16 h-16 bg-primary-100 text-primary-600 rounded-2xl mb-4">
                    <Icon className="h-8 w-8" />
                </div>
                  <div className="text-3xl font-bold text-secondary-900 mb-2">
                    {stat.value}
                </div>
                  <div className="text-secondary-600 font-medium">
                    {stat.label}
              </div>
                </motion.div>
              );
            })}
                </div>
              </div>
            </div>
            
      {/* CTA Section */}
      <div className="bg-secondary-900 py-24 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
          >
            <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
              Ready to Transform Your Learning?
            </h2>
            <p className="text-xl text-secondary-300 mb-12 leading-relaxed">
              Start your journey towards smarter, more efficient learning. 
              Upload your first document and experience the power of AI-driven insights.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link 
                href="/signup" 
                className="inline-flex items-center px-8 py-4 bg-primary-600 text-white font-semibold rounded-xl hover:bg-primary-700 transition-all duration-200 shadow-lg hover:shadow-xl transform hover:-translate-y-1"
              >
                <AcademicCapIcon className="h-5 w-5 mr-2" />
                Get Started Free
                <ArrowRightIcon className="h-4 w-4 ml-2" />
              </Link>
              <Link 
                href="/knowledge-graph" 
                className="inline-flex items-center px-8 py-4 bg-secondary-800 text-white font-semibold rounded-xl hover:bg-secondary-700 transition-all duration-200 shadow-lg hover:shadow-xl transform hover:-translate-y-1 border border-secondary-700"
              >
                <ShareIcon className="h-5 w-5 mr-2" />
                Explore Knowledge Graph
              </Link>
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  )
} 