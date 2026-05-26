import React, { useState, useEffect } from 'react'
import {
  Loader, AlertCircle, ArrowLeft,
  CheckCircle2, XCircle, TrendingUp, Award,
  Cpu, Briefcase, FileSearch, MessageSquare, Target, Download
} from 'lucide-react'
import {
  BarChart, Bar, RadarChart, Radar, PolarGrid,
  PolarAngleAxis, PolarRadiusAxis, XAxis, YAxis,
  CartesianGrid, Tooltip, ResponsiveContainer, Cell
} from 'recharts'
import { useLocation, Link } from 'react-router-dom'

// ── Helpers ─────────────────────────────────────────────────────────────────

function clamp(v) { return Math.min(100, Math.max(0, v ?? 0)) }

function getBadge(score) {
  if (score >= 80) return { label: 'Excellent', bg: 'bg-emerald-500', ring: 'ring-emerald-300', text: 'text-emerald-700', light: 'bg-emerald-50' }
  if (score >= 60) return { label: 'Good',      bg: 'bg-amber-500',   ring: 'ring-amber-300',   text: 'text-amber-700',   light: 'bg-amber-50'   }
  return               { label: 'Needs Work', bg: 'bg-rose-500',    ring: 'ring-rose-300',    text: 'text-rose-700',    light: 'bg-rose-50'    }
}

function ScoreRing({ score, size = 120, stroke = 10, badge }) {
  const r = (size - stroke) / 2
  const circ = 2 * Math.PI * r
  const offset = circ - (score / 100) * circ
  return (
    <svg width={size} height={size} className="-rotate-90">
      <circle cx={size/2} cy={size/2} r={r} fill="none" stroke="#e5e7eb" strokeWidth={stroke} />
      <circle
        cx={size/2} cy={size/2} r={r} fill="none"
        stroke={score >= 80 ? '#10b981' : score >= 60 ? '#f59e0b' : '#f43f5e'}
        strokeWidth={stroke}
        strokeDasharray={circ}
        strokeDashoffset={offset}
        strokeLinecap="round"
        style={{ transition: 'stroke-dashoffset 1s ease' }}
      />
      <text
        x={size/2} y={size/2 + 6}
        textAnchor="middle"
        className="rotate-90"
        style={{ transform: `rotate(90deg)`, transformOrigin: `${size/2}px ${size/2}px`, fontSize: 22, fontWeight: 700, fill: '#111827' }}
      >
        {score.toFixed(0)}
      </text>
    </svg>
  )
}

function MiniScoreCard({ icon: Icon, label, value, color }) {
  const pct = clamp(value)
  return (
    <div className="bg-white rounded-xl border border-gray-100 p-4 shadow-sm flex flex-col gap-2">
      <div className="flex items-center gap-2 text-gray-500 text-sm font-medium">
        <Icon size={15} className={color} />
        {label}
      </div>
      <div className="flex items-end justify-between">
        <span className="text-2xl font-bold text-gray-800">{pct.toFixed(0)}</span>
        <span className="text-sm text-gray-400 mb-0.5">/ 100</span>
      </div>
      <div className="w-full bg-gray-100 rounded-full h-1.5">
        <div
          className="h-1.5 rounded-full transition-all duration-700"
          style={{ width: `${pct}%`, background: pct >= 80 ? '#10b981' : pct >= 60 ? '#f59e0b' : '#f43f5e' }}
        />
      </div>
    </div>
  )
}

