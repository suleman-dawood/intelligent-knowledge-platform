'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  UserCircleIcon,
  EnvelopeIcon,
  PhoneIcon,
  MapPinIcon,
  CameraIcon,
  PencilIcon,
  CheckIcon,
  XMarkIcon
} from '@heroicons/react/24/outline'

interface User {
  id: string
  name: string
  email: string
  phone?: string
  location?: string
  bio?: string
  avatar?: string
  joinDate: string
}

export default function ProfilePage() {
  const [user, setUser] = useState<User | null>(null)
  const [isEditing, setIsEditing] = useState(false)
  const [editForm, setEditForm] = useState<Partial<User>>({})
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Simulate loading user data
    setTimeout(() => {
      const userData = localStorage.getItem('user')
      if (userData) {
        const parsedUser = JSON.parse(userData)
        const fullUser: User = {
          id: '1',
          name: parsedUser.name || 'John Doe',
          email: parsedUser.email || 'john@example.com',
          phone: '+1 (555) 123-4567',
          location: 'San Francisco, CA',
          bio: 'Passionate learner and knowledge seeker. I love exploring new concepts and connecting ideas through AI-powered tools.',
          joinDate: '2024-01-15'
        }
        setUser(fullUser)
        setEditForm(fullUser)
      } else {
        // Default user for demo
        const defaultUser: User = {
          id: '1',
          name: 'John Doe',
          email: 'john@example.com',
          phone: '+1 (555) 123-4567',
          location: 'San Francisco, CA',
          bio: 'Passionate learner and knowledge seeker. I love exploring new concepts and connecting ideas through AI-powered tools.',
          joinDate: '2024-01-15'
        }
        setUser(defaultUser)
        setEditForm(defaultUser)
      }
      setLoading(false)
    }, 1000)
  }, [])

  const handleEdit = () => {
    setIsEditing(true)
  }

  const handleSave = () => {
    if (user && editForm) {
      const updatedUser = { ...user, ...editForm }
      setUser(updatedUser)
      localStorage.setItem('user', JSON.stringify(updatedUser))
      setIsEditing(false)
    }
  }

  const handleCancel = () => {
    setEditForm(user || {})
    setIsEditing(false)
  }

  const handleInputChange = (field: keyof User, value: string) => {
    setEditForm(prev => ({ ...prev, [field]: value }))
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-secondary-50 flex items-center justify-center">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
          className="w-8 h-8 border-2 border-primary-600 border-t-transparent rounded-full"
        />
      </div>
    )
  }

  if (!user) {
    return (
      <div className="min-h-screen bg-secondary-50 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-secondary-900 mb-4">Profile Not Found</h1>
          <p className="text-secondary-600">Please log in to view your profile.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-secondary-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="text-3xl font-bold text-secondary-900 mb-2">Profile</h1>
          <p className="text-secondary-600">Manage your account settings and preferences</p>
        </motion.div>

        {/* Profile Card */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white rounded-2xl shadow-sm border border-secondary-200 overflow-hidden"
        >
          {/* Header Section */}
          <div className="bg-gradient-to-r from-primary-600 to-primary-700 px-6 py-8">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="relative">
                  <div className="w-20 h-20 bg-white rounded-full flex items-center justify-center">
                    {user.avatar ? (
                      <img src={user.avatar} alt={user.name} className="w-20 h-20 rounded-full object-cover" />
                    ) : (
                      <UserCircleIcon className="w-16 h-16 text-secondary-400" />
                    )}
                  </div>
                  <button className="absolute -bottom-1 -right-1 w-6 h-6 bg-primary-600 rounded-full flex items-center justify-center text-white hover:bg-primary-700 transition-colors">
                    <CameraIcon className="w-3 h-3" />
                  </button>
                </div>
                <div className="text-white">
                  <h2 className="text-2xl font-bold">{user.name}</h2>
                  <p className="text-primary-100">{user.email}</p>
                  <p className="text-primary-200 text-sm">Member since {new Date(user.joinDate).toLocaleDateString()}</p>
                </div>
              </div>
              <div className="flex space-x-2">
                {isEditing ? (
                  <>
                    <button
                      onClick={handleSave}
                      className="flex items-center space-x-2 px-4 py-2 bg-white text-primary-600 rounded-lg hover:bg-primary-50 transition-colors"
                    >
                      <CheckIcon className="w-4 h-4" />
                      <span>Save</span>
                    </button>
                    <button
                      onClick={handleCancel}
                      className="flex items-center space-x-2 px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-400 transition-colors"
                    >
                      <XMarkIcon className="w-4 h-4" />
                      <span>Cancel</span>
                    </button>
                  </>
                ) : (
                  <button
                    onClick={handleEdit}
                    className="flex items-center space-x-2 px-4 py-2 bg-white text-primary-600 rounded-lg hover:bg-primary-50 transition-colors"
                  >
                    <PencilIcon className="w-4 h-4" />
                    <span>Edit Profile</span>
                  </button>
                )}
              </div>
            </div>
          </div>

          {/* Profile Details */}
          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Basic Information */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-secondary-900 mb-4">Basic Information</h3>
                
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-2">Full Name</label>
                  {isEditing ? (
                    <input
                      type="text"
                      value={editForm.name || ''}
                      onChange={(e) => handleInputChange('name', e.target.value)}
                      className="w-full px-3 py-2 border border-secondary-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    />
                  ) : (
                    <div className="flex items-center space-x-2 text-secondary-900">
                      <UserCircleIcon className="w-4 h-4 text-secondary-400" />
                      <span>{user.name}</span>
                    </div>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-2">Email Address</label>
                  {isEditing ? (
                    <input
                      type="email"
                      value={editForm.email || ''}
                      onChange={(e) => handleInputChange('email', e.target.value)}
                      className="w-full px-3 py-2 border border-secondary-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    />
                  ) : (
                    <div className="flex items-center space-x-2 text-secondary-900">
                      <EnvelopeIcon className="w-4 h-4 text-secondary-400" />
                      <span>{user.email}</span>
                    </div>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-2">Phone Number</label>
                  {isEditing ? (
                    <input
                      type="tel"
                      value={editForm.phone || ''}
                      onChange={(e) => handleInputChange('phone', e.target.value)}
                      className="w-full px-3 py-2 border border-secondary-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    />
                  ) : (
                    <div className="flex items-center space-x-2 text-secondary-900">
                      <PhoneIcon className="w-4 h-4 text-secondary-400" />
                      <span>{user.phone || 'Not provided'}</span>
                    </div>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-2">Location</label>
                  {isEditing ? (
                    <input
                      type="text"
                      value={editForm.location || ''}
                      onChange={(e) => handleInputChange('location', e.target.value)}
                      className="w-full px-3 py-2 border border-secondary-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    />
                  ) : (
                    <div className="flex items-center space-x-2 text-secondary-900">
                      <MapPinIcon className="w-4 h-4 text-secondary-400" />
                      <span>{user.location || 'Not provided'}</span>
                    </div>
                  )}
                </div>
              </div>

              {/* Bio Section */}
              <div>
                <h3 className="text-lg font-semibold text-secondary-900 mb-4">About</h3>
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-2">Bio</label>
                  {isEditing ? (
                    <textarea
                      value={editForm.bio || ''}
                      onChange={(e) => handleInputChange('bio', e.target.value)}
                      rows={6}
                      className="w-full px-3 py-2 border border-secondary-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none"
                      placeholder="Tell us about yourself..."
                    />
                  ) : (
                    <p className="text-secondary-900 leading-relaxed">
                      {user.bio || 'No bio provided.'}
                    </p>
                  )}
                </div>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Account Statistics */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6"
        >
          <div className="bg-white rounded-xl p-6 border border-secondary-200">
            <h4 className="text-sm font-medium text-secondary-600 mb-2">Documents Analyzed</h4>
            <p className="text-2xl font-bold text-secondary-900">24</p>
          </div>
          <div className="bg-white rounded-xl p-6 border border-secondary-200">
            <h4 className="text-sm font-medium text-secondary-600 mb-2">Knowledge Connections</h4>
            <p className="text-2xl font-bold text-secondary-900">156</p>
          </div>
          <div className="bg-white rounded-xl p-6 border border-secondary-200">
            <h4 className="text-sm font-medium text-secondary-600 mb-2">Learning Hours</h4>
            <p className="text-2xl font-bold text-secondary-900">48</p>
          </div>
        </motion.div>
      </div>
    </div>
  )
} 