'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import {
  HomeIcon,
  MagnifyingGlassIcon,
  CogIcon,
  UserCircleIcon,
  DocumentTextIcon,
  ShareIcon,
  Bars3Icon,
  XMarkIcon,
  ArrowRightOnRectangleIcon,
  UserPlusIcon,
} from '@heroicons/react/24/outline';
import SystemStatus from '../ui/SystemStatus';

interface User {
  email: string;
  name: string;
  role: string;
}

const Header: React.FC = () => {
  const pathname = usePathname();
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);
  
  useEffect(() => {
    // Check for user session
    const userData = localStorage.getItem('user');
    if (userData) {
      setUser(JSON.parse(userData));
    }
  }, []);

  useEffect(() => {
    // Close user menu when clicking outside
    const handleClickOutside = (event: MouseEvent) => {
      if (showUserMenu && !(event.target as Element).closest('.user-menu-container')) {
        setShowUserMenu(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [showUserMenu]);

  const handleLogout = () => {
    localStorage.removeItem('user');
    setUser(null);
    router.push('/');
  };
  
  const navigation = [
    { name: 'Dashboard', href: '/', icon: HomeIcon },
    { name: 'Search', href: '/search', icon: MagnifyingGlassIcon },
    { name: 'Content', href: '/content', icon: DocumentTextIcon },
    { name: 'Knowledge Graph', href: '/knowledge-graph', icon: ShareIcon },
    { name: 'Settings', href: '/settings', icon: CogIcon },
  ];

  const authLinks = user ? [
    {
      name: 'Profile',
      href: '/profile',
      icon: UserCircleIcon,
      action: () => router.push('/profile'),
    },
    {
      name: 'Logout',
      href: '#',
      icon: ArrowRightOnRectangleIcon,
      action: handleLogout,
    },
  ] : [
    {
      name: 'Sign In',
      href: '/login',
      icon: ArrowRightOnRectangleIcon,
      action: () => router.push('/login'),
    },
    {
      name: 'Sign Up',
      href: '/signup',
      icon: UserPlusIcon,
      action: () => router.push('/signup'),
    },
  ];
  
  return (
    <header className="bg-white border-b border-secondary-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="flex items-center">
            <Link href="/" className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-primary-600 rounded-xl flex items-center justify-center">
                <span className="text-white font-bold text-lg">HW</span>
              </div>
              <span className="text-xl font-bold text-secondary-900">
                Homework Analyzer
              </span>
            </Link>
          </div>
          
          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-1">
            {navigation.map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.href || 
                (item.href !== '/' && pathname.startsWith(item.href));
              
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                    isActive
                      ? 'bg-primary-100 text-primary-700 shadow-sm'
                      : 'text-secondary-600 hover:text-secondary-900 hover:bg-secondary-50'
                  }`}
                >
                  <Icon className="h-4 w-4" />
                  <span>{item.name}</span>
                </Link>
              );
            })}
          </nav>
          
          {/* Right Side */}
          <div className="flex items-center space-x-4">
            {/* System Status */}
            <SystemStatus compact className="hidden lg:flex" />
            
            {/* User Menu / Auth Links */}
            <div className="hidden md:flex items-center space-x-2">
              {user ? (
                <div className="relative user-menu-container">
                  <button 
                    onClick={() => setShowUserMenu(!showUserMenu)}
                    className="flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium text-secondary-700 hover:text-secondary-900 hover:bg-secondary-50 transition-colors"
                  >
                    <UserCircleIcon className="h-5 w-5" />
                    <span>{user.name}</span>
                  </button>
                  
                  {/* Dropdown Menu */}
                  <AnimatePresence>
                    {showUserMenu && (
                      <motion.div
                        initial={{ opacity: 0, scale: 0.95, y: -10 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.95, y: -10 }}
                        transition={{ duration: 0.1 }}
                        className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-secondary-200 z-50"
                      >
                        <div className="py-2">
                          <div className="px-4 py-2 border-b border-secondary-200">
                            <p className="text-sm font-medium text-secondary-900">{user.name}</p>
                            <p className="text-xs text-secondary-600">{user.email}</p>
                          </div>
                          {authLinks.map((link) => {
                            const Icon = link.icon;
                            return (
                              <button
                                key={link.name}
                                onClick={() => {
                                  link.action();
                                  setShowUserMenu(false);
                                }}
                                className="w-full flex items-center space-x-2 px-4 py-2 text-sm text-secondary-700 hover:bg-secondary-50 transition-colors"
                              >
                                <Icon className="h-4 w-4" />
                                <span>{link.name}</span>
                              </button>
                            );
                          })}
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              ) : (
                <div className="flex items-center space-x-2">
                  <Link
                    href="/login"
                    className="px-4 py-2 text-sm font-medium text-secondary-600 hover:text-secondary-900 transition-colors"
                  >
                    Sign In
                  </Link>
                  <Link
                    href="/signup"
                    className="px-4 py-2 bg-primary-600 text-white text-sm font-medium rounded-lg hover:bg-primary-700 transition-colors"
                  >
                    Sign Up
                  </Link>
                </div>
              )}
            </div>
            
            {/* Mobile menu button */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden p-2 rounded-lg text-secondary-600 hover:text-secondary-900 hover:bg-secondary-50 transition-colors"
            >
              {mobileMenuOpen ? (
                <XMarkIcon className="h-6 w-6" />
              ) : (
                <Bars3Icon className="h-6 w-6" />
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Menu */}
      <AnimatePresence>
        {mobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="md:hidden bg-white border-t border-secondary-200"
          >
            <div className="px-4 py-4 space-y-2">
              {navigation.map((item) => {
                const Icon = item.icon;
                const isActive = pathname === item.href || 
                  (item.href !== '/' && pathname.startsWith(item.href));
                
                return (
                  <Link
                    key={item.name}
                    href={item.href}
                    onClick={() => setMobileMenuOpen(false)}
                    className={`flex items-center space-x-3 px-4 py-3 rounded-lg text-sm font-medium transition-colors ${
                      isActive
                        ? 'bg-primary-100 text-primary-700'
                        : 'text-secondary-600 hover:text-secondary-900 hover:bg-secondary-50'
                    }`}
                  >
                    <Icon className="h-5 w-5" />
                    <span>{item.name}</span>
                  </Link>
                );
              })}
              
              {/* Mobile Auth */}
              <div className="pt-4 border-t border-secondary-200">
                {user ? (
                  <div className="space-y-2">
                    <div className="px-4 py-2">
                      <p className="text-sm font-medium text-secondary-900">{user.name}</p>
                      <p className="text-xs text-secondary-600">{user.email}</p>
                    </div>
                    {authLinks.map((link) => {
                      const Icon = link.icon;
                      return (
                        <button
                          key={link.name}
                          onClick={() => {
                            link.action();
                            setMobileMenuOpen(false);
                          }}
                          className="w-full flex items-center space-x-3 px-4 py-3 text-sm text-secondary-700 hover:bg-secondary-50 transition-colors rounded-lg"
                        >
                          <Icon className="h-5 w-5" />
                          <span>{link.name}</span>
                        </button>
                      );
                    })}
                  </div>
                ) : (
                  <div className="space-y-2">
                    <Link
                      href="/login"
                      onClick={() => setMobileMenuOpen(false)}
                      className="flex items-center space-x-3 px-4 py-3 text-sm font-medium text-secondary-600 hover:text-secondary-900 hover:bg-secondary-50 transition-colors rounded-lg"
                    >
                      <ArrowRightOnRectangleIcon className="h-5 w-5" />
                      <span>Sign In</span>
                    </Link>
                    <Link
                      href="/signup"
                      onClick={() => setMobileMenuOpen(false)}
                      className="flex items-center space-x-3 px-4 py-3 bg-primary-600 text-white text-sm font-medium rounded-lg hover:bg-primary-700 transition-colors"
                    >
                      <UserPlusIcon className="h-5 w-5" />
                      <span>Sign Up</span>
                    </Link>
                  </div>
                )}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  );
};

export default Header; 