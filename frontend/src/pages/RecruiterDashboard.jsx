import React, { useState, useEffect } from 'react'
import {
  Loader, AlertCircle, Users, TrendingUp, Award,
  Download, Eye, Cpu, Briefcase, FileSearch,
  MessageSquare, ChevronUp, ChevronDown, Search,
} from 'lucide-react'
import { useNavigate } from 'react-router-dom'

// ── Helpers (mirrors EvaluationPage) ─────────────────────────────────────────

function clamp(v) { return Math.min(100, Math.max(0, v ?? 0)) }

function getBadge(score) {
  if (score >= 80) return { label: 'Excellent', bg: 'bg-emerald-500', text: 'text-emerald-700', light: 'bg-emerald-50', border: 'border-emerald-200' }
  if (score >= 60) return { label: 'Good',      bg: 'bg-amber-500',   text: 'text-amber-700',   light: 'bg-amber-50',   border: 'border-amber-200'  }
  return               { label: 'Needs Work', bg: 'bg-rose-500',    text: 'text-rose-700',    light: 'bg-rose-50',    border: 'border-rose-200'   }
}

function ScorePill({ value, compact = false }) {
  const pct  = clamp(value)
  const color = pct >= 80 ? '#10b981' : pct >= 60 ? '#f59e0b' : '#f43f5e'
  return (
    <div className={`flex items-center gap-1.5 ${compact ? '' : 'min-w-[80px]'}`}>
      <div className="flex-1 bg-gray-100 rounded-full h-1.5">
        <div
          className="h-1.5 rounded-full transition-all duration-500"
          style={{ width: `${pct}%`, background: color }}
        />
      </div>
      <span className="text-xs font-semibold text-gray-700 tabular-nums w-7 text-right">
        {pct.toFixed(0)}
      </span>
    </div>
  )
}

function StatCard({ icon: Icon, label, value, sub, color }) {
  return (
    <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-5 flex items-center gap-4">
      <div className={`p-3 rounded-xl ${color}`}>
        <Icon size={20} className="text-white" />
      </div>
      <div>
        <p className="text-sm text-gray-500 font-medium">{label}</p>
        <p className="text-2xl font-bold text-gray-900 leading-tight">{value}</p>
        {sub && <p className="text-xs text-gray-400 mt-0.5">{sub}</p>}
      </div>
    </div>
  )
}

function SortIcon({ field, sortField, sortDir }) {
  if (sortField !== field) return <ChevronUp size={13} className="text-gray-300" />
  return sortDir === 'asc'
    ? <ChevronUp size={13} className="text-indigo-500" />
    : <ChevronDown size={13} className="text-indigo-500" />
}

// ── Main component ────────────────────────────────────────────────────────────

