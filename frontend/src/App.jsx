import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import HomePage from './pages/HomePage'
import CandidatePage from './pages/CandidatePage'
import RecruiterDashboard from './pages/RecruiterDashboard'
import EvaluationPage from './pages/EvaluationPage'
import InterviewSetup from "./pages/InterviewSetup";

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/candidate" element={<CandidatePage />} />
          <Route path="/recruiter" element={<RecruiterDashboard />} />
          <Route path="/evaluation" element={<EvaluationPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
          <Route
    path="/interview/setup"
    element={<InterviewSetup />}
/>
        </Routes>
      </Layout>
    </Router>
  )
}

export default App
