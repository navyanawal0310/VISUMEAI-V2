import React, { useState } from 'react'
import { Plus, Edit, Trash, Eye, X, Briefcase, Users } from 'lucide-react'
import { createJobPosting, updateJobPosting, deleteJobPosting } from '../services/api'

export default function JobManagement({ jobPostings, onJobsUpdated }) {
  const [showJobForm, setShowJobForm] = useState(false)
  const [editingJob, setEditingJob] = useState(null)
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    required_skills: '',
    preferred_skills: '',
    experience_years: ''
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const resetForm = () => {
    setFormData({
      title: '',
      description: '',
      required_skills: '',
      preferred_skills: '',
      experience_years: ''
    })
    setEditingJob(null)
    setError(null)
  }

  const handleOpenCreate = () => {
    resetForm()
    setShowJobForm(true)
  }

  const handleOpenEdit = (job) => {
    setFormData({
      title: job.title,
      description: job.description,
      required_skills: job.required_skills.join(', '),
      preferred_skills: job.preferred_skills?.join(', ') || '',
      experience_years: job.experience_years?.toString() || ''
    })
    setEditingJob(job)
    setShowJobForm(true)
  }

  const handleClose = () => {
    setShowJobForm(false)
    resetForm()
  }

  const handleInputChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)
    setLoading(true)

    try {
      const jobData = {
        title: formData.title,
        description: formData.description,
        required_skills: formData.required_skills
          .split(',')
          .map(s => s.trim())
          .filter(s => s),
        preferred_skills: formData.preferred_skills
          .split(',')
          .map(s => s.trim())
          .filter(s => s),
        experience_years: formData.experience_years ? parseInt(formData.experience_years) : null
      }

      if (editingJob) {
        await updateJobPosting(editingJob.job_id, jobData)
      } else {
        await createJobPosting(jobData)
      }

      onJobsUpdated()
      handleClose()
    } catch (err) {
      console.error('Error saving job:', err)
      setError(err.response?.data?.detail || 'Failed to save job posting')
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (jobId, jobTitle) => {
    if (!window.confirm(`Are you sure you want to delete "${jobTitle}"?`)) {
      return
    }

    try {
      await deleteJobPosting(jobId)
      onJobsUpdated()
    } catch (err) {
      console.error('Error deleting job:', err)
      alert('Failed to delete job posting')
    }
  }

  const handleToggleStatus = async (job) => {
    try {
      const newStatus = job.status === 'active' ? 'closed' : 'active'
      await updateJobPosting(job.job_id, { status: newStatus })
      onJobsUpdated()
    } catch (err) {
      console.error('Error updating job status:', err)
      alert('Failed to update job status')
    }
  }

  return (
    <div>
      {/* Header */}
      <div className="mb-6 flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-semibold text-gray-900">Job Postings</h2>
          <p className="text-gray-600 mt-1">Manage open positions and track applications</p>
        </div>
        <button
          onClick={handleOpenCreate}
          className="flex items-center px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 shadow-md transition-colors"
        >
          <Plus className="h-5 w-5 mr-2" />
          Create Job Posting
        </button>
      </div>

      {/* Job Postings Grid */}
      {jobPostings.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-lg border border-gray-200">
          <Briefcase className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Job Postings Yet</h3>
          <p className="text-gray-600 mb-4">Create your first job posting to start receiving applications</p>
          <button
            onClick={handleOpenCreate}
            className="inline-flex items-center px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
          >
            <Plus className="h-4 w-4 mr-2" />
            Create Job Posting
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {jobPostings.map(job => (
            <div key={job.job_id} className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-lg transition-shadow">
              <div className="flex justify-between items-start mb-4">
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900 mb-1">{job.title}</h3>
                  <div className="flex items-center text-sm text-gray-500 gap-3">
                    <span className="flex items-center">
                      <Users className="h-4 w-4 mr-1" />
                      {job.applications_count} applications
                    </span>
                  </div>
                </div>
                <button
                  onClick={() => handleToggleStatus(job)}
                  className={`px-3 py-1 rounded-full text-xs font-medium ${
                    job.status === 'active'
                      ? 'bg-green-100 text-green-800 hover:bg-green-200'
                      : 'bg-gray-100 text-gray-800 hover:bg-gray-200'
                  } transition-colors`}
                >
                  {job.status}
                </button>
              </div>

              <p className="text-gray-600 text-sm mb-4 line-clamp-3">
                {job.description}
              </p>

              {job.required_skills.length > 0 && (
                <div className="mb-4">
                  <p className="text-xs font-medium text-gray-700 mb-2">Required Skills:</p>
                  <div className="flex flex-wrap gap-1">
                    {job.required_skills.slice(0, 4).map(skill => (
                      <span key={skill} className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">
                        {skill}
                      </span>
                    ))}
                    {job.required_skills.length > 4 && (
                      <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded">
                        +{job.required_skills.length - 4}
                      </span>
                    )}
                  </div>
                </div>
              )}

              {job.experience_years && (
                <p className="text-xs text-gray-600 mb-4">
                  <strong>Experience:</strong> {job.experience_years}+ years
                </p>
              )}

              <div className="flex gap-2 pt-4 border-t border-gray-200">
                <button
                  onClick={() => handleOpenEdit(job)}
                  className="flex-1 flex items-center justify-center px-3 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  <Edit className="h-4 w-4 mr-1" />
                  Edit
                </button>
                <button
                  onClick={() => handleDelete(job.job_id, job.title)}
                  className="px-3 py-2 text-sm border border-red-300 text-red-600 rounded-lg hover:bg-red-50 transition-colors"
                >
                  <Trash className="h-4 w-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Job Form Modal */}
      {showJobForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex justify-between items-center">
              <h3 className="text-xl font-semibold text-gray-900">
                {editingJob ? 'Edit Job Posting' : 'Create Job Posting'}
              </h3>
              <button
                onClick={handleClose}
                className="text-gray-400 hover:text-gray-600 transition-colors"
              >
                <X className="h-6 w-6" />
              </button>
            </div>

            <form onSubmit={handleSubmit} className="p-6">
              {error && (
                <div className="mb-4 bg-red-50 border border-red-200 rounded-lg p-3 text-red-800 text-sm">
                  {error}
                </div>
              )}

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Job Title *
                  </label>
                  <input
                    type="text"
                    name="title"
                    value={formData.title}
                    onChange={handleInputChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    placeholder="e.g., Senior Software Engineer"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Job Description *
                  </label>
                  <textarea
                    name="description"
                    value={formData.description}
                    onChange={handleInputChange}
                    rows={6}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    placeholder="Enter detailed job description..."
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Required Skills * (comma-separated)
                  </label>
                  <input
                    type="text"
                    name="required_skills"
                    value={formData.required_skills}
                    onChange={handleInputChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    placeholder="Python, React, AWS, Docker"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Preferred Skills (comma-separated)
                  </label>
                  <input
                    type="text"
                    name="preferred_skills"
                    value={formData.preferred_skills}
                    onChange={handleInputChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    placeholder="Kubernetes, GraphQL, TypeScript"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Required Experience (years)
                  </label>
                  <input
                    type="number"
                    name="experience_years"
                    value={formData.experience_years}
                    onChange={handleInputChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    placeholder="5"
                    min="0"
                  />
                </div>
              </div>

              <div className="mt-6 flex justify-end gap-3">
                <button
                  type="button"
                  onClick={handleClose}
                  className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                  disabled={loading}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:bg-gray-400 transition-colors"
                  disabled={loading}
                >
                  {loading ? 'Saving...' : editingJob ? 'Update' : 'Create'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
