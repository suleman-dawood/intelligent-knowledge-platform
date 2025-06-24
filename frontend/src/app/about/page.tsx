'use client';

import React from 'react';
import { motion } from 'framer-motion';
import {
  AcademicCapIcon,
  SparklesIcon,
  UserGroupIcon,
  LightBulbIcon,
} from '@heroicons/react/24/outline';

export default function AboutPage() {
  const features = [
    {
      icon: SparklesIcon,
      title: 'AI-Powered Analysis',
      description: 'Our advanced AI algorithms analyze your documents to extract key concepts, generate summaries, and provide intelligent insights.',
    },
    {
      icon: AcademicCapIcon,
      title: 'Educational Focus',
      description: 'Built specifically for students and educators to enhance learning outcomes and accelerate knowledge acquisition.',
    },
    {
      icon: UserGroupIcon,
      title: 'Collaborative Learning',
      description: 'Share insights with classmates, create study groups, and learn together in a collaborative environment.',
    },
    {
      icon: LightBulbIcon,
      title: 'Smart Insights',
      description: 'Get personalized recommendations and discover new learning paths based on your uploaded content.',
    },
  ];

  return (
    <div className="min-h-screen bg-secondary-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Hero Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-center mb-16"
        >
          <h1 className="text-4xl md:text-6xl font-bold text-secondary-900 mb-6">
            About <span className="text-primary-600">Homework Analyzer</span>
          </h1>
          <p className="max-w-3xl mx-auto text-xl text-secondary-600 leading-relaxed">
            We're on a mission to transform education through AI-powered document analysis 
            and intelligent knowledge extraction, making learning more efficient and effective.
          </p>
        </motion.div>

        {/* Mission Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
          className="bg-white rounded-2xl p-8 mb-16 shadow-sm border border-secondary-200"
        >
          <h2 className="text-3xl font-bold text-secondary-900 mb-6 text-center">Our Mission</h2>
          <p className="text-lg text-secondary-700 leading-relaxed text-center max-w-4xl mx-auto">
            At Homework Analyzer, we believe that technology should enhance learning, not complicate it. 
            Our platform empowers students and educators with AI-driven tools that extract meaningful 
            insights from documents, create knowledge maps, and accelerate the learning process. 
            We're committed to making education more accessible, efficient, and engaging for everyone.
          </p>
        </motion.div>

        {/* Features Grid */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
          className="mb-16"
        >
          <h2 className="text-3xl font-bold text-secondary-900 mb-12 text-center">
            What Makes Us Different
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {features.map((feature, index) => {
              const Icon = feature.icon;
              return (
                <motion.div
                  key={feature.title}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: index * 0.1 }}
                  viewport={{ once: true }}
                  className="bg-white rounded-2xl p-6 shadow-sm border border-secondary-200"
                >
                  <div className="flex items-start space-x-4">
                    <div className="p-3 bg-primary-100 rounded-xl">
                      <Icon className="h-6 w-6 text-primary-600" />
                    </div>
                    <div>
                      <h3 className="text-xl font-semibold text-secondary-900 mb-2">
                        {feature.title}
                      </h3>
                      <p className="text-secondary-600 leading-relaxed">
                        {feature.description}
                      </p>
                    </div>
                  </div>
                </motion.div>
              );
            })}
          </div>
        </motion.div>

        {/* Team Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
          className="bg-white rounded-2xl p-8 shadow-sm border border-secondary-200"
        >
          <h2 className="text-3xl font-bold text-secondary-900 mb-6 text-center">Our Team</h2>
          <p className="text-lg text-secondary-700 leading-relaxed text-center max-w-4xl mx-auto mb-8">
            We're a passionate team of educators, engineers, and AI researchers dedicated to 
            revolutionizing the way people learn and process information.
          </p>
          <div className="text-center">
            <p className="text-secondary-600">
              Interested in joining our mission? 
              <a href="/careers" className="text-primary-600 hover:text-primary-700 font-medium ml-1">
                Check out our careers page
              </a>
            </p>
          </div>
        </motion.div>
      </div>
    </div>
  );
} 