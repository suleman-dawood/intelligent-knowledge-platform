'use client'

import { motion } from 'framer-motion'
import Link from 'next/link'
import { 
  CheckIcon,
  ArrowLeftIcon,
  SparklesIcon
} from '@heroicons/react/24/outline'

export default function PricingPage() {
  const plans = [
    {
      name: 'Free',
      price: '$0',
      period: 'forever',
      description: 'Perfect for getting started with basic document analysis',
      features: [
        'Up to 10 documents per month',
        'Basic AI analysis',
        'Simple knowledge graphs',
        'Email support',
        'Community access'
      ],
      cta: 'Get Started',
      href: '/signup',
      popular: false
    },
    {
      name: 'Pro',
      price: '$19',
      period: 'per month',
      description: 'Ideal for students and individual researchers',
      features: [
        'Unlimited documents',
        'Advanced AI analysis',
        'Interactive knowledge graphs',
        'Priority support',
        'Export capabilities',
        'Custom insights',
        'Collaboration tools'
      ],
      cta: 'Start Free Trial',
      href: '/signup?plan=pro',
      popular: true
    },
    {
      name: 'Team',
      price: '$49',
      period: 'per month',
      description: 'Best for teams and educational institutions',
      features: [
        'Everything in Pro',
        'Team collaboration',
        'Admin dashboard',
        'Bulk upload',
        'Custom integrations',
        'Dedicated support',
        'Advanced analytics',
        'White-label options'
      ],
      cta: 'Contact Sales',
      href: '/contact',
      popular: false
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
            Simple, Transparent Pricing
          </h1>
          <p className="text-xl text-secondary-600 max-w-3xl mx-auto leading-relaxed">
            Choose the plan that's right for you. All plans include our core AI-powered features with different usage limits and support levels.
          </p>
        </motion.div>

        {/* Pricing Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-16">
          {plans.map((plan, index) => (
            <motion.div
              key={plan.name}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className={`relative bg-white rounded-2xl shadow-sm border-2 transition-all duration-300 hover:shadow-lg ${
                plan.popular ? 'border-primary-600' : 'border-secondary-200'
              }`}
            >
              {plan.popular && (
                <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                  <div className="bg-primary-600 text-white px-4 py-1 rounded-full text-sm font-medium flex items-center">
                    <SparklesIcon className="h-4 w-4 mr-1" />
                    Most Popular
                  </div>
                </div>
              )}
              
              <div className="p-8">
                <h3 className="text-2xl font-bold text-secondary-900 mb-2">{plan.name}</h3>
                <p className="text-secondary-600 mb-6">{plan.description}</p>
                
                <div className="mb-6">
                  <span className="text-4xl font-bold text-secondary-900">{plan.price}</span>
                  <span className="text-secondary-600 ml-2">/{plan.period}</span>
                </div>
                
                <ul className="space-y-3 mb-8">
                  {plan.features.map((feature, featureIndex) => (
                    <li key={featureIndex} className="flex items-center">
                      <CheckIcon className="h-5 w-5 text-primary-600 mr-3 flex-shrink-0" />
                      <span className="text-secondary-700">{feature}</span>
                    </li>
                  ))}
                </ul>
                
                <Link
                  href={plan.href}
                  className={`block w-full text-center py-3 px-6 rounded-xl font-semibold transition-colors ${
                    plan.popular
                      ? 'bg-primary-600 text-white hover:bg-primary-700'
                      : 'bg-secondary-100 text-secondary-900 hover:bg-secondary-200'
                  }`}
                >
                  {plan.cta}
                </Link>
              </div>
            </motion.div>
          ))}
        </div>

        {/* FAQ Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="text-center"
        >
          <h2 className="text-3xl font-bold text-secondary-900 mb-8">
            Frequently Asked Questions
          </h2>
          <div className="max-w-3xl mx-auto space-y-6">
            <div className="bg-white rounded-xl p-6 text-left">
              <h3 className="font-semibold text-secondary-900 mb-2">Can I change plans anytime?</h3>
              <p className="text-secondary-600">Yes, you can upgrade or downgrade your plan at any time. Changes take effect immediately.</p>
            </div>
            <div className="bg-white rounded-xl p-6 text-left">
              <h3 className="font-semibold text-secondary-900 mb-2">Is there a free trial?</h3>
              <p className="text-secondary-600">Yes, all paid plans come with a 14-day free trial. No credit card required.</p>
            </div>
            <div className="bg-white rounded-xl p-6 text-left">
              <h3 className="font-semibold text-secondary-900 mb-2">What payment methods do you accept?</h3>
              <p className="text-secondary-600">We accept all major credit cards, PayPal, and bank transfers for annual plans.</p>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  )
} 