import React, { useState } from 'react'
import {
  ArrowLeft, Sparkles, Clock, ListChecks, Gauge,
  Coffee, Flame, Skull, CheckCircle2, Lightbulb,
  Mic, Eye, MessageSquare, Play
} from 'lucide-react'
import { useLocation, useNavigate, Link } from 'react-router-dom'

// ── Static config ────────────────────────────────────────────────────────────
// Kept outside the component so it isn't recreated on every render.

const DIFFICULTIES = [
  {
    id: 'easy',
    label: 'Easy',
    tagline: 'Warm up the mic',
    icon: Coffee,
    accent: 'emerald',
    duration: '10–15 min',
    questionCount: '4–5 questions',
    description: 'Foundational questions about your background and the role. Generous follow-up time, gentle pacing.',
    traits: ['Conversational pace', 'Basic role-fit questions', 'No surprise follow-ups'],
  },
  {
    id: 'moderate',
    label: 'Moderate',
    tagline: 'The real dry run',
    icon: Flame,
    accent: 'amber',
    duration: '15–20 min',
    questionCount: '6–7 questions',
    description: 'A balanced mix of behavioral and technical questions, similar to a first-round screen with a hiring manager.',
    traits: ['Behavioral + technical mix', 'Natural follow-up questions', 'Realistic time pressure'],
  },
  {
    id: 'hard',
    label: 'Hard',
    tagline: 'No mercy mode',
    icon: Skull,
    accent: 'rose',
    duration: '20–30 min',
    questionCount: '8–10 questions',
    description: 'Rapid-fire, panel-style pacing with pointed follow-ups and curveballs — built to stress-test your answers.',
    traits: ['Pointed, layered follow-ups', 'Curveball scenario questions', 'Panel-style pacing'],
  },
]

const PREP_TIPS = [
  { icon: Mic,           text: 'Test your microphone and find a quiet room before you start the clock.' },
  { icon: Eye,           text: 'Keep your eyes on the camera, not the script — it reads as confidence.' },
  { icon: MessageSquare, text: 'Structure answers with a quick setup, then the action you took, then the result.' },
]

const ACCENTS = {
  emerald: {
    ring: 'ring-emerald-500',
    border: 'border-emerald-200',
    borderSelected: 'border-emerald-500',
    bg: 'bg-emerald-50',
    text: 'text-emerald-700',
    iconBg: 'bg-emerald-100',
    iconText: 'text-emerald-600',
    dot: 'bg-emerald-500',
    chip: 'bg-emerald-50 text-emerald-700 border-emerald-200',
  },
  amber: {
    ring: 'ring-amber-500',
    border: 'border-amber-200',
    borderSelected: 'border-amber-500',
    bg: 'bg-amber-50',
    text: 'text-amber-700',
    iconBg: 'bg-amber-100',
    iconText: 'text-amber-600',
    dot: 'bg-amber-500',
    chip: 'bg-amber-50 text-amber-700 border-amber-200',
  },
  rose: {
    ring: 'ring-rose-500',
    border: 'border-rose-200',
    borderSelected: 'border-rose-500',
    bg: 'bg-rose-50',
    text: 'text-rose-700',
    iconBg: 'bg-rose-100',
    iconText: 'text-rose-600',
    dot: 'bg-rose-500',
    chip: 'bg-rose-50 text-rose-700 border-rose-200',
  },
}

// ── Page ─────────────────────────────────────────────────────────────────────

