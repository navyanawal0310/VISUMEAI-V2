import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Upload, FileText, Video, Loader, CheckCircle, AlertCircle, Briefcase } from 'lucide-react'
import { useDropzone } from 'react-dropzone'
import { uploadVideo, uploadResume, evaluateCandidate, listJobPostings, checkVideoQuality, getLatestSubmission } from '../services/api'

// ---------------------------------------------------------------------------
// Lightweight client-side JD preview
// Mirrors the skill list from jd_parser.py so the user sees instant feedback.
// This runs in the browser only — the authoritative parse happens on the server.
// ---------------------------------------------------------------------------
const PREVIEW_SKILLS = [
  "python","java","javascript","typescript","c++","c#","golang","rust","ruby",
  "php","swift","kotlin","scala","matlab","bash","powershell","react","angular",
  "vue","django","flask","fastapi","express","spring","node.js","laravel",".net",
  "tensorflow","pytorch","keras","scikit-learn","pandas","numpy","next.js","sql",
  "mysql","postgresql","mongodb","redis","cassandra","dynamodb","oracle",
  "elasticsearch","neo4j","sqlite","aws","azure","gcp","docker","kubernetes",
  "jenkins","terraform","ansible","ci/cd","git","jira","linux","unix",
  "machine learning","deep learning","nlp","natural language processing",
  "computer vision","data science","data engineering","spark","hadoop",
  "tableau","power bi","agile","scrum","microservices","rest api","graphql","devops",
]

const PREFERRED_RE = /\b(nice[- ]to[- ]have|preferred?|bonus|optional|desirable|good to have)\b/i
const REQUIRED_RE  = /\b(required?|must[- ]have|essential|mandatory|minimum)\b/i

function extractPreviewSkills(text) {
  const lower = text.toLowerCase()
  const chunks = text.split(/[\n.;]/).filter(Boolean)
  const required = new Set()
  const preferred = new Set()

  chunks.forEach(chunk => {
    const cl = chunk.toLowerCase()
    const isPref = PREFERRED_RE.test(chunk)
    const isReq  = REQUIRED_RE.test(chunk)
    PREVIEW_SKILLS.forEach(skill => {
      const escaped = skill.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
      if (new RegExp(`\\b${escaped}\\b`, 'i').test(chunk)) {
        if (isPref && !isReq) preferred.add(skill)
        else required.add(skill)
      }
    })
  })
  // A skill can't be in both — required wins
  preferred.forEach(s => { if (required.has(s)) preferred.delete(s) })

  // Fallback: if bucketing found nothing, scan the full text
  if (required.size === 0 && preferred.size === 0) {
    PREVIEW_SKILLS.forEach(skill => {
      const escaped = skill.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
      if (new RegExp(`\\b${escaped}\\b`, 'i').test(text)) required.add(skill)
    })
  }
  return { required: [...required], preferred: [...preferred] }
}

function extractPreviewExp(text) {
  const patterns = [
    /(\d+)\+?\s*(?:years?|yrs?)\s+(?:of\s+)?experience/i,
    /minimum\s+(?:of\s+)?(\d+)\+?\s*(?:years?|yrs?)/i,
    /at\s+least\s+(\d+)\+?\s*(?:years?|yrs?)/i,
    /(\d+)\+\s*(?:years?|yrs?)/i,
  ]
  for (const pat of patterns) {
    const m = text.match(pat)
    if (m) return parseInt(m[1], 10)
  }
  return null
}

function JDPreview({ jdText }) {
  const { required, preferred } = extractPreviewSkills(jdText)
  const exp = extractPreviewExp(jdText)

  if (required.length === 0 && preferred.length === 0) return null

  return (
    <div className="mt-3 p-4 bg-indigo-50 border border-indigo-200 rounded-lg text-sm">
      <p className="font-semibold text-indigo-800 mb-2 flex items-center gap-1.5">
        <Briefcase className="h-4 w-4" /> Skills detected from this JD
        <span className="font-normal text-indigo-500 text-xs">(preview — server parse is authoritative)</span>
      </p>

      {required.length > 0 && (
        <div className="mb-2">
          <span className="text-xs font-semibold text-gray-600 uppercase tracking-wide">Required</span>
          <div className="flex flex-wrap gap-1.5 mt-1">
            {required.map(s => (
              <span key={s} className="px-2 py-0.5 bg-indigo-200 text-indigo-900 rounded-full text-xs font-medium">
                {s}
              </span>
            ))}
          </div>
        </div>
      )}

      {preferred.length > 0 && (
        <div className="mb-2">
          <span className="text-xs font-semibold text-gray-600 uppercase tracking-wide">Preferred</span>
          <div className="flex flex-wrap gap-1.5 mt-1">
            {preferred.map(s => (
              <span key={s} className="px-2 py-0.5 bg-violet-100 text-violet-800 rounded-full text-xs font-medium">
                {s}
              </span>
            ))}
          </div>
        </div>
      )}

      {exp !== null && (
        <p className="text-indigo-700 text-xs mt-1">
          <strong>Experience:</strong> {exp}+ years detected
        </p>
      )}
    </div>
  )
}

