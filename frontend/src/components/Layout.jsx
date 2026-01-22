import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { Video, Users, Home, Sparkles } from 'lucide-react'

export default function Layout({ children }) {
  const location = useLocation()
  
  const isActive = (path) => {
    return location.pathname === path
  }
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-purple-50/30 to-cyan-50/30 flex flex-col">
      {/* Modern Gradient Navbar */}
      <nav className="sticky top-0 z-50 bg-white/80 backdrop-blur-lg shadow-lg border-b border-purple-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center gap-8">
              {/* Logo */}
              <Link to="/" className="flex items-center gap-2 group">
                <div className="relative">
                  <Video className="h-8 w-8 text-purple-600 group-hover:text-cyan-600 transition-colors" />
                  <div className="absolute inset-0 bg-purple-400 blur-lg opacity-0 group-hover:opacity-30 transition-opacity"></div>
                </div>
                <span className="text-2xl font-bold">
                  <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-cyan-600">
                    VisumeAI
                  </span>
                </span>
              </Link>
              
              {/* Navigation Links */}
              <div className="hidden sm:flex sm:gap-2">
                <Link
                  to="/"
                  className={`inline-flex items-center px-4 py-2 text-sm font-semibold rounded-lg transition-all ${
                    isActive('/') 
                      ? 'text-white bg-gradient-to-r from-purple-600 to-cyan-600 shadow-glow' 
                      : 'text-gray-700 hover:text-purple-600 hover:bg-purple-50'
                  }`}
                >
                  <Home className="h-4 w-4 mr-2" />
                  Home
                </Link>
                
                <Link
                  to="/candidate"
                  className={`inline-flex items-center px-4 py-2 text-sm font-semibold rounded-lg transition-all ${
                    isActive('/candidate') 
                      ? 'text-white bg-gradient-to-r from-purple-600 to-cyan-600 shadow-glow' 
                      : 'text-gray-700 hover:text-purple-600 hover:bg-purple-50'
                  }`}
                >
                  <Video className="h-4 w-4 mr-2" />
                  Candidate
                </Link>
                
                <Link
                  to="/recruiter"
                  className={`inline-flex items-center px-4 py-2 text-sm font-semibold rounded-lg transition-all ${
                    isActive('/recruiter') 
                      ? 'text-white bg-gradient-to-r from-purple-600 to-cyan-600 shadow-glow' 
                      : 'text-gray-700 hover:text-purple-600 hover:bg-purple-50'
                  }`}
                >
                  <Users className="h-4 w-4 mr-2" />
                  Recruiter
                </Link>
              </div>
            </div>

            {/* AI Badge */}
            <div className="hidden md:flex items-center">
              <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-gradient-to-r from-purple-100 to-cyan-100 text-purple-700 text-xs font-semibold">
                <Sparkles className="h-3 w-3" />
                AI-Powered
              </div>
            </div>
          </div>
        </div>
      </nav>
      
      {/* Main Content */}
      <main className="flex-1">
        {children}
      </main>
      
      {/* Modern Footer */}
      <footer className="relative bg-gradient-to-r from-purple-900 via-indigo-900 to-cyan-900 text-white mt-auto">
        <div className="absolute inset-0 bg-black opacity-30"></div>
        <div className="relative max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <div className="inline-flex items-center gap-2 mb-3">
              <Video className="h-6 w-6" />
              <span className="text-xl font-bold">VisumeAI</span>
            </div>
            <p className="text-sm text-purple-200 mb-2">
              AI-Powered Video Resume Analysis Platform
            </p>
            <p className="text-xs text-purple-300">
              © 2025 VisumeAI. Transforming recruitment with intelligent technology.
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}
