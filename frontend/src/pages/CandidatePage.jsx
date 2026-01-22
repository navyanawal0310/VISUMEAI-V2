import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Upload, FileText, Video, Loader, CheckCircle, AlertCircle, Briefcase } from 'lucide-react'
import { useDropzone } from 'react-dropzone'
import { uploadVideo, uploadResume, evaluateCandidate, listJobPostings, checkVideoQuality, getLatestSubmission } from '../services/api'

export default function CandidatePage() {
  const navigate = useNavigate()
  const [formData, setFormData] = useState({
    candidateName: '',
    selectedJobId: ''
  })
  const [jobPostings, setJobPostings] = useState([])
  const [loadingJobs, setLoadingJobs] = useState(true)
  const [videoFile, setVideoFile] = useState(null)
  const [resumeFile, setResumeFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(null)
  const [videoQualityCheck, setVideoQualityCheck] = useState(null)
  const [checkingQuality, setCheckingQuality] = useState(false)
  const [previousSubmission, setPreviousSubmission] = useState(null)
  const [checkingPrevious, setCheckingPrevious] = useState(false)
  
  // Load available job postings
  useEffect(() => {
    loadJobPostings()
  }, [])
  
  // Check for previous submissions when candidate name and job are selected
  useEffect(() => {
    if (formData.candidateName && formData.selectedJobId) {
      checkForPreviousSubmissions()
    } else {
      setPreviousSubmission(null)
    }
  }, [formData.candidateName, formData.selectedJobId])
  
  const loadJobPostings = async () => {
    try {
      const jobs = await listJobPostings('active', 50)
      setJobPostings(jobs)
    } catch (err) {
      console.error('Failed to load job postings:', err)
      setError('Failed to load available positions. Please refresh the page.')
    } finally {
      setLoadingJobs(false)
    }
  }
  
  const checkForPreviousSubmissions = async () => {
    setCheckingPrevious(true)
    try {
      const latest = await getLatestSubmission(formData.candidateName, formData.selectedJobId)
      setPreviousSubmission(latest)
    } catch (err) {
      // No previous submission found - that's okay
      setPreviousSubmission(null)
    } finally {
      setCheckingPrevious(false)
    }
  }
  
  const selectedJob = jobPostings.find(job => job.job_id === formData.selectedJobId)
  
  const videoDropzone = useDropzone({
    accept: {
      'video/*': ['.mp4', '.avi', '.mov', '.webm']
    },
    maxFiles: 1,
    onDrop: (acceptedFiles) => {
      if (acceptedFiles.length > 0) {
        setVideoFile(acceptedFiles[0])
        setError(null)
      }
    }
  })
  
  const resumeDropzone = useDropzone({
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx']
    },
    maxFiles: 1,
    onDrop: (acceptedFiles) => {
      if (acceptedFiles.length > 0) {
        setResumeFile(acceptedFiles[0])
        setError(null)
      }
    }
  })
  
  const handleInputChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleVideoQualityCheck = async (file) => {
    setCheckingQuality(true)
    setVideoQualityCheck(null)
    
    try {
      const result = await checkVideoQuality(file)
      setVideoQualityCheck(result)
    } catch (err) {
      setError('Failed to check video quality: ' + err.message)
    } finally {
      setCheckingQuality(false)
    }
  }
  
  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)
    setSuccess(null)
    
    // Validation
    if (!formData.candidateName) {
      setError('Please enter your name')
      return
    }
    
    if (!formData.selectedJobId) {
      setError('Please select a position')
      return
    }
    
    if (!videoFile && !resumeFile) {
      setError('Please upload at least a video or resume')
      return
    }
    
    setLoading(true)
    
    try {
      let videoId = null
      let resumeId = null
      
      // Upload video
      if (videoFile) {
        const videoResponse = await uploadVideo(videoFile, formData.candidateName)
        videoId = videoResponse.video_id
      }
      
      // Upload resume
      if (resumeFile) {
        const resumeResponse = await uploadResume(resumeFile, formData.candidateName)
        resumeId = resumeResponse.resume_id
      }
      
      // Start evaluation using job_id
      const evaluation = await evaluateCandidate({
        video_id: videoId,
        resume_id: resumeId,
        candidate_name: formData.candidateName,
        job_id: formData.selectedJobId
      })
      
      setSuccess('Evaluation complete!')
      
      // Navigate to results
      setTimeout(() => {
        navigate(`/evaluation/${evaluation.evaluation_id}`)
      }, 1500)
      
    } catch (err) {
      console.error('Submission error:', err)
      setError(err.response?.data?.detail || 'Failed to process submission. Please try again.')
    } finally {
      setLoading(false)
    }
  }
  
  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-2">
          Submit Your Video Resume
        </h1>
        <p className="text-lg text-gray-600">
          Upload your video resume and/or text resume to receive AI-powered feedback
        </p>
      </div>
      
      {error && (
        <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4 flex items-start">
          <AlertCircle className="h-5 w-5 text-red-600 mt-0.5 mr-3 flex-shrink-0" />
          <p className="text-red-800">{error}</p>
        </div>
      )}
      
      {success && (
        <div className="mb-6 bg-green-50 border border-green-200 rounded-lg p-4 flex items-start">
          <CheckCircle className="h-5 w-5 text-green-600 mt-0.5 mr-3 flex-shrink-0" />
          <p className="text-green-800">{success}</p>
        </div>
      )}
      
      <form onSubmit={handleSubmit} className="bg-white rounded-xl shadow-sm border border-gray-200 p-8">
        {/* Personal Information */}
        <div className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">Personal Information</h2>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Full Name *
              </label>
              <input
                type="text"
                name="candidateName"
                value={formData.candidateName}
                onChange={handleInputChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                placeholder="John Doe"
                required
              />
            </div>
          </div>
        </div>
        
        {/* Previous Submission Notification */}
        {checkingPrevious && (
          <div className="mb-8 bg-blue-50 border border-blue-200 rounded-lg p-4 flex items-center gap-3">
            <Loader className="h-5 w-5 animate-spin text-blue-600" />
            <p className="text-blue-800">Checking for previous submissions...</p>
          </div>
        )}
        
        {previousSubmission && (
          <div className="mb-8 bg-gradient-to-r from-purple-50 to-cyan-50 border-2 border-purple-200 rounded-xl p-6 shadow-lg">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-3">
                  <div className="w-12 h-12 rounded-full bg-gradient-to-br from-purple-500 to-cyan-500 flex items-center justify-center text-white font-bold text-lg shadow-lg">
                    {previousSubmission.version}
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-gray-900">
                      Previous Submission Found!
                    </h3>
                    <p className="text-sm text-gray-600">
                      You submitted for this position before
                    </p>
                  </div>
                </div>
                
                <div className="grid grid-cols-2 gap-4 mt-4">
                  <div className="bg-white rounded-lg p-4 border border-purple-200">
                    <p className="text-xs text-gray-600 mb-1">Previous Score</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {previousSubmission.score.toFixed(1)}
                      <span className="text-sm text-gray-500">/100</span>
                    </p>
                  </div>
                  <div className="bg-white rounded-lg p-4 border border-cyan-200">
                    <p className="text-xs text-gray-600 mb-1">Recommendation</p>
                    <p className="text-sm font-semibold text-gray-900">
                      {previousSubmission.recommendation}
                    </p>
                  </div>
                </div>
                
                <div className="mt-4 p-4 bg-white rounded-lg border border-purple-200">
                  <p className="text-sm text-purple-900 font-medium mb-2">
                    💡 This is your <span className="font-bold">attempt #{previousSubmission.version + 1}</span>
                  </p>
                  <p className="text-sm text-gray-700">
                    Your new submission will be compared with your previous one, and you'll see a detailed 
                    improvement analysis showing exactly what got better and what needs work!
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}
        
        {/* Job Selection */}
        <div className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">Select Position</h2>
          
          {loadingJobs ? (
            <div className="flex items-center justify-center py-8">
              <Loader className="h-8 w-8 animate-spin text-primary-600" />
              <span className="ml-3 text-gray-600">Loading available positions...</span>
            </div>
          ) : jobPostings.length === 0 ? (
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <p className="text-yellow-800">
                No active job postings available at the moment. Please check back later.
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Available Positions *
                </label>
                <div className="relative">
                  <Briefcase className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                  <select
                    name="selectedJobId"
                    value={formData.selectedJobId}
                    onChange={handleInputChange}
                    className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 appearance-none bg-white"
                    required
                  >
                    <option value="">-- Select a position to apply for --</option>
                    {jobPostings.map(job => (
                      <option key={job.job_id} value={job.job_id}>
                        {job.title} {job.experience_years && `(${job.experience_years}+ years)`}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
              
              {/* Show selected job details */}
              {selectedJob && (
                <div className="mt-4 p-6 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg border border-blue-200">
                  <div className="flex items-start justify-between mb-3">
                    <h3 className="text-xl font-semibold text-gray-900">{selectedJob.title}</h3>
                    <span className="px-3 py-1 bg-green-100 text-green-800 text-xs font-medium rounded-full">
                      Active
                    </span>
                  </div>
                  
                  <p className="text-sm text-gray-700 mb-4 whitespace-pre-line">
                    {selectedJob.description}
                  </p>
                  
                  {selectedJob.required_skills.length > 0 && (
                    <div className="mb-3">
                      <p className="text-sm font-semibold text-gray-700 mb-2">Required Skills:</p>
                      <div className="flex flex-wrap gap-2">
                        {selectedJob.required_skills.map(skill => (
                          <span key={skill} className="px-3 py-1 bg-blue-200 text-blue-900 text-xs font-medium rounded-full">
                            {skill}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  {selectedJob.preferred_skills && selectedJob.preferred_skills.length > 0 && (
                    <div className="mb-3">
                      <p className="text-sm font-semibold text-gray-700 mb-2">Preferred Skills:</p>
                      <div className="flex flex-wrap gap-2">
                        {selectedJob.preferred_skills.map(skill => (
                          <span key={skill} className="px-3 py-1 bg-indigo-100 text-indigo-800 text-xs font-medium rounded-full">
                            {skill}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  {selectedJob.experience_years && (
                    <p className="text-sm text-gray-600 mt-2">
                      <strong>Required Experience:</strong> {selectedJob.experience_years}+ years
                    </p>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
        
        {/* File Uploads */}
        <div className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">Upload Files</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Video Upload */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Video Resume
              </label>
              <div
                {...videoDropzone.getRootProps()}
                className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors ${
                  videoDropzone.isDragActive
                    ? 'border-primary-500 bg-primary-50'
                    : 'border-gray-300 hover:border-primary-400'
                }`}
              >
                <input {...videoDropzone.getInputProps()} />
                <Video className="h-12 w-12 mx-auto text-gray-400 mb-3" />
                {videoFile ? (
                  <div>
                    <p className="text-sm font-medium text-green-600">{videoFile.name}</p>
                    <p className="text-xs text-gray-500 mt-1">
                      {(videoFile.size / (1024 * 1024)).toFixed(2)} MB
                    </p>
                  </div>
                ) : (
                  <div>
                    <p className="text-sm text-gray-600">Drop video here or click to browse</p>
                    <p className="text-xs text-gray-500 mt-1">MP4, AVI, MOV, WEBM (max 100MB)</p>
                  </div>
                )}
              </div>
              
              {/* Video Quality Check */}
              {videoFile && (
                <div className="mt-4">
                  <button
                    type="button"
                    onClick={() => handleVideoQualityCheck(videoFile)}
                    disabled={checkingQuality}
                    className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
                  >
                    {checkingQuality ? (
                      <>
                        <Loader className="h-4 w-4 animate-spin mr-2" />
                        Checking Quality...
                      </>
                    ) : (
                      <>
                        <CheckCircle className="h-4 w-4 mr-2" />
                        Check Video Quality
                      </>
                    )}
                  </button>
                  
                  {videoQualityCheck && (
                    <div className="mt-4 p-4 rounded-lg border">
                      <h4 className="font-semibold mb-3 flex items-center">
                        {videoQualityCheck.can_proceed ? (
                          <CheckCircle className="h-5 w-5 text-green-600 mr-2" />
                        ) : (
                          <AlertCircle className="h-5 w-5 text-red-600 mr-2" />
                        )}
                        Video Quality Check
                      </h4>
                      
                      {videoQualityCheck.issues.length > 0 && (
                        <div className="mb-3">
                          <h5 className="font-medium text-red-900 mb-2">Issues Found:</h5>
                          <ul className="list-disc list-inside text-sm text-red-700 space-y-1">
                            {videoQualityCheck.issues.map((issue, index) => (
                              <li key={index}>{issue}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                      
                      {videoQualityCheck.warnings.length > 0 && (
                        <div className="mb-3">
                          <h5 className="font-medium text-yellow-900 mb-2">Warnings:</h5>
                          <ul className="list-disc list-inside text-sm text-yellow-700 space-y-1">
                            {videoQualityCheck.warnings.map((warning, index) => (
                              <li key={index}>{warning}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                      
                      {videoQualityCheck.recommendations.length > 0 && (
                        <div className="mb-3">
                          <h5 className="font-medium text-blue-900 mb-2">Recommendations:</h5>
                          <ul className="list-disc list-inside text-sm text-blue-700 space-y-1">
                            {videoQualityCheck.recommendations.map((rec, index) => (
                              <li key={index}>{rec}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                      
                      {videoQualityCheck.video_stats && (
                        <div className="text-xs text-gray-600 bg-gray-50 p-2 rounded">
                          <strong>Video Stats:</strong> {videoQualityCheck.video_stats.resolution}, {videoQualityCheck.video_stats.fps}fps, {videoQualityCheck.video_stats.duration}s
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}
            </div>
            
            {/* Resume Upload */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Text Resume
              </label>
              <div
                {...resumeDropzone.getRootProps()}
                className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors ${
                  resumeDropzone.isDragActive
                    ? 'border-primary-500 bg-primary-50'
                    : 'border-gray-300 hover:border-primary-400'
                }`}
              >
                <input {...resumeDropzone.getInputProps()} />
                <FileText className="h-12 w-12 mx-auto text-gray-400 mb-3" />
                {resumeFile ? (
                  <div>
                    <p className="text-sm font-medium text-green-600">{resumeFile.name}</p>
                    <p className="text-xs text-gray-500 mt-1">
                      {(resumeFile.size / 1024).toFixed(2)} KB
                    </p>
                  </div>
                ) : (
                  <div>
                    <p className="text-sm text-gray-600">Drop resume here or click to browse</p>
                    <p className="text-xs text-gray-500 mt-1">PDF or DOCX</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
        
        {/* Submit Button */}
        <div className="flex justify-end">
          <button
            type="submit"
            disabled={loading || loadingJobs || !formData.selectedJobId}
            className="inline-flex items-center px-8 py-3 border border-transparent text-base font-medium rounded-lg text-white bg-primary-600 hover:bg-primary-700 disabled:bg-gray-400 disabled:cursor-not-allowed shadow-lg transition-all"
          >
            {loading ? (
              <>
                <Loader className="animate-spin h-5 w-5 mr-2" />
                Processing...
              </>
            ) : (
              <>
                <Upload className="h-5 w-5 mr-2" />
                Submit for Evaluation
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  )
}