export default function CandidatePage() {
  const navigate = useNavigate()
  // FIX 2: Renamed state variable from `formData` to `fields` so it can't be
  // shadowed by `const formData = new FormData()` inside handleSubmit.
  const [fields, setFields] = useState({
    candidateName: '',
    selectedJobId: '',
    jdText: '',
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
  
  useEffect(() => {
    loadJobPostings()
  }, [])
  
  useEffect(() => {
    if (fields.candidateName && fields.selectedJobId) {
      checkForPreviousSubmissions()
    } else {
      setPreviousSubmission(null)
    }
  }, [fields.candidateName, fields.selectedJobId])
  
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
      const latest = await getLatestSubmission(fields.candidateName, fields.selectedJobId)
      setPreviousSubmission(latest)
    } catch (err) {
      setPreviousSubmission(null)
    } finally {
      setCheckingPrevious(false)
    }
  }
  
  const selectedJob = jobPostings.find(job => job.job_id === fields.selectedJobId)
  
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
  
  // FIX 3: Resume dropzone now accepts PDF only (removed .docx).
  const resumeDropzone = useDropzone({
    accept: {
      'application/pdf': ['.pdf'],
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
    setFields(prev => ({
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
    e.preventDefault();

    if (!resumeFile) {
      setError("Please select a PDF resume");
      return;
    }

    // FIX 4: `formData` here is now a plain local variable — no longer shadows
    // the state. The state was renamed to `fields` above.
    const formData = new FormData();
    formData.append("file", resumeFile);
    formData.append("jd_text", fields.jdText.trim());

    try {
      setLoading(true);
      setError(null);
      setSuccess("Uploading...");

      const res = await fetch("http://127.0.0.1:8000/upload", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        throw new Error(`Server responded with ${res.status}`);
      }

      const data = await res.json();
      console.log(data);

      setSuccess("Upload successful!");
      navigate("/evaluation", { state: data });

    } catch (err) {
      console.error(err);
      setError("Upload failed: " + err.message);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-2">
          Submit Your Resume
        </h1>
        <p className="text-lg text-gray-600">
          Upload your PDF resume to receive AI-powered feedback. Video is optional.
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
      
      {/* FIX 5: Removed the duplicate bare <input type="file"> that was sitting
          above the Personal Information section. The dropzone below is the
          canonical file picker. Having two inputs was confusing and redundant. */}
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
                value={fields.candidateName}
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
            <p className="text-blue-800 text-sm">Checking for previous submissions...</p>
          </div>
        )}

        {/* Job Postings */}
        {!loadingJobs && jobPostings.length > 0 && (
          <div className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">Select Position</h2>
            <select
              name="selectedJobId"
              value={fields.selectedJobId}
              onChange={handleInputChange}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            >
              <option value="">— Select a job posting —</option>
              {jobPostings.map(job => (
                <option key={job.job_id} value={job.job_id}>
                  {job.title}
                </option>
              ))}
            </select>

            {selectedJob && (
              <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <Briefcase className="h-5 w-5 text-blue-600" />
                  <h3 className="font-semibold text-blue-900">{selectedJob.title}</h3>
                </div>
                {selectedJob.required_skills && selectedJob.required_skills.length > 0 && (
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
        
        {/* Job Description */}
        <div className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-1">
            Job Description
          </h2>
          <p className="text-sm text-gray-500 mb-4">
            Paste the job posting below. The AI will extract required skills and
            experience to give you a precise match score.
          </p>

          <textarea
            name="jdText"
            value={fields.jdText}
            onChange={handleInputChange}
            rows={8}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 text-sm leading-relaxed resize-y"
            placeholder={`Paste the full job description here, for example:\n\nSenior Data Scientist\n\nWe are looking for a Senior Data Scientist with 4+ years of experience.\n\nRequired: Python, SQL, Machine Learning, TensorFlow, AWS\nPreferred: Spark, Tableau, Docker`}
          />

          {/* Live preview of extracted skills once the user has typed enough */}
          {fields.jdText.trim().length > 40 && (
            <JDPreview jdText={fields.jdText} />
          )}
        </div>

        {/* File Uploads */}
        <div className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">Upload Files</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Video Upload — Optional */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Video Resume <span className="text-gray-400 font-normal">(optional)</span>
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
            
            {/* Resume Upload — Required, PDF only */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                PDF Resume <span className="text-red-500">*</span>
              </label>
              <div
                {...resumeDropzone.getRootProps()}
                className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors ${
                  resumeDropzone.isDragActive
                    ? 'border-primary-500 bg-primary-50'
                    : resumeFile
                    ? 'border-green-400 bg-green-50'
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
                    <p className="text-sm text-gray-600">Drop your resume here or click to browse</p>
                    <p className="text-xs text-gray-500 mt-1">PDF only</p>
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
            disabled={loading || !resumeFile}
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