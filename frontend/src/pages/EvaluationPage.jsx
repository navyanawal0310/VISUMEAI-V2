import React, { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { 
  Loader, AlertCircle, Download, ArrowLeft, 
  CheckCircle, XCircle, TrendingUp, Video,
  FileText, Target, MessageSquare, Award
} from 'lucide-react'
import { getEvaluation, compareSubmissions } from '../services/api'
import ImprovementComparison from '../components/ImprovementComparison'
import { 
  BarChart, Bar, RadarChart, Radar, PolarGrid, 
  PolarAngleAxis, PolarRadiusAxis, XAxis, YAxis, 
  CartesianGrid, Tooltip, Legend, ResponsiveContainer 
} from 'recharts'

export default function EvaluationPage() {
  const { id } = useParams()
  const [evaluation, setEvaluation] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [improvementComparison, setImprovementComparison] = useState(null)
  const [showImprovementModal, setShowImprovementModal] = useState(false)
  
  useEffect(() => {
    loadEvaluation()
  }, [id])
  
  const loadEvaluation = async () => {
    try {
      const data = await getEvaluation(id)
      setEvaluation(data)
      
      // Check if there's a previous submission to compare
      if (data.previous_evaluation_id) {
        loadImprovementComparison(data.evaluation_id, data.previous_evaluation_id)
      }
    } catch (err) {
      console.error('Failed to load evaluation:', err)
      setError('Failed to load evaluation')
    } finally {
      setLoading(false)
    }
  }
  
  const loadImprovementComparison = async (currentId, previousId) => {
    try {
      const comparison = await compareSubmissions(currentId, previousId)
      setImprovementComparison(comparison)
      setShowImprovementModal(true)  // Auto-show on load
    } catch (err) {
      console.error('Failed to load improvement comparison:', err)
    }
  }
  
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader className="h-12 w-12 animate-spin text-primary-600" />
      </div>
    )
  }
  
  if (error || !evaluation) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-12">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 flex items-start">
          <AlertCircle className="h-6 w-6 text-red-600 mt-0.5 mr-3 flex-shrink-0" />
          <div>
            <h3 className="text-lg font-semibold text-red-900 mb-1">Error</h3>
            <p className="text-red-700">{error || 'Evaluation not found'}</p>
          </div>
        </div>
        <Link to="/recruiter" className="mt-6 inline-flex items-center text-primary-600 hover:text-primary-900">
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Dashboard
        </Link>
      </div>
    )
  }
  
  // Prepare chart data
  const scoreData = [
    { 
      name: 'Technical', 
      score: evaluation.role_match?.match_percentage || 0 
    },
    { 
      name: 'Soft Skills', 
      score: evaluation.soft_skill_index ? evaluation.soft_skill_index.overall_score * 100 : 0 
    },
    { 
      name: 'Video', 
      score: evaluation.video_analysis ? evaluation.video_analysis.confidence_score * 100 : 0 
    },
    { 
      name: 'Overall', 
      score: evaluation.overall_score 
    }
  ]
  
  const softSkillData = evaluation.soft_skill_index ? [
    { skill: 'Communication', value: evaluation.soft_skill_index.communication * 100 },
    { skill: 'Confidence', value: evaluation.soft_skill_index.confidence * 100 },
    { skill: 'Engagement', value: evaluation.soft_skill_index.engagement * 100 },
    { skill: 'Professionalism', value: evaluation.soft_skill_index.professionalism * 100 }
  ] : []
  
  const getScoreColor = (score) => {
    if (score >= 80) return 'bg-green-100 text-green-800'
    if (score >= 60) return 'bg-yellow-100 text-yellow-800'
    return 'bg-red-100 text-red-800'
  }
  
  const getScoreBadge = (score) => {
    if (score >= 80) return { text: 'Excellent', color: 'bg-green-500' }
    if (score >= 60) return { text: 'Good', color: 'bg-yellow-500' }
    return { text: 'Needs Work', color: 'bg-red-500' }
  }
  
  const badge = getScoreBadge(evaluation.overall_score)
  
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      {/* Header */}
      <div className="mb-6">
        <Link to="/recruiter" className="inline-flex items-center text-primary-600 hover:text-primary-900 mb-4">
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Dashboard
        </Link>
        
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-4xl font-bold text-gray-900">
                {evaluation.candidate_name}
              </h1>
              {evaluation.submission_version > 1 && (
                <span className="inline-flex items-center px-3 py-1 rounded-full bg-gradient-to-r from-purple-100 to-cyan-100 text-purple-700 text-sm font-bold">
                  Version {evaluation.submission_version}
                </span>
              )}
            </div>
            <p className="text-lg text-gray-600">
              Evaluation Report
            </p>
            
            {/* Action Buttons */}
            <div className="mt-3 flex flex-wrap gap-3">
              {evaluation.previous_evaluation_id && improvementComparison && (
                <button
                  onClick={() => setShowImprovementModal(true)}
                  className="inline-flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-green-500 to-teal-500 text-white rounded-lg font-semibold hover:from-green-600 hover:to-teal-600 shadow-lg hover:shadow-glow transition-all"
                >
                  <TrendingUp className="h-4 w-4" />
                  View Improvement Stats
                </button>
              )}
              
              <a
                href={`/api/v1/export-pdf/${evaluation.evaluation_id}`}
                download
                className="inline-flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-purple-600 to-cyan-600 text-white rounded-lg font-semibold hover:from-purple-700 hover:to-cyan-700 shadow-lg hover:shadow-glow transition-all"
              >
                <Download className="h-4 w-4" />
                Export to PDF
              </a>
            </div>
          </div>
          
          <div className="text-right">
            <div className={`inline-flex items-center px-4 py-2 rounded-full text-white font-semibold ${badge.color}`}>
              <Award className="h-5 w-5 mr-2" />
              {badge.text}
            </div>
            <div className="mt-2 text-3xl font-bold text-gray-900">
              {evaluation.overall_score.toFixed(1)}<span className="text-lg text-gray-500">/100</span>
            </div>
            {evaluation.submission_version > 1 && improvementComparison && (
              <div className={`mt-2 inline-flex items-center gap-1 text-sm font-semibold ${
                improvementComparison.score_change > 0 ? 'text-green-600' :
                improvementComparison.score_change < 0 ? 'text-red-600' :
                'text-gray-600'
              }`}>
                {improvementComparison.score_change > 0 ? '↑' : improvementComparison.score_change < 0 ? '↓' : '→'}
                {Math.abs(improvementComparison.score_change).toFixed(1)} pts from last attempt
              </div>
            )}
          </div>
        </div>
      </div>
      
      {/* Improvement Comparison Modal */}
      {showImprovementModal && improvementComparison && (
        <ImprovementComparison 
          comparison={improvementComparison}
          onClose={() => setShowImprovementModal(false)}
        />
      )}
      
      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm">
          <div className="flex items-start justify-between">
            <div>
              <div className="text-sm text-gray-600 mb-1">Recommendation</div>
              <div className="text-2xl font-bold text-gray-900">{evaluation.recommendation}</div>
            </div>
            <Target className="h-10 w-10 text-primary-600" />
          </div>
        </div>
        
        <div className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm">
          <div className="flex items-start justify-between">
            <div>
              <div className="text-sm text-gray-600 mb-1">Role Match</div>
              <div className="text-2xl font-bold text-gray-900">
                {evaluation.role_match?.match_percentage.toFixed(1)}%
              </div>
            </div>
            <CheckCircle className="h-10 w-10 text-green-600" />
          </div>
        </div>
        
        <div className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm">
          <div className="flex items-start justify-between">
            <div>
              <div className="text-sm text-gray-600 mb-1">Evaluation Date</div>
              <div className="text-lg font-semibold text-gray-900">
                {new Date(evaluation.created_at).toLocaleDateString()}
              </div>
            </div>
            <FileText className="h-10 w-10 text-primary-600" />
          </div>
        </div>
      </div>
      
      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <div className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Score Breakdown</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={scoreData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis domain={[0, 100]} />
              <Tooltip />
              <Bar dataKey="score" fill="#3b82f6" />
            </BarChart>
          </ResponsiveContainer>
        </div>
        
        {softSkillData.length > 0 && (
          <div className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Soft Skills Profile</h2>
            <ResponsiveContainer width="100%" height={300}>
              <RadarChart data={softSkillData}>
                <PolarGrid />
                <PolarAngleAxis dataKey="skill" />
                <PolarRadiusAxis domain={[0, 100]} />
                <Radar name="Score" dataKey="value" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.6} />
                <Tooltip />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>
      
      {/* Detailed Analysis */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Video Analysis */}
        {evaluation.video_analysis && (
          <div className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm">
            <div className="flex items-center mb-4">
              <Video className="h-6 w-6 text-primary-600 mr-2" />
              <h2 className="text-xl font-semibold text-gray-900">Video Analysis</h2>
            </div>
            
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-gray-700">Confidence</span>
                <span className={`px-3 py-1 rounded-full text-sm font-semibold ${getScoreColor(evaluation.video_analysis.confidence_score * 100)}`}>
                  {(evaluation.video_analysis.confidence_score * 100).toFixed(1)}%
                </span>
              </div>
              
              <div className="flex justify-between items-center">
                <span className="text-gray-700">Eye Contact</span>
                <span className={`px-3 py-1 rounded-full text-sm font-semibold ${getScoreColor(evaluation.video_analysis.eye_contact_score * 100)}`}>
                  {(evaluation.video_analysis.eye_contact_score * 100).toFixed(1)}%
                </span>
              </div>
              
              <div className="flex justify-between items-center">
                <span className="text-gray-700">Posture</span>
                <span className={`px-3 py-1 rounded-full text-sm font-semibold ${getScoreColor(evaluation.video_analysis.posture_score * 100)}`}>
                  {(evaluation.video_analysis.posture_score * 100).toFixed(1)}%
                </span>
              </div>
              
              <div className="flex justify-between items-center">
                <span className="text-gray-700">Expressiveness</span>
                <span className={`px-3 py-1 rounded-full text-sm font-semibold ${getScoreColor(evaluation.video_analysis.expressiveness_score * 100)}`}>
                  {(evaluation.video_analysis.expressiveness_score * 100).toFixed(1)}%
                </span>
              </div>
            </div>
          </div>
        )}
        
        {/* Communication Analysis */}
        {evaluation.transcript_analysis && (
          <div className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm">
            <div className="flex items-center mb-4">
              <MessageSquare className="h-6 w-6 text-primary-600 mr-2" />
              <h2 className="text-xl font-semibold text-gray-900">Communication Analysis</h2>
            </div>
            
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-gray-700">Clarity</span>
                <span className={`px-3 py-1 rounded-full text-sm font-semibold ${getScoreColor(evaluation.transcript_analysis.clarity_score * 100)}`}>
                  {(evaluation.transcript_analysis.clarity_score * 100).toFixed(1)}%
                </span>
              </div>
              
              <div className="flex justify-between items-center">
                <span className="text-gray-700">Vocabulary</span>
                <span className={`px-3 py-1 rounded-full text-sm font-semibold ${getScoreColor(evaluation.transcript_analysis.vocabulary_diversity * 100)}`}>
                  {(evaluation.transcript_analysis.vocabulary_diversity * 100).toFixed(1)}%
                </span>
              </div>
              
              <div className="flex justify-between items-center">
                <span className="text-gray-700">Coherence</span>
                <span className={`px-3 py-1 rounded-full text-sm font-semibold ${getScoreColor(evaluation.transcript_analysis.coherence_score * 100)}`}>
                  {(evaluation.transcript_analysis.coherence_score * 100).toFixed(1)}%
                </span>
              </div>
              
              <div className="mt-4">
                <span className="text-gray-700 font-medium">Technical Terms:</span>
                <div className="mt-2 flex flex-wrap gap-2">
                  {evaluation.transcript_analysis.technical_terms.slice(0, 8).map((term, idx) => (
                    <span key={idx} className="px-2 py-1 bg-primary-100 text-primary-700 text-xs rounded-full">
                      {term}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
      
      {/* Role Match Details */}
      {evaluation.role_match && (
        <div className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Role Match Analysis</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="text-lg font-medium text-green-700 mb-3 flex items-center">
                <CheckCircle className="h-5 w-5 mr-2" />
                Matching Skills
              </h3>
              <div className="flex flex-wrap gap-2">
                {evaluation.role_match.matching_skills.map((skill, idx) => (
                  <span key={idx} className="px-3 py-1 bg-green-100 text-green-800 text-sm rounded-full">
                    {skill}
                  </span>
                ))}
                {evaluation.role_match.matching_skills.length === 0 && (
                  <p className="text-gray-500">No matching skills identified</p>
                )}
              </div>
            </div>
            
            <div>
              <h3 className="text-lg font-medium text-red-700 mb-3 flex items-center">
                <XCircle className="h-5 w-5 mr-2" />
                Missing Skills
              </h3>
              <div className="flex flex-wrap gap-2">
                {evaluation.role_match.missing_skills.slice(0, 10).map((skill, idx) => (
                  <span key={idx} className="px-3 py-1 bg-red-100 text-red-800 text-sm rounded-full">
                    {skill}
                  </span>
                ))}
                {evaluation.role_match.missing_skills.length === 0 && (
                  <p className="text-gray-500">All required skills matched</p>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
      
    </div>
  )
}