const BAR_COLORS = ['#6366f1', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981']

// ── Page ─────────────────────────────────────────────────────────────────────

export default function EvaluationPage() {
  const location = useLocation()
  const passedData = location.state

  const [evaluation, setEvaluation] = useState(null)
  const [loading, setLoading]       = useState(true)
  const [error, setError]           = useState(null)

  useEffect(() => {
    if (passedData) {
      setEvaluation(passedData)
      setLoading(false)
      return
    }
    const cached = localStorage.getItem('evaluation')
    if (cached) { setEvaluation(JSON.parse(cached)); setLoading(false); return }
    setError('No evaluation data found. Please upload again.')
    setLoading(false)
  }, [passedData])

  useEffect(() => {
    if (passedData) localStorage.setItem('evaluation', JSON.stringify(passedData))
  }, [passedData])

  if (loading) return (
    <div className="flex items-center justify-center min-h-screen bg-gray-50">
      <Loader className="h-10 w-10 animate-spin text-indigo-600" />
    </div>
  )

  if (error || !evaluation) return (
    <div className="p-10 text-center">
      <AlertCircle className="mx-auto mb-4 text-rose-500" size={40} />
      <h2 className="text-lg font-semibold mb-2">Something went wrong</h2>
      <p className="text-gray-600 mb-4">{error}</p>
      <Link to="/candidate" className="px-4 py-2 bg-indigo-600 text-white rounded-lg">Go Back</Link>
    </div>
  )

  // ── Field mapping (fixed: backend returns "matching_skills") ───────────────
  const overallScore        = clamp(evaluation.match_percentage ?? evaluation.overall_score ?? evaluation.score ?? 0)
  const technicalScore      = clamp(evaluation.technical_score)
  const experienceScore     = clamp(evaluation.experience_score)
  const atsScore            = clamp(evaluation.ats_score)
  const communicationScore  = clamp(evaluation.communication_score)

  // FIX: backend field is "matching_skills", not "skills" or "skills_matched"
  const matchedSkills  = evaluation.matching_skills ?? evaluation.skills ?? evaluation.skills_matched ?? []
  const missingSkills  = evaluation.missing_skills  ?? []
  const strengths      = evaluation.strengths       ?? []
  const gaps           = evaluation.gaps            ?? []
  const experienceMatch = evaluation.experience_match ?? null
  const semSimilarity  = evaluation.semantic_similarity ?? null
  const feedback       = evaluation.feedback        ?? (gaps.length ? gaps.join(' ') : 'No feedback available.')

  const badge = getBadge(overallScore)

  const barData = [
    { name: 'Technical',     score: technicalScore },
    { name: 'Experience',    score: experienceScore },
    { name: 'ATS',           score: atsScore },
    { name: 'Communication', score: communicationScore },
    { name: 'Overall',       score: overallScore },
  ]

  const radarData = [
    { subject: 'Technical',     value: technicalScore },
    { subject: 'Experience',    value: experienceScore },
    { subject: 'ATS',           value: atsScore },
    { subject: 'Communication', value: communicationScore },
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-5xl mx-auto px-4 py-8 space-y-6">

        {/* ── Top bar ── */}
        <div className="flex justify-between items-center">
          <Link to="/candidate" className="flex items-center gap-1.5 text-indigo-600 hover:text-indigo-800 font-medium text-sm">
            <ArrowLeft size={16} /> Back
          </Link>
          <div className="flex items-center gap-3">
            {evaluation.report_url && (
              <a
                href={`http://localhost:8000${evaluation.report_url}`}
                target="_blank"
                rel="noreferrer"
                className="flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium text-indigo-700 bg-indigo-50 border border-indigo-200 rounded-full hover:bg-indigo-100 transition-colors"
              >
                <Download size={14} /> Download PDF Report
              </a>
            )}
            <span className={`px-4 py-1.5 text-white text-sm font-semibold rounded-full shadow ${badge.bg}`}>
              {badge.label}
            </span>
          </div>
        </div>

        {/* ── Hero card ── */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 flex flex-col sm:flex-row items-center gap-6">
          <div className="flex-shrink-0">
            <ScoreRing score={overallScore} size={130} stroke={12} badge={badge} />
          </div>
          <div className="flex-1 text-center sm:text-left">
            <h1 className="text-2xl font-bold text-gray-900 mb-1">
              {evaluation.candidate_name || 'Candidate'}
            </h1>
            <p className="text-gray-500 text-sm mb-3">Overall match score</p>
            <div className="flex flex-wrap gap-2 justify-center sm:justify-start">
              {typeof experienceMatch === 'boolean' && (
                <span className={`flex items-center gap-1 text-xs px-3 py-1 rounded-full font-medium
                  ${experienceMatch ? 'bg-emerald-100 text-emerald-700' : 'bg-rose-100 text-rose-700'}`}>
                  {experienceMatch
                    ? <><CheckCircle2 size={12}/> Experience matched</>
                    : <><XCircle size={12}/> Experience below requirement</>}
                </span>
              )}
              {semSimilarity !== null && (
                <span className="flex items-center gap-1 text-xs px-3 py-1 rounded-full font-medium bg-indigo-100 text-indigo-700">
                  <TrendingUp size={12}/> Semantic similarity: {(semSimilarity * 100).toFixed(0)}%
                </span>
              )}
            </div>
          </div>
        </div>

        {/* ── Mini score cards ── */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <MiniScoreCard icon={Cpu}           label="Technical"     value={technicalScore}     color="text-indigo-500" />
          <MiniScoreCard icon={Briefcase}     label="Experience"    value={experienceScore}    color="text-violet-500" />
          <MiniScoreCard icon={FileSearch}    label="ATS"           value={atsScore}           color="text-pink-500"   />
          <MiniScoreCard icon={MessageSquare} label="Communication" value={communicationScore} color="text-amber-500"  />
        </div>

        {/* ── Charts ── */}
        <div className="grid md:grid-cols-2 gap-4">

          <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-5">
            <h2 className="font-semibold text-gray-800 mb-4 flex items-center gap-2">
              <Target size={16} className="text-indigo-500" /> Score Breakdown
            </h2>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={barData} barSize={32}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f3f4f6" />
                <XAxis dataKey="name" tick={{ fontSize: 11, fill: '#9ca3af' }} axisLine={false} tickLine={false} />
                <YAxis domain={[0, 100]} tick={{ fontSize: 11, fill: '#9ca3af' }} axisLine={false} tickLine={false} />
                <Tooltip
                  formatter={(v) => [`${Number(v).toFixed(1)}%`, 'Score']}
                  contentStyle={{ borderRadius: 10, border: 'none', boxShadow: '0 4px 20px rgba(0,0,0,0.08)' }}
                />
                <Bar dataKey="score" radius={[6, 6, 0, 0]}>
                  {barData.map((_, i) => <Cell key={i} fill={BAR_COLORS[i]} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-5">
            <h2 className="font-semibold text-gray-800 mb-4 flex items-center gap-2">
              <Award size={16} className="text-indigo-500" /> Competency Radar
            </h2>
            <ResponsiveContainer width="100%" height={220}>
              <RadarChart data={radarData}>
                <PolarGrid stroke="#e5e7eb" />
                <PolarAngleAxis dataKey="subject" tick={{ fontSize: 11, fill: '#6b7280' }} />
                <PolarRadiusAxis domain={[0, 100]} tick={false} axisLine={false} />
                <Radar
                  dataKey="value"
                  stroke="#6366f1"
                  fill="#6366f1"
                  fillOpacity={0.25}
                  strokeWidth={2}
                />
                <Tooltip
                  formatter={(v) => [`${Number(v).toFixed(1)}%`, 'Score']}
                  contentStyle={{ borderRadius: 10, border: 'none', boxShadow: '0 4px 20px rgba(0,0,0,0.08)' }}
                />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* ── Skill analysis ── */}
        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-5">
          <h2 className="font-semibold text-gray-800 mb-4">Skill Analysis</h2>
          <div className="grid md:grid-cols-2 gap-6">

            <div>
              <h3 className="text-sm font-semibold text-emerald-600 mb-2 flex items-center gap-1.5">
                <CheckCircle2 size={14}/> Matched Skills ({matchedSkills.length})
              </h3>
              {matchedSkills.length > 0 ? (
                <div className="flex flex-wrap gap-2">
                  {matchedSkills.map((s, i) => (
                    <span key={i} className="bg-emerald-50 text-emerald-700 border border-emerald-200 text-xs px-2.5 py-1 rounded-full font-medium">
                      {s}
                    </span>
                  ))}
                </div>
              ) : (
                <p className="text-gray-400 text-sm italic">No matched skills detected</p>
              )}
            </div>

            <div>
              <h3 className="text-sm font-semibold text-rose-600 mb-2 flex items-center gap-1.5">
                <XCircle size={14}/> Missing Skills ({missingSkills.length})
              </h3>
              {missingSkills.length > 0 ? (
                <div className="flex flex-wrap gap-2">
                  {missingSkills.map((s, i) => (
                    <span key={i} className="bg-rose-50 text-rose-700 border border-rose-200 text-xs px-2.5 py-1 rounded-full font-medium">
                      {s}
                    </span>
                  ))}
                </div>
              ) : (
                <p className="text-gray-400 text-sm italic">No missing skills — great coverage!</p>
              )}
            </div>
          </div>
        </div>

        {/* ── Strengths & Gaps ── */}
        {(strengths.length > 0 || gaps.length > 0) && (
          <div className="grid md:grid-cols-2 gap-4">

            {strengths.length > 0 && (
              <div className="bg-emerald-50 border border-emerald-100 rounded-2xl p-5">
                <h2 className="font-semibold text-emerald-800 mb-3 flex items-center gap-2">
                  <TrendingUp size={16}/> Strengths
                </h2>
                <ul className="space-y-2">
                  {strengths.map((s, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-emerald-700">
                      <CheckCircle2 size={14} className="mt-0.5 flex-shrink-0" />
                      {s}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {gaps.length > 0 && (
              <div className="bg-rose-50 border border-rose-100 rounded-2xl p-5">
                <h2 className="font-semibold text-rose-800 mb-3 flex items-center gap-2">
                  <AlertCircle size={16}/> Gaps to Address
                </h2>
                <ul className="space-y-2">
                  {gaps.map((g, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-rose-700">
                      <XCircle size={14} className="mt-0.5 flex-shrink-0" />
                      {g}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}

        {/* ── Feedback ── */}
        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-5">
          <h2 className="font-semibold text-gray-800 mb-2">Evaluator Feedback</h2>
          <p className="text-gray-600 text-sm leading-relaxed">{feedback}</p>
        </div>
      {/* Improvement Recommendations */}
{evaluation.improvement_recommendations && (
  <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 mt-6">
    <h3 className="text-xl font-semibold mb-4">
      Improvement Recommendations
    </h3>

    <div className="space-y-3">
      {evaluation.improvement_recommendations.map((item, index) => (
        <div
          key={index}
          className="border border-gray-200 rounded-xl p-4"
        >
          <div className="flex items-center justify-between mb-2">
            <h4 className="font-medium text-gray-900">
              {item.category}
            </h4>

            <span className={`px-2 py-1 rounded-full text-xs font-medium ${
              item.priority === "high"
                ? "bg-red-100 text-red-700"
                : item.priority === "medium"
                ? "bg-yellow-100 text-yellow-700"
                : "bg-green-100 text-green-700"
            }`}>
              {item.priority}
            </span>
          </div>

          <p className="text-gray-600 text-sm mb-2">
            {item.issue}
          </p>

          <p className="text-blue-600 text-sm font-medium">
            → {item.suggestion}
          </p>
        </div>
      ))}
    </div>
  </div>
)}

      </div>
    </div>
  )
}