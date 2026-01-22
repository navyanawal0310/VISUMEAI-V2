import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Search, Filter, TrendingUp, TrendingDown, Minus, Eye, Loader, Users, Briefcase, Download } from 'lucide-react'
import { listEvaluations, listJobPostings } from '../services/api'
import JobManagement from '../components/JobManagement'

export default function RecruiterDashboard() {
  const [evaluations, setEvaluations] = useState([])
  const [jobPostings, setJobPostings] = useState([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('all')
  const [searchTerm, setSearchTerm] = useState('')
  const [activeTab, setActiveTab] = useState('candidates')
  
  useEffect(() => {
    if (activeTab === 'candidates') {
      loadEvaluations()
    } else if (activeTab === 'jobs') {
      loadJobPostings()
    }
  }, [activeTab])
  
  const loadEvaluations = async () => {
    setLoading(true)
    try {
      const data = await listEvaluations(50)
      setEvaluations(data)
    } catch (err) {
      console.error('Failed to load evaluations:', err)
    } finally {
      setLoading(false)
    }
  }
  
  const loadJobPostings = async () => {
    setLoading(true)
    try {
      const data = await listJobPostings('all', 50)
      setJobPostings(data)
    } catch (err) {
      console.error('Failed to load job postings:', err)
    } finally {
      setLoading(false)
    }
  }
  
  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-600 bg-green-100'
    if (score >= 60) return 'text-yellow-600 bg-yellow-100'
    return 'text-red-600 bg-red-100'
  }
  
  const getRecommendationIcon = (recommendation) => {
    if (recommendation.includes('Highly')) return <TrendingUp className="h-4 w-4 text-green-600" />
    if (recommendation.includes('Not')) return <TrendingDown className="h-4 w-4 text-red-600" />
    return <Minus className="h-4 w-4 text-yellow-600" />
  }
  
  const filteredEvaluations = evaluations
    .filter(e => {
      if (filter === 'top') return e.overall_score >= 80
      if (filter === 'good') return e.overall_score >= 60 && e.overall_score < 80
      if (filter === 'needs-improvement') return e.overall_score < 60
      return true
    })
    .filter(e => 
      e.candidate_name.toLowerCase().includes(searchTerm.toLowerCase())
    )
  
  const stats = {
    total: evaluations.length,
    highly_recommended: evaluations.filter(e => e.overall_score >= 80).length,
    recommended: evaluations.filter(e => e.overall_score >= 60 && e.overall_score < 80).length,
    needs_improvement: evaluations.filter(e => e.overall_score < 60).length,
    avg_score: evaluations.length > 0 
      ? (evaluations.reduce((sum, e) => sum + e.overall_score, 0) / evaluations.length).toFixed(1)
      : 0
  }
  
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader className="h-12 w-12 animate-spin text-primary-600" />
      </div>
    )
  }
  
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-2">
          Recruiter Dashboard
        </h1>
        <p className="text-lg text-gray-600">
          Manage job postings and review candidate evaluations
        </p>
      </div>
      
      {/* Tab Navigation */}
      <div className="mb-8 border-b border-gray-200">
        <nav className="flex gap-8">
          <button
            onClick={() => setActiveTab('candidates')}
            className={`flex items-center py-4 px-1 border-b-2 font-medium transition-colors ${
              activeTab === 'candidates'
                ? 'border-primary-600 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <Users className="h-5 w-5 mr-2" />
            Candidates
            {evaluations.length > 0 && (
              <span className="ml-2 px-2 py-0.5 text-xs bg-gray-100 text-gray-600 rounded-full">
                {evaluations.length}
              </span>
            )}
          </button>
          <button
            onClick={() => setActiveTab('jobs')}
            className={`flex items-center py-4 px-1 border-b-2 font-medium transition-colors ${
              activeTab === 'jobs'
                ? 'border-primary-600 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <Briefcase className="h-5 w-5 mr-2" />
            Job Postings
            {jobPostings.length > 0 && (
              <span className="ml-2 px-2 py-0.5 text-xs bg-gray-100 text-gray-600 rounded-full">
                {jobPostings.length}
              </span>
            )}
          </button>
        </nav>
      </div>
      
      {/* Tab Content */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <Loader className="h-12 w-12 animate-spin text-primary-600" />
        </div>
      ) : activeTab === 'candidates' ? (
        <div>
          {/* Statistics */}
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-8">
        <div className="bg-white rounded-lg border border-gray-200 p-4 shadow-sm">
          <div className="text-sm text-gray-600 mb-1">Total Candidates</div>
          <div className="text-2xl font-bold text-gray-900">{stats.total}</div>
        </div>
        
        <div className="bg-white rounded-lg border border-gray-200 p-4 shadow-sm">
          <div className="text-sm text-gray-600 mb-1">Highly Recommended</div>
          <div className="text-2xl font-bold text-green-600">{stats.highly_recommended}</div>
        </div>
        
        <div className="bg-white rounded-lg border border-gray-200 p-4 shadow-sm">
          <div className="text-sm text-gray-600 mb-1">Recommended</div>
          <div className="text-2xl font-bold text-yellow-600">{stats.recommended}</div>
        </div>
        
        <div className="bg-white rounded-lg border border-gray-200 p-4 shadow-sm">
          <div className="text-sm text-gray-600 mb-1">Needs Improvement</div>
          <div className="text-2xl font-bold text-red-600">{stats.needs_improvement}</div>
        </div>
        
        <div className="bg-white rounded-lg border border-gray-200 p-4 shadow-sm">
          <div className="text-sm text-gray-600 mb-1">Average Score</div>
          <div className="text-2xl font-bold text-primary-600">{stats.avg_score}</div>
        </div>
      </div>
      
      {/* Filters and Search */}
      <div className="bg-white rounded-lg border border-gray-200 p-4 mb-6 shadow-sm">
        <div className="flex flex-col md:flex-row gap-4">
          {/* Search */}
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search by candidate name..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            />
          </div>
          
          {/* Filter */}
          <div className="flex items-center gap-2">
            <Filter className="h-5 w-5 text-gray-400" />
            <select
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            >
              <option value="all">All Candidates</option>
              <option value="top">Top Matches (80+)</option>
              <option value="good">Good Matches (60-79)</option>
              <option value="needs-improvement">Needs Improvement (&lt;60)</option>
            </select>
          </div>
        </div>
      </div>
      
      {/* Evaluations Table */}
      <div className="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Candidate
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Overall Score
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Recommendation
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Date
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredEvaluations.length === 0 ? (
                <tr>
                  <td colSpan="5" className="px-6 py-12 text-center text-gray-500">
                    No evaluations found
                  </td>
                </tr>
              ) : (
                filteredEvaluations.map((evaluation) => (
                  <tr key={evaluation.evaluation_id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">
                        {evaluation.candidate_name}
                      </div>
                      <div className="text-xs text-gray-500">
                        ID: {evaluation.evaluation_id.slice(0, 8)}...
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-3 py-1 text-sm font-semibold rounded-full ${getScoreColor(evaluation.overall_score)}`}>
                        {evaluation.overall_score.toFixed(1)}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center gap-2">
                        {getRecommendationIcon(evaluation.recommendation)}
                        <span className="text-sm text-gray-900">
                          {evaluation.recommendation}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(evaluation.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <div className="flex items-center justify-end gap-3">
                        <Link
                          to={`/evaluation/${evaluation.evaluation_id}`}
                          className="inline-flex items-center text-primary-600 hover:text-primary-900 font-medium"
                        >
                          <Eye className="h-4 w-4 mr-1" />
                          View
                        </Link>
                        <a
                          href={`/api/v1/export-pdf/${evaluation.evaluation_id}`}
                          download
                          className="inline-flex items-center text-cyan-600 hover:text-cyan-900 font-medium"
                          title="Download PDF Report"
                        >
                          <Download className="h-4 w-4 mr-1" />
                          PDF
                        </a>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
        </div>
      ) : (
        <JobManagement jobPostings={jobPostings} onJobsUpdated={loadJobPostings} />
      )}
    </div>
  )
}
