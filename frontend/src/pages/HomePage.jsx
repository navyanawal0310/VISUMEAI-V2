import React from 'react'
import { Link } from 'react-router-dom'
import { Video, FileText, Target, BarChart, CheckCircle, Zap, Sparkles, TrendingUp } from 'lucide-react'

export default function HomePage() {
  const features = [
    {
      icon: <Video className="h-6 w-6" />,
      title: 'Video Analysis',
      description: 'AI-powered analysis of body language, eye contact, and presentation skills using MediaPipe.',
      gradient: 'from-purple-500 to-pink-500'
    },
    {
      icon: <FileText className="h-6 w-6" />,
      title: 'Resume Parsing',
      description: 'Intelligent extraction of skills, experience, and qualifications from PDF/DOCX resumes.',
      gradient: 'from-cyan-500 to-blue-500'
    },
    {
      icon: <Target className="h-6 w-6" />,
      title: 'Role Matching',
      description: 'Semantic matching against job descriptions using advanced NLP and embeddings.',
      gradient: 'from-green-500 to-teal-500'
    },
    {
      icon: <BarChart className="h-6 w-6" />,
      title: 'Comprehensive Scoring',
      description: 'Multi-dimensional evaluation covering technical skills, soft skills, and role fit.',
      gradient: 'from-orange-500 to-red-500'
    },
    {
      icon: <CheckCircle className="h-6 w-6" />,
      title: 'AI Feedback',
      description: 'Personalized feedback reports generated using LLMs with actionable recommendations.',
      gradient: 'from-indigo-500 to-purple-500'
    },
    {
      icon: <Zap className="h-6 w-6" />,
      title: 'Fast Processing',
      description: 'Automated pipeline processes videos and resumes in minutes, not hours.',
      gradient: 'from-yellow-500 to-orange-500'
    }
  ]
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-purple-50 to-cyan-50">
      {/* Animated Background */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 -left-4 w-72 h-72 bg-purple-300 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-float"></div>
        <div className="absolute top-0 -right-4 w-72 h-72 bg-cyan-300 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-float" style={{ animationDelay: '2s' }}></div>
        <div className="absolute -bottom-8 left-20 w-72 h-72 bg-pink-300 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-float" style={{ animationDelay: '4s' }}></div>
      </div>

      {/* Hero Section */}
      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center">
          <div className="inline-flex items-center gap-2 bg-gradient-to-r from-purple-600 to-cyan-600 text-white px-4 py-2 rounded-full text-sm font-semibold mb-6 shadow-glow">
            <Sparkles className="h-4 w-4" />
            AI-Powered Recruitment Platform
          </div>
          
          <h1 className="text-5xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-purple-600 via-pink-600 to-cyan-600 sm:text-6xl md:text-7xl mb-6 animate-gradient">
            Welcome to VisumeAI
          </h1>
          
          <p className="mt-6 max-w-2xl mx-auto text-xl text-gray-700 font-medium">
            Transform your hiring process with intelligent video resume analysis and AI-driven candidate evaluation.
          </p>
          
          <div className="mt-10 flex flex-col sm:flex-row justify-center gap-4">
            <Link
              to="/candidate"
              className="group relative inline-flex items-center justify-center px-8 py-4 text-lg font-semibold rounded-xl text-white bg-gradient-to-r from-purple-600 to-cyan-600 hover:from-purple-700 hover:to-cyan-700 shadow-glow hover:shadow-glow-lg transition-all duration-300 transform hover:scale-105"
            >
              <Video className="h-5 w-5 mr-2 group-hover:animate-pulse" />
              Submit Your Video Resume
              <TrendingUp className="h-4 w-4 ml-2 opacity-0 group-hover:opacity-100 transition-opacity" />
            </Link>
            
            <Link
              to="/recruiter"
              className="inline-flex items-center justify-center px-8 py-4 text-lg font-semibold rounded-xl text-purple-600 bg-white hover:bg-gray-50 border-2 border-purple-600 shadow-card hover:shadow-card-hover transition-all duration-300 transform hover:scale-105"
            >
              <BarChart className="h-5 w-5 mr-2" />
              Recruiter Dashboard
            </Link>
          </div>
        </div>
      </div>
      
      {/* Features Section */}
      <div className="relative py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-cyan-600 mb-4">
              Powerful Features
            </h2>
            <p className="mt-4 text-lg text-gray-600 max-w-2xl mx-auto">
              Powered by cutting-edge AI and computer vision technology to revolutionize your hiring process
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <div 
                key={index}
                className="group relative bg-white p-8 rounded-2xl border border-gray-200 shadow-card hover:shadow-card-hover transition-all duration-300 hover:-translate-y-2"
              >
                <div className={`inline-flex items-center justify-center w-14 h-14 rounded-xl bg-gradient-to-br ${feature.gradient} text-white mb-5 shadow-lg group-hover:scale-110 transition-transform`}>
                  {feature.icon}
                </div>
                <h3 className="text-xl font-bold text-gray-900 mb-3 group-hover:text-purple-600 transition-colors">
                  {feature.title}
                </h3>
                <p className="text-gray-600 leading-relaxed">
                  {feature.description}
                </p>
                <div className={`absolute top-0 left-0 w-full h-1 bg-gradient-to-r ${feature.gradient} rounded-t-2xl opacity-0 group-hover:opacity-100 transition-opacity`}></div>
              </div>
            ))}
          </div>
        </div>
      </div>
      
      {/* How It Works Section */}
      <div className="relative py-20 bg-gradient-to-br from-purple-50 via-cyan-50 to-pink-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-600 to-purple-600 mb-4">
              How It Works
            </h2>
            <p className="text-lg text-gray-600">Simple, fast, and intelligent</p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            {[
              { step: '1', title: 'Upload', desc: 'Submit video resume and/or text resume', gradient: 'from-purple-500 to-pink-500' },
              { step: '2', title: 'Analyze', desc: 'AI processes video, audio, and text', gradient: 'from-cyan-500 to-blue-500' },
              { step: '3', title: 'Match', desc: 'Compare against job requirements', gradient: 'from-green-500 to-teal-500' },
              { step: '4', title: 'Report', desc: 'Receive detailed feedback and scores', gradient: 'from-orange-500 to-red-500' }
            ].map((item, idx) => (
              <div key={item.step} className="relative text-center group">
                <div className={`relative inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-gradient-to-br ${item.gradient} text-white text-3xl font-bold mb-6 shadow-glow group-hover:shadow-glow-lg transition-all duration-300 group-hover:scale-110`}>
                  {item.step}
                  <div className="absolute inset-0 bg-white opacity-0 group-hover:opacity-20 rounded-2xl transition-opacity"></div>
                </div>
                {idx < 3 && (
                  <div className="hidden md:block absolute top-10 left-[60%] w-full h-0.5 bg-gradient-to-r from-purple-300 to-transparent"></div>
                )}
                <h3 className="text-xl font-bold text-gray-900 mb-3">
                  {item.title}
                </h3>
                <p className="text-gray-600">
                  {item.desc}
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>
      
      {/* CTA Section */}
      <div className="relative py-20 bg-gradient-to-r from-purple-600 via-pink-600 to-cyan-600 overflow-hidden">
        <div className="absolute inset-0 bg-black opacity-10"></div>
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div className="inline-flex items-center gap-2 bg-white/20 backdrop-blur-sm text-white px-4 py-2 rounded-full text-sm font-semibold mb-6">
            <Sparkles className="h-4 w-4" />
            Start Your Journey Today
          </div>
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
            Ready to Transform Your Hiring?
          </h2>
          <p className="text-xl text-white/90 mb-10 max-w-2xl mx-auto">
            Join the future of recruitment with AI-powered video resume analysis. Get started in minutes.
          </p>
          <Link
            to="/candidate"
            className="inline-flex items-center justify-center px-10 py-4 text-lg font-semibold rounded-xl text-purple-600 bg-white hover:bg-gray-50 shadow-2xl hover:shadow-glow-lg transition-all duration-300 transform hover:scale-105"
          >
            <Sparkles className="h-5 w-5 mr-2" />
            Get Started Now
            <TrendingUp className="h-5 w-5 ml-2" />
          </Link>
        </div>
      </div>
    </div>
  )
}
