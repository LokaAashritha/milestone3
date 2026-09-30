import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar';
import Sidebar from '../components/Sidebar';
import {
  Upload,
  FileText,
  Trash2,
  ArrowRight,
  RefreshCw,
  AlertCircle,
  Check,
  X,
  Loader2
} from 'lucide-react';
import { ResumeService } from '../services/api';

export default function ResumeUpload() {
  const navigate = useNavigate();

  const [resumes, setResumes] = useState([]);
  const [activeResumeId, setActiveResumeId] = useState(null);

  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [processingId, setProcessingId] = useState(null);

  const [errorMessage, setErrorMessage] = useState(null);

  // ---------------------------------------------------------------------------
  // Load resumes from the real backend
  // ---------------------------------------------------------------------------

  useEffect(() => {
    loadResumes();
  }, []);

  const normalizeResumeList = (response) => {
    if (Array.isArray(response)) {
      return response;
    }

    if (Array.isArray(response?.resumes)) {
      return response.resumes;
    }

    if (Array.isArray(response?.data?.resumes)) {
      return response.data.resumes;
    }

    if (Array.isArray(response?.data)) {
      return response.data;
    }

    return [];
  };

  const loadResumes = async () => {
    setLoading(true);
    setErrorMessage(null);

    try {
      const response = await ResumeService.getResumes();

      const list = normalizeResumeList(response);

      setResumes(list);

      const active = list.find(
        (resume) => resume.is_active_version === true
      );

      setActiveResumeId(
        active?.id || list[0]?.id || null
      );

    } catch (err) {
      console.error('Failed to load resumes:', err);

      setResumes([]);
      setActiveResumeId(null);

      setErrorMessage(
        err?.message ||
        'Unable to load resumes. Please make sure the Gateway service is running.'
      );
    } finally {
      setLoading(false);
    }
  };

  // ---------------------------------------------------------------------------
  // Upload Resume
  // ---------------------------------------------------------------------------

  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];

    // Allow selecting the same file again later.
    e.target.value = '';

    if (!file) {
      return;
    }

    setErrorMessage(null);

    // 10 MB maximum
    if (file.size > 10 * 1024 * 1024) {
      setErrorMessage('File size exceeds the 10MB limit.');
      return;
    }

    // Frontend validation
    const fileName = file.name.toLowerCase();

    const isPdf = fileName.endsWith('.pdf');
    const isDocx = fileName.endsWith('.docx');

    if (!isPdf && !isDocx) {
      setErrorMessage(
        'Unsupported file type. Please upload a PDF or DOCX resume.'
      );
      return;
    }

    setUploading(true);
    setErrorMessage(null);

    const formData = new FormData();

    formData.append('file', file);

    try {
      /*
       * IMPORTANT:
       *
       * ResumeService handles the authenticated API request.
       *
       * The integrated backend flow is:
       *
       * Frontend
       *    ↓
       * Gateway
       *    ↓
       * AIML resume processing
       *    ↓
       * Job Data resume storage
       *
       * No local/mock resume is created if this request fails.
       */

      const response = await ResumeService.uploadResume(formData);

      const uploadedResume =
        response?.resume ||
        response?.data?.resume ||
        response?.data ||
        response;

      if (!uploadedResume?.id) {
        throw new Error(
          'Resume upload completed, but the backend did not return a resume ID.'
        );
      }

      /*
       * Refresh from the backend so version numbers and active-version
       * state come from the canonical data source.
       */
      await loadResumes();

      setActiveResumeId(uploadedResume.id);

    } catch (err) {
      console.error('Resume upload failed:', err);

      setErrorMessage(
        err?.message ||
        'Unable to upload the resume. Please make sure the Gateway, Job Data, and AIML services are running.'
      );
    } finally {
      setUploading(false);
    }
  };

  // ---------------------------------------------------------------------------
  // Set Active Resume
  // ---------------------------------------------------------------------------

  const handleSetActive = async (id) => {
    if (!id || id === activeResumeId) {
      return;
    }

    setErrorMessage(null);
    setProcessingId(id);

    try {
      await ResumeService.setActiveVersion(id);

      /*
       * Do not permanently change UI state before the backend confirms it.
       */
      await loadResumes();

    } catch (err) {
      console.error('Failed to set active resume:', err);

      setErrorMessage(
        err?.message ||
        'Unable to change the active resume version.'
      );
    } finally {
      setProcessingId(null);
    }
  };

  // ---------------------------------------------------------------------------
  // Delete Resume
  // ---------------------------------------------------------------------------

  const handleDelete = async (id, e) => {
    e.stopPropagation();

    if (!id) {
      return;
    }

    const resumeToDelete = resumes.find(
      (resume) => resume.id === id
    );

    if (!resumeToDelete) {
      return;
    }

    /*
     * Do not allow deleting the active resume without first selecting
     * another version. This prevents the user from ending up with no
     * active resume when other versions exist.
     */
    if (
      resumeToDelete.is_active_version &&
      resumes.length > 1
    ) {
      setErrorMessage(
        'Please set another resume version as active before deleting this resume.'
      );
      return;
    }

    if (resumes.length === 1) {
      const confirmed = window.confirm(
        'Delete your only resume version? This cannot be undone.'
      );

      if (!confirmed) {
        return;
      }
    }

    setErrorMessage(null);
    setProcessingId(id);

    try {
      await ResumeService.deleteResume(id);

      /*
       * Refresh from backend instead of manually maintaining a fake
       * local state.
       */
      await loadResumes();

    } catch (err) {
      console.error('Failed to delete resume:', err);

      setErrorMessage(
        err?.message ||
        'Unable to delete the resume.'
      );
    } finally {
      setProcessingId(null);
    }
  };

  // ---------------------------------------------------------------------------
  // Formatting Helpers
  // ---------------------------------------------------------------------------

  const formatUploadDate = (dateValue) => {
    if (!dateValue) {
      return 'Date unavailable';
    }

    const date = new Date(dateValue);

    if (Number.isNaN(date.getTime())) {
      return 'Date unavailable';
    }

    return date.toLocaleDateString();
  };

  const getResumeFileType = (resume) => {
    if (resume?.file_type) {
      return String(resume.file_type).toUpperCase();
    }

    const fileName = resume?.file_name || '';

    if (fileName.toLowerCase().endsWith('.pdf')) {
      return 'PDF';
    }

    if (fileName.toLowerCase().endsWith('.docx')) {
      return 'DOCX';
    }

    return 'RESUME';
  };

  // ---------------------------------------------------------------------------
  // UI
  // ---------------------------------------------------------------------------

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col font-sans">

      {/* Top Navbar */}
      <Navbar />

      <div className="flex flex-1">

        {/* Left Sidebar */}
        <Sidebar />

        {/* Main Content */}
        <main className="flex-1 p-8 max-w-5xl space-y-8">

          {/* Header */}
          <div className="flex flex-col sm:flex-row justify-between gap-4 sm:items-end">

            <div>
              <h1 className="text-2xl font-black text-slate-900 tracking-tight">
                Resume Management
              </h1>

              <p className="text-xs text-slate-500 font-medium">
                Upload resume versions and select the active resume for AI matching.
              </p>
            </div>

            <button
              onClick={() => navigate('/ats-ranker')}
              disabled={!activeResumeId}
              className={`
                px-4 py-2.5 rounded-xl text-xs font-bold
                flex items-center gap-2 shadow-sm transition
                ${
                  activeResumeId
                    ? 'bg-purple-600 hover:bg-purple-700 text-white cursor-pointer'
                    : 'bg-slate-200 text-slate-400 cursor-not-allowed'
                }
              `}
            >
              <span>Proceed to ATS Scoring</span>
              <ArrowRight className="w-4 h-4" />
            </button>

          </div>

          {/* Error Banner */}
          {errorMessage && (
            <div className="p-4 bg-rose-50 border border-rose-200 rounded-2xl flex items-start gap-3 text-xs font-bold text-rose-700">

              <AlertCircle className="w-5 h-5 flex-shrink-0 text-rose-600" />

              <span className="flex-1">
                {errorMessage}
              </span>

              <button
                type="button"
                onClick={() => setErrorMessage(null)}
                className="text-rose-400 hover:text-rose-700"
              >
                <X className="w-4 h-4" />
              </button>

            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-5 gap-6">

            {/* ---------------------------------------------------------------- */}
            {/* Upload Box */}
            {/* ---------------------------------------------------------------- */}

            <div className="md:col-span-2 space-y-4">

              <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm space-y-4">

                <h2 className="text-sm font-black text-slate-900 flex items-center gap-2">
                  <Upload className="w-4 h-4 text-purple-600" />
                  Upload New Version
                </h2>

                <label
                  className={`
                    border-2 border-dashed rounded-2xl p-8
                    flex flex-col items-center justify-center
                    text-center space-y-2 transition
                    ${
                      uploading
                        ? 'border-slate-200 bg-slate-50 cursor-not-allowed'
                        : 'border-purple-200 hover:border-purple-500 bg-purple-50/40 cursor-pointer'
                    }
                  `}
                >

                  <div className="w-12 h-12 rounded-2xl bg-purple-100 text-purple-600 flex items-center justify-center mb-1">
                    <Upload className="w-6 h-6" />
                  </div>

                  <span className="text-xs font-bold text-slate-800">
                    {uploading
                      ? 'Uploading resume...'
                      : 'Click or drag resume here'}
                  </span>

                  <span className="text-[10px] text-slate-400 font-medium">
                    PDF or DOCX (Max 10MB)
                  </span>

                  <input
                    type="file"
                    accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    onChange={handleFileUpload}
                    disabled={uploading}
                    className="hidden"
                  />

                </label>

                {uploading && (
                  <div className="p-3 bg-purple-50 border border-purple-100 rounded-xl flex items-center justify-center gap-2 text-xs font-bold text-purple-700">
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    Processing resume...
                  </div>
                )}

                <div className="text-[10px] text-slate-400 font-medium leading-relaxed">
                  Uploaded resumes are stored by the backend and processed
                  for resume text and skill extraction.
                </div>

              </div>

            </div>

            {/* ---------------------------------------------------------------- */}
            {/* Version History */}
            {/* ---------------------------------------------------------------- */}

            <div className="md:col-span-3 space-y-4">

              <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm space-y-4">

                <div className="flex justify-between items-center">

                  <h2 className="text-sm font-black text-slate-900 flex items-center gap-2">
                    <FileText className="w-4 h-4 text-purple-600" />
                    Version History
                  </h2>

                  <span className="text-xs font-bold text-slate-400">
                    {resumes.length} saved version
                    {resumes.length === 1 ? '' : 's'}
                  </span>

                </div>

                {/* Loading */}
                {loading ? (

                  <div className="text-center py-10">

                    <RefreshCw className="w-6 h-6 text-purple-600 animate-spin mx-auto mb-2" />

                    <p className="text-xs font-bold text-slate-400">
                      Loading versions...
                    </p>

                  </div>

                ) : resumes.length === 0 ? (

                  /* Empty State */
                  <div className="text-center py-10 space-y-2">

                    <FileText className="w-8 h-8 text-slate-300 mx-auto" />

                    <p className="text-xs font-bold text-slate-500">
                      No resumes uploaded yet
                    </p>

                    <p className="text-[10px] text-slate-400 font-medium">
                      Upload a PDF or DOCX resume to begin AI analysis.
                    </p>

                  </div>

                ) : (

                  /* Resume List */
                  <div className="space-y-3">

                    {resumes.map((resume) => {

                      const isActive =
                        activeResumeId === resume.id ||
                        resume.is_active_version === true;

                      const isProcessing =
                        processingId === resume.id;

                      return (
                        <div
                          key={resume.id}
                          onClick={() => {
                            if (!isProcessing) {
                              handleSetActive(resume.id);
                            }
                          }}
                          className={`
                            p-4 rounded-2xl border transition
                            flex items-center justify-between gap-3
                            ${
                              isActive
                                ? 'bg-purple-50/60 border-purple-300 shadow-2xs'
                                : 'bg-slate-50 border-slate-200 hover:bg-slate-100'
                            }
                            ${
                              isProcessing
                                ? 'cursor-wait opacity-70'
                                : 'cursor-pointer'
                            }
                          `}
                        >

                          {/* Resume Information */}
                          <div className="flex items-center gap-3 min-w-0">

                            <div
                              className={`
                                w-10 h-10 rounded-xl
                                flex items-center justify-center flex-shrink-0
                                ${
                                  isActive
                                    ? 'bg-purple-600 text-white'
                                    : 'bg-slate-200 text-slate-500'
                                }
                              `}
                            >
                              <FileText className="w-5 h-5" />
                            </div>

                            <div className="min-w-0">

                              <p className="text-xs font-bold text-slate-900 truncate">
                                {resume.file_name || 'Resume'}
                              </p>

                              <p className="text-[10px] text-slate-400 font-medium">
                                Version {resume.version_number || 1}
                                {' • '}
                                {getResumeFileType(resume)}
                                {' • '}
                                {formatUploadDate(
                                  resume.uploaded_at || resume.created_at
                                )}
                              </p>

                              {resume.parsed_status && (
                                <p className="text-[9px] text-slate-400 mt-0.5">
                                  Processing status:{' '}
                                  {String(
                                    resume.parsed_status
                                  ).toLowerCase()}
                                </p>
                              )}

                            </div>

                          </div>

                          {/* Actions */}
                          <div className="flex items-center gap-2 flex-shrink-0">

                            {isProcessing ? (

                              <Loader2 className="w-4 h-4 text-purple-600 animate-spin" />

                            ) : isActive ? (

                              <span className="text-[10px] font-black bg-purple-600 text-white px-2.5 py-1 rounded-full flex items-center gap-1">
                                <Check className="w-3 h-3" />
                                Active
                              </span>

                            ) : (

                              <span className="text-[10px] font-bold text-slate-400 border border-slate-200 px-2.5 py-1 rounded-full hover:bg-white">
                                Set Active
                              </span>

                            )}

                            <button
                              type="button"
                              onClick={(e) =>
                                handleDelete(resume.id, e)
                              }
                              disabled={isProcessing}
                              className={`
                                p-1.5 rounded-lg transition
                                ${
                                  isProcessing
                                    ? 'text-slate-300 cursor-not-allowed'
                                    : 'text-slate-400 hover:text-rose-600 hover:bg-rose-50 cursor-pointer'
                                }
                              `}
                              title="Delete resume"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>

                          </div>

                        </div>
                      );
                    })}

                  </div>
                )}

              </div>

            </div>

          </div>

          {/* ---------------------------------------------------------------- */}
          {/* Integration Information */}
          {/* ---------------------------------------------------------------- */}

          <div className="bg-slate-900 rounded-3xl p-5 text-white">

            <div className="flex items-start gap-3">

              <div className="w-9 h-9 rounded-xl bg-purple-600 flex items-center justify-center flex-shrink-0">
                <FileText className="w-4 h-4" />
              </div>

              <div>

                <h3 className="text-xs font-black">
                  Resume Intelligence Pipeline
                </h3>

                <p className="text-[10px] text-slate-400 font-medium mt-1 leading-relaxed">
                  Your selected resume is stored through the integrated
                  backend and can be processed by the AI/ML service for
                  resume parsing, skill extraction, ATS scoring and
                  personalized job recommendations.
                </p>

              </div>

            </div>

          </div>

        </main>
      </div>
    </div>
  );
}