import React, { useState, useEffect } from 'react'
import {
  Loader, AlertCircle, ArrowLeft
} from 'lucide-react'
import {
  BarChart, Bar, RadarChart, Radar, PolarGrid,
  PolarAngleAxis, PolarRadiusAxis, XAxis, YAxis,
  CartesianGrid, Tooltip, ResponsiveContainer
} from 'recharts'
import { useLocation, Link } from "react-router-dom"

export default function EvaluationPage() {

  const location = useLocation()
  const passedData = location.state

  const [evaluation, setEvaluation] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    console.log("LOCATION STATE:", passedData)

    if (passedData) {
      setEvaluation(passedData)
      setLoading(false)
      return
    }

    const lastData = localStorage.getItem("evaluation")
    if (lastData) {
      setEvaluation(JSON.parse(lastData))
      setLoading(false)
      return
    }

    setError("No evaluation data found. Please upload again.")
    setLoading(false)
  }, [passedData])

  useEffect(() => {
    if (passedData) {
      localStorage.setItem("evaluation", JSON.stringify(passedData))
    }
  }, [passedData])

  // ---------- STATES ----------
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader className="h-10 w-10 animate-spin text-blue-600" />
      </div>
    )
  }

  if (error || !evaluation) {
    return (
      <div className="p-10 text-center">
        <AlertCircle className="mx-auto mb-4 text-red-500" size={40} />
        <h2 className="text-lg font-semibold mb-2">Something went wrong</h2>
        <p className="text-gray-600 mb-4">{error}</p>
        <Link to="/candidate" className="px-4 py-2 bg-blue-600 text-white rounded">
          Go Back
        </Link>
      </div>
    )
  }

  console.log(JSON.stringify(evaluation, null, 2))

  // ---------- FIXED: use correct API field names ----------
  // API returns: score, skills, missing_skills, feedback, soft_skill_index
  const overallScore = evaluation.score ?? evaluation.overall_score ?? 0

  const scoreData = [
    { name: 'Technical', score: overallScore },
    {
      name: 'Soft Skills',
      score: evaluation.soft_skill_index
        ? (Object.values(evaluation.soft_skill_index).reduce((a, b) => a + b, 0) /
            Object.values(evaluation.soft_skill_index).length) * 100
        : 0
    },
    { name: 'Video', score: evaluation.video_score ?? 0 },
    { name: 'Overall', score: overallScore }
  ]

  const softSkillData = evaluation.soft_skill_index ? [
    { skill: 'Communication', value: evaluation.soft_skill_index.communication * 100 },
    { skill: 'Confidence', value: evaluation.soft_skill_index.confidence * 100 },
    { skill: 'Engagement', value: evaluation.soft_skill_index.engagement * 100 },
    { skill: 'Professionalism', value: evaluation.soft_skill_index.professionalism * 100 }
  ] : []

  const getScoreBadge = (score) => {
    if (score >= 80) return { text: 'Excellent', color: 'bg-green-500' }
    if (score >= 60) return { text: 'Good', color: 'bg-yellow-500' }
    return { text: 'Needs Work', color: 'bg-red-500' }
  }

  const badge = getScoreBadge(overallScore)

  // FIXED: API uses "skills" for matched skills (not "skills_matched")
  const matchedSkills = evaluation.skills ?? evaluation.skills_matched ?? []
  const missingSkills = evaluation.missing_skills ?? []

  // ---------- UI ----------
  return (
    <div className="max-w-6xl mx-auto p-6">

      {/* HEADER */}
      <div className="mb-6 flex justify-between items-center">
        <Link to="/candidate" className="flex items-center text-blue-600">
          <ArrowLeft className="mr-2" size={16} /> Back
        </Link>
        <div className={`px-4 py-2 text-white rounded ${badge.color}`}>
          {badge.text}
        </div>
      </div>

      <h1 className="text-3xl font-bold mb-2">
        {evaluation.candidate_name || "Candidate"}
      </h1>

      <p className="text-gray-600 mb-6">
        Overall Score: <strong>{overallScore.toFixed(1)}/100</strong>
      </p>

      {/* CHARTS */}
      <div className="grid md:grid-cols-2 gap-6">

        {/* BAR CHART */}
        <div className="bg-white p-4 rounded shadow">
          <h2 className="mb-3 font-semibold">Score Breakdown</h2>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={scoreData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis domain={[0, 100]} />
              <Tooltip formatter={(value) => `${value.toFixed(1)}`} />
              <Bar dataKey="score" fill="#3b82f6" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* RADAR CHART */}
        {softSkillData.length > 0 && (
          <div className="bg-white p-4 rounded shadow">
            <h2 className="mb-3 font-semibold">Soft Skills</h2>
            <ResponsiveContainer width="100%" height={250}>
              <RadarChart data={softSkillData}>
                <PolarGrid />
                <PolarAngleAxis dataKey="skill" />
                <PolarRadiusAxis domain={[0, 100]} />
                <Radar dataKey="value" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.6} />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        )}

      </div>

      {/* SKILL ANALYSIS */}
      <div className="mt-8 bg-white p-4 rounded shadow">
        <h2 className="font-semibold mb-4">Skill Analysis</h2>

        <div className="grid md:grid-cols-2 gap-4">

          {/* MATCHED SKILLS — API field: "skills" */}
          <div>
            <h3 className="text-green-600 font-medium mb-2">Matched Skills</h3>
            {matchedSkills.length > 0 ? (
              matchedSkills.map((s, i) => (
                <span key={i} className="inline-block bg-green-100 px-2 py-1 mr-2 mb-2 rounded">
                  {s}
                </span>
              ))
            ) : (
              <p className="text-gray-500">No matched skills</p>
            )}
          </div>

          {/* MISSING SKILLS — API field: "missing_skills" */}
          <div>
            <h3 className="text-red-600 font-medium mb-2">Missing Skills</h3>
            {missingSkills.length > 0 ? (
              missingSkills.map((s, i) => (
                <span key={i} className="inline-block bg-red-100 px-2 py-1 mr-2 mb-2 rounded">
                  {s}
                </span>
              ))
            ) : (
              <p className="text-gray-500">No missing skills</p>
            )}
          </div>

        </div>

        {/* FEEDBACK */}
        <div className="mt-4">
          <h3 className="font-medium mb-2">Feedback</h3>
          <p className="text-gray-700">
            {evaluation.feedback || "No feedback available"}
          </p>
        </div>

      </div>
    </div>
  )
}
