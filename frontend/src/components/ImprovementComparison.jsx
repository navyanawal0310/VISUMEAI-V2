import React from 'react'
import { TrendingUp, TrendingDown, Minus, CheckCircle, AlertCircle, Award, Target } from 'lucide-react'

export default function ImprovementComparison({ comparison, onClose }) {
  if (!comparison) return null

  const getChangeIcon = (change) => {
    if (change > 0) return <TrendingUp className="h-5 w-5 text-green-600" />
    if (change < 0) return <TrendingDown className="h-5 w-5 text-red-600" />
    return <Minus className="h-5 w-5 text-gray-400" />
  }

  const getChangeColor = (change) => {
    if (change > 5) return 'text-green-700 bg-green-100'
    if (change > 0) return 'text-green-600 bg-green-50'
    if (change === 0) return 'text-gray-600 bg-gray-100'
    if (change > -5) return 'text-orange-600 bg-orange-50'
    return 'text-red-700 bg-red-100'
  }

  const getScoreChangeDisplay = (change) => {
    const sign = change >= 0 ? '+' : ''
    return `${sign}${change.toFixed(1)}`
  }

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4 z-50 animate-in fade-in duration-200">
      <div className="bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-gradient-to-r from-purple-600 to-cyan-600 text-white px-8 py-6 rounded-t-2xl">
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-2xl font-bold flex items-center gap-2">
                <Award className="h-7 w-7" />
                Improvement Analysis
              </h2>
              <p className="text-purple-100 mt-1">
                {comparison.candidate_name} - {comparison.job_title}
              </p>
            </div>
            <button
              onClick={onClose}
              className="text-white hover:bg-white/20 rounded-lg p-2 transition-colors"
            >
              ✕
            </button>
          </div>
        </div>

        {/* Overall Score Comparison */}
        <div className="px-8 py-6 bg-gradient-to-br from-purple-50 to-cyan-50">
          <div className="grid grid-cols-3 gap-6">
            <div className="text-center">
              <p className="text-sm text-gray-600 mb-2">Version {comparison.previous_version}</p>
              <div className="text-3xl font-bold text-gray-900">
                {comparison.previous_score.toFixed(1)}
              </div>
              <p className="text-xs text-gray-500 mt-1">Previous Score</p>
            </div>
            
            <div className="flex items-center justify-center">
              <div className={`px-6 py-3 rounded-xl ${getChangeColor(comparison.score_change)} font-bold text-2xl shadow-lg`}>
                {getChangeIcon(comparison.score_change)}
                <span className="ml-2">{getScoreChangeDisplay(comparison.score_change)}</span>
              </div>
            </div>
            
            <div className="text-center">
              <p className="text-sm text-gray-600 mb-2">Version {comparison.current_version}</p>
              <div className="text-3xl font-bold bg-gradient-to-r from-purple-600 to-cyan-600 bg-clip-text text-transparent">
                {comparison.current_score.toFixed(1)}
              </div>
              <p className="text-xs text-gray-500 mt-1">Current Score</p>
            </div>
          </div>

          {/* Percentage Change */}
          <div className="text-center mt-4">
            <span className={`inline-flex items-center gap-2 px-4 py-2 rounded-full text-sm font-semibold ${
              comparison.score_change_percentage > 0 ? 'bg-green-100 text-green-800' : 
              comparison.score_change_percentage < 0 ? 'bg-red-100 text-red-800' : 
              'bg-gray-100 text-gray-800'
            }`}>
              {comparison.score_change_percentage > 0 ? '📈' : comparison.score_change_percentage < 0 ? '📉' : '➡️'}
              {Math.abs(comparison.score_change_percentage).toFixed(1)}% Change
            </span>
          </div>
        </div>

        {/* Summary */}
        <div className="px-8 py-6 border-b">
          <div className="bg-blue-50 border-l-4 border-blue-500 p-4 rounded-r-lg">
            <p className="text-blue-900 font-medium">
              {comparison.overall_improvement_summary}
            </p>
          </div>
          
          <div className="mt-4">
            <p className="text-sm font-semibold text-gray-700">
              {comparison.recommendation_change}
            </p>
          </div>
        </div>

        {/* Detailed Metrics Comparison */}
        <div className="px-8 py-6">
          <h3 className="text-xl font-bold text-gray-900 mb-6 flex items-center gap-2">
            <Target className="h-6 w-6 text-purple-600" />
            Detailed Metrics
          </h3>
          
          <div className="space-y-4">
            {Object.entries(comparison.improvements).map(([category, metrics]) => (
              <div key={category} className="bg-white border border-gray-200 rounded-xl p-4 hover:shadow-md transition-shadow">
                <div className="flex items-center justify-between mb-3">
                  <h4 className="font-semibold text-gray-900">{category}</h4>
                  <div className="flex items-center gap-2">
                    {getChangeIcon(metrics.change)}
                    <span className={`font-bold ${
                      metrics.change > 0 ? 'text-green-600' : 
                      metrics.change < 0 ? 'text-red-600' : 
                      'text-gray-600'
                    }`}>
                      {getScoreChangeDisplay(metrics.change)}
                    </span>
                  </div>
                </div>
                
                <div className="flex items-center gap-4">
                  {/* Previous Score */}
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-xs text-gray-500">Before:</span>
                      <span className="text-sm font-semibold text-gray-700">
                        {metrics.old.toFixed(1)}
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-gray-400 h-2 rounded-full transition-all"
                        style={{ width: `${metrics.old}%` }}
                      ></div>
                    </div>
                  </div>
                  
                  {/* Arrow */}
                  <div className="text-gray-400">→</div>
                  
                  {/* Current Score */}
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-xs text-gray-500">After:</span>
                      <span className="text-sm font-semibold text-purple-700">
                        {metrics.new.toFixed(1)}
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className={`h-2 rounded-full transition-all ${
                          metrics.change > 0 ? 'bg-gradient-to-r from-green-400 to-green-600' :
                          metrics.change < 0 ? 'bg-gradient-to-r from-red-400 to-red-600' :
                          'bg-gray-400'
                        }`}
                        style={{ width: `${metrics.new}%` }}
                      ></div>
                    </div>
                  </div>
                </div>

                {/* Skills changes if available */}
                {metrics.new_skills && metrics.new_skills.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-gray-200">
                    <p className="text-xs font-semibold text-green-700 mb-1">
                      ✨ New Skills Added:
                    </p>
                    <div className="flex flex-wrap gap-1">
                      {metrics.new_skills.map(skill => (
                        <span key={skill} className="px-2 py-0.5 bg-green-100 text-green-800 text-xs rounded">
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Areas Improved & Declined */}
        <div className="px-8 py-6 bg-gray-50 grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Improvements */}
          {comparison.areas_improved.length > 0 && (
            <div>
              <h4 className="font-bold text-green-900 mb-3 flex items-center gap-2">
                <CheckCircle className="h-5 w-5" />
                Areas Improved
              </h4>
              <ul className="space-y-2">
                {comparison.areas_improved.map((area, index) => (
                  <li key={index} className="flex items-start gap-2 text-sm text-green-700">
                    <span className="text-green-500 mt-0.5">✓</span>
                    <span>{area}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
          
          {/* Areas to Work On */}
          {comparison.areas_declined.length > 0 && (
            <div>
              <h4 className="font-bold text-orange-900 mb-3 flex items-center gap-2">
                <AlertCircle className="h-5 w-5" />
                Areas to Focus On
              </h4>
              <ul className="space-y-2">
                {comparison.areas_declined.map((area, index) => (
                  <li key={index} className="flex items-start gap-2 text-sm text-orange-700">
                    <span className="text-orange-500 mt-0.5">!</span>
                    <span>{area}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {/* Close Button */}
        <div className="px-8 py-6 flex justify-end border-t">
          <button
            onClick={onClose}
            className="px-6 py-3 bg-gradient-to-r from-purple-600 to-cyan-600 text-white rounded-xl font-semibold hover:from-purple-700 hover:to-cyan-700 transition-all shadow-lg hover:shadow-glow"
          >
            Got it!
          </button>
        </div>
      </div>
    </div>
  )
}