export default function RecruiterDashboard() {
  const navigate = useNavigate()

  const [candidates, setCandidates] = useState([])
  const [loading, setLoading]       = useState(true)
  const [error, setError]           = useState(null)
  const [search, setSearch]         = useState('')
  const [sortField, setSortField]   = useState('created_at')
  const [sortDir, setSortDir]       = useState('desc')

  // ── Fetch ─────────────────────────────────────────────────────────────────

  useEffect(() => {
    const controller = new AbortController()
    fetch('http://localhost:8000/candidates', { signal: controller.signal })
      .then(r => {
        if (!r.ok) throw new Error(`Server returned ${r.status}`)
        return r.json()
      })
      .then(data => { setCandidates(data); setLoading(false) })
      .catch(err => {
        if (err.name !== 'AbortError') {
          setError(err.message)
          setLoading(false)
        }
      })
    return () => controller.abort()
  }, [])

  // ── Derived stats ─────────────────────────────────────────────────────────

  const totalCandidates = candidates.length
  const avgScore = totalCandidates
    ? (candidates.reduce((s, c) => s + c.overall_score, 0) / totalCandidates).toFixed(1)
    : '—'
  const highestScore = totalCandidates
    ? Math.max(...candidates.map(c => c.overall_score)).toFixed(1)
    : '—'

  // ── Filter + sort ─────────────────────────────────────────────────────────

  const filtered = candidates
    .filter(c => {
      const q = search.toLowerCase()
      return (
        c.candidate_name.toLowerCase().includes(q) ||
        c.job_title.toLowerCase().includes(q)
      )
    })
    .sort((a, b) => {
      let av = a[sortField], bv = b[sortField]
      if (typeof av === 'string') av = av.toLowerCase(), bv = bv.toLowerCase()
      if (av < bv) return sortDir === 'asc' ? -1 : 1
      if (av > bv) return sortDir === 'asc' ? 1  : -1
      return 0
    })

  function toggleSort(field) {
    if (sortField === field) setSortDir(d => d === 'asc' ? 'desc' : 'asc')
    else { setSortField(field); setSortDir('desc') }
  }

  function handleView(candidate) {
    navigate('/evaluation', { state: candidate })
  }

  // ── Loading / error states ────────────────────────────────────────────────

  if (loading) return (
    <div className="flex items-center justify-center min-h-screen bg-gray-50">
      <Loader className="h-10 w-10 animate-spin text-indigo-600" />
    </div>
  )

  if (error) return (
    <div className="p-10 text-center">
      <AlertCircle className="mx-auto mb-4 text-rose-500" size={40} />
      <h2 className="text-lg font-semibold mb-2">Could not load candidates</h2>
      <p className="text-gray-600 mb-4">{error}</p>
      <button
        onClick={() => { setError(null); setLoading(true); window.location.reload() }}
        className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
      >
        Retry
      </button>
    </div>
  )

  // ── Render ────────────────────────────────────────────────────────────────

  const TH = ({ field, label, className = '' }) => (
    <th
      className={`px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide cursor-pointer select-none hover:text-indigo-600 ${className}`}
      onClick={() => toggleSort(field)}
    >
      <span className="flex items-center gap-1">
        {label}
        <SortIcon field={field} sortField={sortField} sortDir={sortDir} />
      </span>
    </th>
  )

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 py-8 space-y-6">

        {/* ── Header ── */}
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Recruiter Dashboard</h1>
          <p className="text-gray-500 text-sm mt-1">All candidate evaluations</p>
        </div>

        {/* ── Stat cards ── */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <StatCard
            icon={Users}
            label="Total Candidates"
            value={totalCandidates}
            sub="evaluated so far"
            color="bg-indigo-500"
          />
          <StatCard
            icon={TrendingUp}
            label="Average Score"
            value={avgScore}
            sub="across all roles"
            color="bg-violet-500"
          />
          <StatCard
            icon={Award}
            label="Highest Score"
            value={highestScore}
            sub="top performer"
            color="bg-emerald-500"
          />
        </div>

        {/* ── Table card ── */}
        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">

          {/* Search bar */}
          <div className="p-4 border-b border-gray-100 flex items-center gap-3">
            <Search size={16} className="text-gray-400 flex-shrink-0" />
            <input
              type="text"
              placeholder="Search by name or job title…"
              value={search}
              onChange={e => setSearch(e.target.value)}
              className="w-full text-sm outline-none text-gray-700 placeholder-gray-400"
            />
            {search && (
              <button
                onClick={() => setSearch('')}
                className="text-xs text-gray-400 hover:text-gray-600 flex-shrink-0"
              >
                Clear
              </button>
            )}
          </div>

          {filtered.length === 0 ? (
            <div className="py-16 text-center text-gray-400">
              <Users size={36} className="mx-auto mb-3 opacity-40" />
              <p className="text-sm">{search ? 'No candidates match your search.' : 'No candidates evaluated yet.'}</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-gray-50 border-b border-gray-100">
                  <tr>
                    <TH field="candidate_name" label="Candidate" />
                    <TH field="job_title"       label="Role" />
                    <TH field="overall_score"   label="Overall" />
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide">
                      Breakdown
                    </th>
                    <TH field="created_at" label="Date" className="hidden md:table-cell" />
                    <th className="px-4 py-3 text-right text-xs font-semibold text-gray-500 uppercase tracking-wide">
                      Actions
                    </th>
                  </tr>
                </thead>

                <tbody className="divide-y divide-gray-50">
                  {filtered.map(c => {
                    const badge = getBadge(clamp(c.overall_score))
                    const date  = new Date(c.created_at).toLocaleDateString('en-GB', {
                      day: '2-digit', month: 'short', year: 'numeric',
                    })
                    return (
                      <tr key={c.id} className="hover:bg-gray-50 transition-colors">

                        {/* Candidate */}
                        <td className="px-4 py-3.5">
                          <p className="font-medium text-gray-900">{c.candidate_name}</p>
                        </td>

                        {/* Role */}
                        <td className="px-4 py-3.5">
                          <span className="flex items-center gap-1.5 text-gray-600">
                            <Briefcase size={13} className="text-gray-400 flex-shrink-0" />
                            {c.job_title}
                          </span>
                        </td>

                        {/* Overall score */}
                        <td className="px-4 py-3.5">
                          <div className="flex items-center gap-2">
                            <span className="text-base font-bold text-gray-900">
                              {clamp(c.overall_score).toFixed(1)}
                            </span>
                            <span className={`px-2 py-0.5 text-xs font-semibold rounded-full border ${badge.light} ${badge.text} ${badge.border}`}>
                              {badge.label}
                            </span>
                          </div>
                        </td>

                        {/* Score breakdown mini-bars */}
                        <td className="px-4 py-3.5">
                          <div className="space-y-1.5 min-w-[160px]">
                            <div className="flex items-center gap-2">
                              <Cpu size={11} className="text-indigo-400 flex-shrink-0" />
                              <ScorePill value={c.technical_score} />
                            </div>
                            <div className="flex items-center gap-2">
                              <FileSearch size={11} className="text-pink-400 flex-shrink-0" />
                              <ScorePill value={c.ats_score} />
                            </div>
                            <div className="flex items-center gap-2">
                              <MessageSquare size={11} className="text-amber-400 flex-shrink-0" />
                              <ScorePill value={c.communication_score} />
                            </div>
                          </div>
                        </td>

                        {/* Date */}
                        <td className="px-4 py-3.5 text-gray-500 hidden md:table-cell whitespace-nowrap">
                          {date}
                        </td>

                        {/* Actions */}
                        <td className="px-4 py-3.5">
                          <div className="flex items-center justify-end gap-2">
                            <button
                              onClick={() => handleView(c)}
                              className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-indigo-700 bg-indigo-50 border border-indigo-200 rounded-full hover:bg-indigo-100 transition-colors"
                            >
                              <Eye size={12} /> View
                            </button>

                            {c.report_url ? (
                              <a
                                href={`http://localhost:8000${c.report_url}`}
                                target="_blank"
                                rel="noreferrer"
                                className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-emerald-700 bg-emerald-50 border border-emerald-200 rounded-full hover:bg-emerald-100 transition-colors"
                              >
                                <Download size={12} /> PDF
                              </a>
                            ) : (
                              <span className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-gray-400 bg-gray-50 border border-gray-200 rounded-full cursor-not-allowed">
                                <Download size={12} /> PDF
                              </span>
                            )}
                          </div>
                        </td>

                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          )}

          {/* Row count footer */}
          {filtered.length > 0 && (
            <div className="px-4 py-3 border-t border-gray-100 text-xs text-gray-400">
              Showing {filtered.length} of {totalCandidates} candidate{totalCandidates !== 1 ? 's' : ''}
            </div>
          )}
        </div>

      </div>
    </div>
  )
}