import axios from 'axios'

const API_BASE_URL = '/api/v1'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const uploadVideo = async (file, candidateName) => {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('candidate_name', candidateName)
  
  const response = await api.post('/upload/video', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  
  return response.data
}

export const uploadResume = async (file, candidateName) => {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('candidate_name', candidateName)
  
  const response = await api.post('/upload/resume', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  
  return response.data
}

export const evaluateCandidate = async (evaluationData) => {
  const response = await api.post('/evaluate', evaluationData)
  return response.data
}

export const getEvaluation = async (evaluationId) => {
  const response = await api.get(`/evaluation/${evaluationId}`)
  return response.data
}

export const generateFeedback = async (evaluationId, jobTitle) => {
  const response = await api.post(`/feedback/${evaluationId}?job_title=${encodeURIComponent(jobTitle)}`)
  return response.data
}

export const listEvaluations = async (limit = 10) => {
  const response = await api.get(`/evaluations?limit=${limit}`)
  return response.data
}

export const healthCheck = async () => {
  const response = await api.get('/health')
  return response.data
}

// Job Posting APIs
export const createJobPosting = async (jobData) => {
  const response = await api.post('/jobs', jobData)
  return response.data
}

export const listJobPostings = async (status = 'active', limit = 50) => {
  const response = await api.get('/jobs', {
    params: { status, limit }
  })
  return response.data
}

export const getJobPosting = async (jobId) => {
  const response = await api.get(`/jobs/${jobId}`)
  return response.data
}

export const updateJobPosting = async (jobId, updates) => {
  const response = await api.put(`/jobs/${jobId}`, updates)
  return response.data
}

export const deleteJobPosting = async (jobId) => {
  const response = await api.delete(`/jobs/${jobId}`)
  return response.data
}

export const checkVideoQuality = async (videoFile) => {
  try {
    const formData = new FormData();
    formData.append('file', videoFile);
    
    const response = await api.post('/check-video-quality', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    console.error('Error checking video quality:', error);
    throw error;
  }
};

// Submission History & Improvement Tracking
export const getSubmissionHistory = async (candidateName, jobId) => {
  const response = await api.get(`/submission-history/${encodeURIComponent(candidateName)}/${jobId}`)
  return response.data
}

export const compareSubmissions = async (currentId, previousId) => {
  const response = await api.get(`/compare-submissions/${currentId}/${previousId}`)
  return response.data
}

export const getLatestSubmission = async (candidateName, jobId) => {
  const response = await api.get(`/latest-submission/${encodeURIComponent(candidateName)}/${jobId}`)
  return response.data
}

export default api
