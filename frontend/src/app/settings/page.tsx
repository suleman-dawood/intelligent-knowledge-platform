'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import {
  UserCircleIcon,
  BellIcon,
  ShieldCheckIcon,
  PaintBrushIcon,
  CogIcon,
  KeyIcon,
  CircleStackIcon,
  CloudIcon,
  DevicePhoneMobileIcon,
  GlobeAltIcon,
  EyeIcon,
  EyeSlashIcon,
  CheckIcon,
  XMarkIcon,
} from '@heroicons/react/24/outline';

interface SettingsSection {
  id: string;
  title: string;
  description: string;
  icon: React.ReactNode;
}

const SettingsPage = () => {
  const [activeSection, setActiveSection] = useState('profile');
  const [showPassword, setShowPassword] = useState(false);
  const [settings, setSettings] = useState({
    profile: {
      name: 'John Doe',
      email: 'john.doe@example.com',
      bio: 'AI enthusiast and lifelong learner',
      avatar: '',
    },
    notifications: {
      emailNotifications: true,
      pushNotifications: false,
      weeklyDigest: true,
      newFeatures: true,
      securityAlerts: true,
    },
    privacy: {
      profileVisibility: 'public',
      dataSharing: false,
      analyticsTracking: true,
      cookiePreferences: 'essential',
    },
    appearance: {
      theme: 'light',
      language: 'en',
      fontSize: 'medium',
      compactMode: false,
    },
    security: {
      twoFactorAuth: false,
      sessionTimeout: '30',
      loginAlerts: true,
    },
    api: {
      apiKey: 'sk-1234567890abcdef...',
      rateLimit: '1000',
      webhookUrl: '',
    },
    storage: {
      autoBackup: true,
      retentionPeriod: '90',
      compressionEnabled: true,
    },
  });

  const sections: SettingsSection[] = [
    {
      id: 'profile',
      title: 'Profile',
      description: 'Manage your personal information',
      icon: <UserCircleIcon className="h-5 w-5" />,
    },
    {
      id: 'notifications',
      title: 'Notifications',
      description: 'Configure notification preferences',
      icon: <BellIcon className="h-5 w-5" />,
    },
    {
      id: 'privacy',
      title: 'Privacy',
      description: 'Control your privacy settings',
      icon: <ShieldCheckIcon className="h-5 w-5" />,
    },
    {
      id: 'appearance',
      title: 'Appearance',
      description: 'Customize the look and feel',
      icon: <PaintBrushIcon className="h-5 w-5" />,
    },
    {
      id: 'security',
      title: 'Security',
      description: 'Manage security and authentication',
      icon: <KeyIcon className="h-5 w-5" />,
    },
    {
      id: 'api',
      title: 'API Settings',
      description: 'Configure API access and keys',
      icon: <CogIcon className="h-5 w-5" />,
    },
    {
      id: 'storage',
      title: 'Storage',
      description: 'Manage data storage preferences',
      icon: <CircleStackIcon className="h-5 w-5" />,
    },
  ];

  const handleSettingChange = (section: string, key: string, value: any) => {
    setSettings(prev => ({
      ...prev,
      [section]: {
        ...prev[section as keyof typeof prev],
        [key]: value,
      },
    }));
  };

  const renderProfileSettings = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-secondary-900 mb-4">Profile Information</h3>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-secondary-700 mb-2">
              Full Name
            </label>
            <input
              type="text"
              value={settings.profile.name}
              onChange={(e) => handleSettingChange('profile', 'name', e.target.value)}
              className="w-full px-3 py-2 border border-secondary-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-secondary-700 mb-2">
              Email Address
            </label>
            <input
              type="email"
              value={settings.profile.email}
              onChange={(e) => handleSettingChange('profile', 'email', e.target.value)}
              className="w-full px-3 py-2 border border-secondary-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-secondary-700 mb-2">
              Bio
            </label>
            <textarea
              rows={3}
              value={settings.profile.bio}
              onChange={(e) => handleSettingChange('profile', 'bio', e.target.value)}
              className="w-full px-3 py-2 border border-secondary-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              placeholder="Tell us about yourself..."
            />
          </div>
        </div>
      </div>
      
      <div>
        <h3 className="text-lg font-semibold text-secondary-900 mb-4">Profile Picture</h3>
        <div className="flex items-center space-x-4">
          <div className="w-16 h-16 bg-secondary-200 rounded-full flex items-center justify-center">
            <UserCircleIcon className="h-12 w-12 text-secondary-400" />
          </div>
          <div>
            <button className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors">
              Upload Photo
            </button>
            <p className="text-sm text-secondary-600 mt-1">JPG, PNG up to 5MB</p>
          </div>
        </div>
      </div>
    </div>
  );

  const renderNotificationSettings = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-secondary-900 mb-4">Email Notifications</h3>
        <div className="space-y-4">
          {Object.entries(settings.notifications).map(([key, value]) => (
            <div key={key} className="flex items-center justify-between">
              <div>
                <p className="font-medium text-secondary-900 capitalize">
                  {key.replace(/([A-Z])/g, ' $1').trim()}
                </p>
                <p className="text-sm text-secondary-600">
                  {key === 'emailNotifications' && 'Receive email notifications for important updates'}
                  {key === 'pushNotifications' && 'Get push notifications on your devices'}
                  {key === 'weeklyDigest' && 'Weekly summary of your activity'}
                  {key === 'newFeatures' && 'Notifications about new features and updates'}
                  {key === 'securityAlerts' && 'Important security and account alerts'}
                </p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={value as boolean}
                  onChange={(e) => handleSettingChange('notifications', key, e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-secondary-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-secondary-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
              </label>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderPrivacySettings = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-secondary-900 mb-4">Privacy Controls</h3>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-secondary-700 mb-2">
              Profile Visibility
            </label>
            <select
              value={settings.privacy.profileVisibility}
              onChange={(e) => handleSettingChange('privacy', 'profileVisibility', e.target.value)}
              className="w-full px-3 py-2 border border-secondary-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            >
              <option value="public">Public</option>
              <option value="private">Private</option>
              <option value="friends">Friends Only</option>
            </select>
          </div>
          
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium text-secondary-900">Data Sharing</p>
              <p className="text-sm text-secondary-600">Allow sharing anonymized data for research</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={settings.privacy.dataSharing}
                onChange={(e) => handleSettingChange('privacy', 'dataSharing', e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-secondary-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-secondary-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
            </label>
          </div>

          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium text-secondary-900">Analytics Tracking</p>
              <p className="text-sm text-secondary-600">Help improve the platform with usage analytics</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={settings.privacy.analyticsTracking}
                onChange={(e) => handleSettingChange('privacy', 'analyticsTracking', e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-secondary-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-secondary-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
            </label>
          </div>
        </div>
      </div>
    </div>
  );

  const renderAppearanceSettings = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-secondary-900 mb-4">Display Preferences</h3>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-secondary-700 mb-2">
              Theme
            </label>
            <div className="flex space-x-3">
              {['light', 'dark', 'auto'].map((theme) => (
                <button
                  key={theme}
                  onClick={() => handleSettingChange('appearance', 'theme', theme)}
                  className={`px-4 py-2 rounded-lg border-2 transition-colors capitalize ${
                    settings.appearance.theme === theme
                      ? 'border-primary-500 bg-primary-50 text-primary-700'
                      : 'border-secondary-300 bg-white text-secondary-700 hover:border-secondary-400'
                  }`}
                >
                  {theme}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-secondary-700 mb-2">
              Language
            </label>
            <select
              value={settings.appearance.language}
              onChange={(e) => handleSettingChange('appearance', 'language', e.target.value)}
              className="w-full px-3 py-2 border border-secondary-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            >
              <option value="en">English</option>
              <option value="es">Spanish</option>
              <option value="fr">French</option>
              <option value="de">German</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-secondary-700 mb-2">
              Font Size
            </label>
            <div className="flex space-x-3">
              {['small', 'medium', 'large'].map((size) => (
                <button
                  key={size}
                  onClick={() => handleSettingChange('appearance', 'fontSize', size)}
                  className={`px-4 py-2 rounded-lg border-2 transition-colors capitalize ${
                    settings.appearance.fontSize === size
                      ? 'border-primary-500 bg-primary-50 text-primary-700'
                      : 'border-secondary-300 bg-white text-secondary-700 hover:border-secondary-400'
                  }`}
                >
                  {size}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderSecuritySettings = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-secondary-900 mb-4">Account Security</h3>
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium text-secondary-900">Two-Factor Authentication</p>
              <p className="text-sm text-secondary-600">Add an extra layer of security to your account</p>
            </div>
            <button
              onClick={() => handleSettingChange('security', 'twoFactorAuth', !settings.security.twoFactorAuth)}
              className={`px-4 py-2 rounded-lg transition-colors ${
                settings.security.twoFactorAuth
                  ? 'bg-success-100 text-success-700 hover:bg-success-200'
                  : 'bg-secondary-100 text-secondary-700 hover:bg-secondary-200'
              }`}
            >
              {settings.security.twoFactorAuth ? 'Enabled' : 'Enable'}
            </button>
          </div>

          <div>
            <label className="block text-sm font-medium text-secondary-700 mb-2">
              Session Timeout (minutes)
            </label>
            <select
              value={settings.security.sessionTimeout}
              onChange={(e) => handleSettingChange('security', 'sessionTimeout', e.target.value)}
              className="w-full px-3 py-2 border border-secondary-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            >
              <option value="15">15 minutes</option>
              <option value="30">30 minutes</option>
              <option value="60">1 hour</option>
              <option value="120">2 hours</option>
              <option value="never">Never</option>
            </select>
          </div>

          <div>
            <button className="w-full px-4 py-2 bg-warning-100 text-warning-700 rounded-lg hover:bg-warning-200 transition-colors">
              Change Password
            </button>
          </div>
        </div>
      </div>
    </div>
  );

  const renderApiSettings = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-secondary-900 mb-4">API Configuration</h3>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-secondary-700 mb-2">
              API Key
            </label>
            <div className="flex space-x-2">
              <div className="flex-1 relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={settings.api.apiKey}
                  readOnly
                  className="w-full px-3 py-2 pr-10 border border-secondary-300 rounded-lg bg-secondary-50 text-secondary-600"
                />
                <button
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center"
                >
                  {showPassword ? (
                    <EyeSlashIcon className="h-4 w-4 text-secondary-400" />
                  ) : (
                    <EyeIcon className="h-4 w-4 text-secondary-400" />
                  )}
                </button>
              </div>
              <button className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors">
                Regenerate
              </button>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-secondary-700 mb-2">
              Rate Limit (requests/hour)
            </label>
            <input
              type="number"
              value={settings.api.rateLimit}
              onChange={(e) => handleSettingChange('api', 'rateLimit', e.target.value)}
              className="w-full px-3 py-2 border border-secondary-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-secondary-700 mb-2">
              Webhook URL
            </label>
            <input
              type="url"
              value={settings.api.webhookUrl}
              onChange={(e) => handleSettingChange('api', 'webhookUrl', e.target.value)}
              placeholder="https://your-webhook-url.com"
              className="w-full px-3 py-2 border border-secondary-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>
        </div>
      </div>
    </div>
  );

  const renderStorageSettings = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-secondary-900 mb-4">Storage Management</h3>
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium text-secondary-900">Auto Backup</p>
              <p className="text-sm text-secondary-600">Automatically backup your data daily</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={settings.storage.autoBackup}
                onChange={(e) => handleSettingChange('storage', 'autoBackup', e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-secondary-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-secondary-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
            </label>
          </div>

          <div>
            <label className="block text-sm font-medium text-secondary-700 mb-2">
              Data Retention Period (days)
            </label>
            <select
              value={settings.storage.retentionPeriod}
              onChange={(e) => handleSettingChange('storage', 'retentionPeriod', e.target.value)}
              className="w-full px-3 py-2 border border-secondary-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            >
              <option value="30">30 days</option>
              <option value="90">90 days</option>
              <option value="180">6 months</option>
              <option value="365">1 year</option>
              <option value="forever">Forever</option>
            </select>
          </div>

          <div className="bg-secondary-50 rounded-lg p-4">
            <h4 className="font-medium text-secondary-900 mb-2">Storage Usage</h4>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-secondary-600">Documents</span>
                <span className="font-medium text-secondary-900">2.3 GB</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-secondary-600">Images</span>
                <span className="font-medium text-secondary-900">856 MB</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-secondary-600">Other</span>
                <span className="font-medium text-secondary-900">124 MB</span>
              </div>
              <div className="border-t border-secondary-200 pt-2 mt-2">
                <div className="flex justify-between font-medium">
                  <span className="text-secondary-900">Total</span>
                  <span className="text-secondary-900">3.28 GB / 10 GB</span>
                </div>
                <div className="w-full bg-secondary-200 rounded-full h-2 mt-2">
                  <div className="bg-primary-600 h-2 rounded-full" style={{ width: '32.8%' }}></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderContent = () => {
    switch (activeSection) {
      case 'profile': return renderProfileSettings();
      case 'notifications': return renderNotificationSettings();
      case 'privacy': return renderPrivacySettings();
      case 'appearance': return renderAppearanceSettings();
      case 'security': return renderSecuritySettings();
      case 'api': return renderApiSettings();
      case 'storage': return renderStorageSettings();
      default: return renderProfileSettings();
    }
  };

  return (
    <div className="min-h-screen bg-secondary-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-secondary-900 mb-2">Settings</h1>
          <p className="text-secondary-600">Manage your account preferences and configuration</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Sidebar */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-2xl shadow-sm border border-secondary-200 p-6">
              <nav className="space-y-2">
                {sections.map((section) => (
                  <button
                    key={section.id}
                    onClick={() => setActiveSection(section.id)}
                    className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-left transition-colors ${
                      activeSection === section.id
                        ? 'bg-primary-100 text-primary-700 border border-primary-200'
                        : 'text-secondary-700 hover:bg-secondary-50'
                    }`}
                  >
                    {section.icon}
                    <div>
                      <p className="font-medium">{section.title}</p>
                      <p className="text-xs text-secondary-500">{section.description}</p>
                    </div>
                  </button>
                ))}
              </nav>
            </div>
          </div>

          {/* Main Content */}
          <div className="lg:col-span-3">
            <div className="bg-white rounded-2xl shadow-sm border border-secondary-200 p-6">
              <motion.div
                key={activeSection}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3 }}
              >
                {renderContent()}
              </motion.div>

              {/* Save Button */}
              <div className="mt-8 pt-6 border-t border-secondary-200">
                <div className="flex items-center justify-end space-x-3">
                  <button className="px-4 py-2 text-secondary-600 hover:text-secondary-900 transition-colors">
                    Cancel
                  </button>
                  <button className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors flex items-center space-x-2">
                    <CheckIcon className="h-4 w-4" />
                    <span>Save Changes</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SettingsPage; 