export default function InterviewSetup() {
  const location = useLocation()
  const navigate = useNavigate()
  const passedData = location.state || {}

  const candidateName = passedData.candidateName || passedData.evaluation?.candidate_name || null
  const jobTitle       = passedData.jobTitle || passedData.evaluation?.job_title || null
  const overallScore   = passedData.evaluation?.match_percentage ?? passedData.evaluation?.overall_score ?? null

  const [selectedId, setSelectedId] = useState('moderate')
  const selected = DIFFICULTIES.find(d => d.id === selectedId)
  const accent = ACCENTS[selected.accent]

  const handleStart = () => {
    navigate('/interview', {
      state: {
        ...passedData,
        difficulty: selectedId,
      },
    })
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-5xl mx-auto px-4 py-8 space-y-6">

        {/* ── Top bar ── */}
        <div className="flex justify-between items-center">
          <Link
            to="/evaluation"
            className="flex items-center gap-1.5 text-indigo-600 hover:text-indigo-800 font-medium text-sm"
          >
            <ArrowLeft size={16} /> Back
          </Link>
        </div>

        {/* ── Hero ── */}
        <div className="relative overflow-hidden bg-gradient-to-br from-violet-600 to-indigo-600 rounded-2xl shadow-sm p-8 sm:p-10 text-white">
          <div className="absolute -right-10 -top-10 w-56 h-56 rounded-full bg-white/10 blur-2xl" />
          <div className="absolute -left-16 bottom-0 w-72 h-72 rounded-full bg-white/5 blur-3xl" />
          <div className="relative">
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-white/15 text-xs font-semibold mb-4 backdrop-blur-sm">
              <Sparkles size={13} /> AI Mock Interview
            </div>
            <h1 className="text-2xl sm:text-3xl font-bold mb-2">
              Ready for a practice round{candidateName ? `, ${candidateName}` : ''}?
            </h1>
            <p className="text-indigo-100 text-sm sm:text-base max-w-xl">
              {jobTitle
                ? `Run a simulated interview for the ${jobTitle} role, tailored to the gaps from your evaluation.`
                : 'Run a simulated interview tailored to the gaps and strengths from your evaluation.'}
            </p>
          </div>
        </div>

        {/* ── Difficulty selection ── */}
        <div>
          <h2 className="font-semibold text-gray-800 mb-1">Choose your difficulty</h2>
          <p className="text-sm text-gray-500 mb-4">You can always run another round at a different level afterward.</p>

          <div className="grid sm:grid-cols-3 gap-4">
            {DIFFICULTIES.map(d => {
              const a = ACCENTS[d.accent]
              const isSelected = d.id === selectedId
              const Icon = d.icon
              return (
                <button
                  key={d.id}
                  type="button"
                  onClick={() => setSelectedId(d.id)}
                  aria-pressed={isSelected}
                  className={`text-left bg-white rounded-2xl border-2 p-5 shadow-sm transition-all focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 ${a.ring} ${
                    isSelected ? `${a.borderSelected} shadow-md` : 'border-gray-100 hover:border-gray-200'
                  }`}
                >
                  <div className="flex items-center justify-between mb-3">
                    <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${a.iconBg}`}>
                      <Icon size={18} className={a.iconText} />
                    </div>
                    {isSelected && <CheckCircle2 size={18} className={a.iconText} />}
                  </div>

                  <h3 className="font-semibold text-gray-900">{d.label}</h3>
                  <p className={`text-xs font-medium mb-3 ${a.text}`}>{d.tagline}</p>

                  <p className="text-sm text-gray-600 leading-relaxed mb-4">{d.description}</p>

                  <div className="flex flex-wrap gap-1.5 mb-4">
                    <span className={`inline-flex items-center gap-1 text-xs px-2 py-1 rounded-full border font-medium ${a.chip}`}>
                      <Clock size={11} /> {d.duration}
                    </span>
                    <span className={`inline-flex items-center gap-1 text-xs px-2 py-1 rounded-full border font-medium ${a.chip}`}>
                      <ListChecks size={11} /> {d.questionCount}
                    </span>
                  </div>

                  <ul className="space-y-1.5">
                    {d.traits.map((t, i) => (
                      <li key={i} className="flex items-start gap-1.5 text-xs text-gray-500">
                        <span className={`mt-1 w-1 h-1 rounded-full flex-shrink-0 ${a.dot}`} />
                        {t}
                      </li>
                    ))}
                  </ul>
                </button>
              )
            })}
          </div>
        </div>

        {/* ── Summary + tips ── */}
        <div className="grid md:grid-cols-2 gap-4">

          {/* Interview summary card */}
          <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-5">
            <h2 className="font-semibold text-gray-800 mb-4 flex items-center gap-2">
              <Gauge size={16} className="text-indigo-500" /> Interview Summary
            </h2>

            <dl className="space-y-3">
              <div className="flex items-center justify-between text-sm">
                <dt className="text-gray-500">Difficulty</dt>
                <dd className={`inline-flex items-center gap-1.5 font-semibold ${accent.text}`}>
                  <span className={`w-2 h-2 rounded-full ${accent.dot}`} />
                  {selected.label}
                </dd>
              </div>
              <div className="flex items-center justify-between text-sm">
                <dt className="text-gray-500">Estimated length</dt>
                <dd className="font-semibold text-gray-800">{selected.duration}</dd>
              </div>
              <div className="flex items-center justify-between text-sm">
                <dt className="text-gray-500">Question count</dt>
                <dd className="font-semibold text-gray-800">{selected.questionCount}</dd>
              </div>
              {jobTitle && (
                <div className="flex items-center justify-between text-sm">
                  <dt className="text-gray-500">Target role</dt>
                  <dd className="font-semibold text-gray-800 text-right">{jobTitle}</dd>
                </div>
              )}
              {overallScore !== null && (
                <div className="flex items-center justify-between text-sm">
                  <dt className="text-gray-500">Last evaluation score</dt>
                  <dd className="font-semibold text-gray-800">{Number(overallScore).toFixed(0)} / 100</dd>
                </div>
              )}
            </dl>

            <div className={`mt-4 rounded-xl p-3 text-xs leading-relaxed ${accent.bg} ${accent.text}`}>
              Questions will lean on the gaps and strengths identified in your last evaluation, when available.
            </div>
          </div>

          {/* Preparation tips */}
          <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-5">
            <h2 className="font-semibold text-gray-800 mb-4 flex items-center gap-2">
              <Lightbulb size={16} className="text-indigo-500" /> Preparation Tips
            </h2>
            <ul className="space-y-3">
              {PREP_TIPS.map((tip, i) => {
                const TipIcon = tip.icon
                return (
                  <li key={i} className="flex items-start gap-3">
                    <div className="w-7 h-7 rounded-lg bg-indigo-50 flex items-center justify-center flex-shrink-0 mt-0.5">
                      <TipIcon size={13} className="text-indigo-600" />
                    </div>
                    <p className="text-sm text-gray-600 leading-relaxed">{tip.text}</p>
                  </li>
                )
              })}
            </ul>
          </div>
        </div>

        {/* ── Actions ── */}
        <div className="flex justify-between items-center pt-2">
          <Link
            to="/evaluation"
            className="px-5 py-2.5 text-sm font-medium text-gray-600 hover:text-gray-800 transition-colors"
          >
            Back
          </Link>

          <button
            type="button"
            onClick={handleStart}
            className="flex items-center gap-2 px-6 py-2.5 text-sm font-semibold text-white bg-gradient-to-r from-violet-600 to-indigo-600 rounded-full shadow hover:from-violet-700 hover:to-indigo-700 transition-all"
          >
            <Play size={15} />
            Start Interview
          </button>
        </div>

      </div>
    </div>
  )
}