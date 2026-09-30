import React, { useState, useEffect } from 'react';
import Navbar from '../components/Navbar';
import Sidebar from '../components/Sidebar';
import {
  Briefcase,
  RefreshCw,
  AlertCircle,
  CheckCircle2,
  Lightbulb,
  ChevronRight,
  X
} from 'lucide-react';
import {
  AtsService,
  JobService,
  ResumeService
} from '../services/api';

export default function AtsRanker() {
  const [jobs, setJobs] = useState([]);
  const [selectedJobId, setSelectedJobId] = useState('');

  const [resumes, setResumes] = useState([]);
  const [activeResume, setActiveResume] = useState(null);

  const [loadingData, setLoadingData] = useState(true);
  const [loadingAnalysis, setLoadingAnalysis] = useState(false);

  const [atsScore, setAtsScore] = useState(null);
  const [suggestions, setSuggestions] = useState([]);

  const [errorMessage, setErrorMessage] = useState(null);

  // ---------------------------------------------------------------------------
  // Normalize API responses
  // ---------------------------------------------------------------------------

  const normalizeJobs = (response) => {
    if (Array.isArray(response)) {
      return response;
    }

    if (Array.isArray(response?.results)) {
      return response.results;
    }

    if (Array.isArray(response?.jobs)) {
      return response.jobs;
    }

    if (Array.isArray(response?.data?.jobs)) {
      return response.data.jobs;
    }

    if (Array.isArray(response?.data)) {
      return response.data;
    }

    return [];
  };

  const normalizeResumes = (response) => {
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

  // ---------------------------------------------------------------------------
  // Initial Data
  // ---------------------------------------------------------------------------

  useEffect(() => {
    initData();
  }, []);

  const initData = async () => {
    setLoadingData(true);
    setErrorMessage(null);

    try {
      // -----------------------------------------------------------------------
      // Load real jobs from Gateway
      // -----------------------------------------------------------------------

      const jobResponse = await JobService.getJobs(1, 50);

      const jobList = normalizeJobs(jobResponse);

      setJobs(jobList);

      if (jobList.length > 0) {
        const firstJob = jobList[0];

        const firstJobId =
          firstJob.id ||
          firstJob.job_id;

        if (firstJobId) {
          setSelectedJobId(String(firstJobId));
        }
      }

      // -----------------------------------------------------------------------
      // Load real resumes from Gateway
      // -----------------------------------------------------------------------

      const resumeResponse = await ResumeService.getResumes();

      const resumeList = normalizeResumes(resumeResponse);

      setResumes(resumeList);

      const active =
        resumeList.find(
          (resume) => resume.is_active_version === true
        ) || resumeList[0];

      setActiveResume(active || null);

      if (!active) {
        setErrorMessage(
          'No resume is available. Please upload a resume before running ATS analysis.'
        );
      } else if (jobList.length === 0) {
        setErrorMessage(
          'No active jobs are available for ATS analysis.'
        );
      }

    } catch (err) {
      console.error('Failed to load ATS data:', err);

      setJobs([]);
      setResumes([]);
      setActiveResume(null);
      setSelectedJobId('');

      setErrorMessage(
        err?.message ||
        'Unable to load jobs and resumes. Please make sure the Gateway service is running.'
      );
    } finally {
      setLoadingData(false);
    }
  };

  // ---------------------------------------------------------------------------
  // Run Real ATS Analysis
  // ---------------------------------------------------------------------------

  const handleRunAnalysis = async () => {
    if (!selectedJobId) {
      setErrorMessage('Please select a target job.');
      return;
    }

    if (!activeResume?.id) {
      setErrorMessage(
        'No active resume is available. Please upload or activate a resume first.'
      );
      return;
    }

    setLoadingAnalysis(true);
    setErrorMessage(null);

    /*
     * Clear previous results while the new analysis is running.
     */
    setAtsScore(null);
    setSuggestions([]);

    try {
      // -----------------------------------------------------------------------
      // Gateway:
      //
      // POST /api/v1/ats/score
      //
      // Gateway verifies the user's resume/job and forwards the request to
      // AIML.
      // -----------------------------------------------------------------------

      const scoreResponse = await AtsService.getAtsScore(
        activeResume.id,
        selectedJobId
      );

      // -----------------------------------------------------------------------
      // Gateway:
      //
      // POST /api/v1/ats/suggestions
      //
      // Gateway forwards this to AIML.
      // -----------------------------------------------------------------------

      const suggestionsResponse =
        await AtsService.getAtsSuggestions(
          activeResume.id,
          selectedJobId
        );

      const normalizedScore =
        scoreResponse?.data ||
        scoreResponse?.ats_score ||
        scoreResponse;

      const normalizedSuggestions =
        suggestionsResponse?.suggestions ||
        suggestionsResponse?.data?.suggestions ||
        suggestionsResponse?.data ||
        [];

      setAtsScore(normalizedScore || null);

      setSuggestions(
        Array.isArray(normalizedSuggestions)
          ? normalizedSuggestions
          : []
      );

      if (!normalizedScore) {
        throw new Error(
          'The ATS service returned an empty analysis result.'
        );
      }

    } catch (err) {
      console.error('ATS analysis failed:', err);

      setAtsScore(null);
      setSuggestions([]);

      setErrorMessage(
        err?.message ||
        'Unable to calculate ATS score. Please make sure the Gateway, AIML, and Job Data services are running.'
      );
    } finally {
      setLoadingAnalysis(false);
    }
  };

  // ---------------------------------------------------------------------------
  // Automatically analyse when both real job + resume are available
  // ---------------------------------------------------------------------------

  useEffect(() => {
    if (
      !loadingData &&
      selectedJobId &&
      activeResume?.id
    ) {
      handleRunAnalysis();
    }
  }, [selectedJobId, activeResume?.id, loadingData]);

  // ---------------------------------------------------------------------------
  // Score Helpers
  // ---------------------------------------------------------------------------

  const getOverallScore = () => {
    const value =
      atsScore?.overall_score ??
      atsScore?.match_score ??
      null;

    if (value === null || value === undefined) {
      return null;
    }

    return Number(value);
  };

  const getSkillScore = () => {
    const value = atsScore?.skill_score;

    if (value === null || value === undefined) {
      return null;
    }

    return Number(value);
  };

  const getKeywordScore = () => {
    const value = atsScore?.keyword_score;

    if (value === null || value === undefined) {
      return null;
    }

    return Number(value);
  };

  const getSemanticScore = () => {
    const value =
      atsScore?.semantic_match_score ??
      atsScore?.semantic_score ??
      null;

    if (value === null || value === undefined) {
      return null;
    }

    return Number(value);
  };

  const clampScore = (score) => {
    if (score === null || score === undefined) {
      return 0;
    }

    return Math.min(100, Math.max(0, Number(score)));
  };

  const selectedJob = jobs.find(
    (job) =>
      String(job.id || job.job_id) ===
      String(selectedJobId)
  );

  // ---------------------------------------------------------------------------
  // Render
  // ---------------------------------------------------------------------------

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col font-sans">

      <Navbar />

      <div className="flex flex-1">

        <Sidebar />

        <main className="flex-1 p-8 max-w-5xl space-y-8">

          {/* --------------------------------------------------------------- */}
          {/* Header */}
          {/* --------------------------------------------------------------- */}

          <div className="flex flex-col sm:flex-row justify-between gap-4 sm:items-end">

            <div>

              <h1 className="text-2xl font-black text-slate-900 tracking-tight">
                ATS Resume Ranker
              </h1>

              <p className="text-xs text-slate-500 font-medium">
                Evaluate resume compatibility against real job descriptions using AI scoring.
              </p>

            </div>

            <div className="bg-purple-50 border border-purple-200 px-3.5 py-2 rounded-xl flex items-center gap-2">

              <span className="text-[10px] font-black uppercase text-purple-600">
                Active Resume:
              </span>

              <span className="text-xs font-bold text-slate-800">
                {activeResume?.file_name || 'None selected'}
              </span>

            </div>

          </div>

          {/* --------------------------------------------------------------- */}
          {/* Error */}
          {/* --------------------------------------------------------------- */}

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

          {/* --------------------------------------------------------------- */}
          {/* Loading Initial Data */}
          {/* --------------------------------------------------------------- */}

          {loadingData ? (

            <div className="bg-white p-12 rounded-3xl border border-slate-200 text-center space-y-3">

              <RefreshCw className="w-8 h-8 text-purple-600 animate-spin mx-auto" />

              <p className="text-xs font-bold text-slate-700">
                Loading jobs and resume data...
              </p>

            </div>

          ) : (

            <>
              {/* ----------------------------------------------------------- */}
              {/* Job Selection */}
              {/* ----------------------------------------------------------- */}

              <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm space-y-4">

                <label className="text-xs font-black text-slate-700 uppercase tracking-wider flex items-center gap-2">

                  <Briefcase className="w-4 h-4 text-purple-600" />

                  Select Target Job Position

                </label>

                {jobs.length === 0 ? (

                  <div className="p-4 bg-slate-50 border border-slate-200 rounded-2xl text-xs font-medium text-slate-500">
                    No jobs are currently available.
                  </div>

                ) : (

                  <select
                    value={selectedJobId}
                    onChange={(e) => {
                      setSelectedJobId(e.target.value);
                    }}
                    className="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3 text-xs font-bold text-slate-800 focus:outline-hidden focus:border-purple-600 transition cursor-pointer"
                  >

                    {jobs.map((job) => {

                      const jobId =
                        job.id ||
                        job.job_id;

                      const companyName =
                        job.company_name ||
                        job.company?.name ||
                        job.company ||
                        'Employer';

                      return (
                        <option
                          key={jobId}
                          value={jobId}
                        >
                          {job.title || 'Untitled Job'}
                          {' — '}
                          {companyName}
                        </option>
                      );
                    })}

                  </select>

                )}

                {selectedJob && (
                  <div className="text-[10px] text-slate-400 font-medium">

                    Target:
                    {' '}
                    <span className="font-bold text-slate-600">
                      {selectedJob.title}
                    </span>

                    {selectedJob.location && (
                      <>
                        {' • '}
                        {selectedJob.location}
                      </>
                    )}

                  </div>
                )}

              </div>

              {/* ----------------------------------------------------------- */}
              {/* No Resume */}
              {/* ----------------------------------------------------------- */}

              {!activeResume?.id && (
                <div className="bg-white p-8 rounded-3xl border border-slate-200 text-center space-y-4">

                  <AlertCircle className="w-8 h-8 text-amber-500 mx-auto" />

                  <div>

                    <h3 className="text-sm font-black text-slate-900">
                      Resume Required
                    </h3>

                    <p className="text-xs text-slate-500 font-medium mt-1">
                      Upload a resume before running ATS analysis.
                    </p>

                  </div>

                </div>
              )}

              {/* ----------------------------------------------------------- */}
              {/* Loading Analysis */}
              {/* ----------------------------------------------------------- */}

              {loadingAnalysis && (
                <div className="bg-white p-12 rounded-3xl border border-slate-200 text-center space-y-3">

                  <RefreshCw className="w-8 h-8 text-purple-600 animate-spin mx-auto" />

                  <p className="text-xs font-bold text-slate-700">
                    AI/ML service is evaluating resume compatibility...
                  </p>

                  <p className="text-[10px] text-slate-400 font-medium">
                    Calculating skill overlap, keyword overlap and semantic similarity.
                  </p>

                </div>
              )}

              {/* ----------------------------------------------------------- */}
              {/* ATS Results */}
              {/* ----------------------------------------------------------- */}

              {!loadingAnalysis && atsScore && (

                <div className="space-y-6">

                  {/* Score Cards */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">

                    {/* Overall */}
                    <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm flex flex-col justify-between space-y-4">

                      <span className="text-xs font-black text-slate-400 uppercase">
                        Overall Match
                      </span>

                      <div className="flex items-baseline gap-2">

                        <span className="text-4xl font-black text-purple-600">

                          {getOverallScore() !== null
                            ? `${Math.round(getOverallScore())}%`
                            : 'N/A'}

                        </span>

                        <span className="text-xs font-bold text-slate-400">
                          Target Fit
                        </span>

                      </div>

                      <p className="text-[11px] text-slate-500 font-medium">
                        {atsScore.summary ||
                          atsScore.overall_feedback ||
                          'ATS analysis completed using the integrated AI/ML service.'}
                      </p>

                    </div>

                    {/* Skill */}
                    <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm flex flex-col justify-between space-y-4">

                      <span className="text-xs font-black text-slate-400 uppercase">
                        Skill Overlap
                      </span>

                      <div className="flex items-baseline gap-2">

                        <span className="text-3xl font-black text-slate-900">

                          {getSkillScore() !== null
                            ? `${Math.round(getSkillScore())}%`
                            : 'N/A'}

                        </span>

                      </div>

                      <div className="w-full bg-slate-100 rounded-full h-2">

                        {getSkillScore() !== null && (
                          <div
                            className="bg-purple-600 h-2 rounded-full transition-all"
                            style={{
                              width: `${clampScore(
                                getSkillScore()
                              )}%`
                            }}
                          />
                        )}

                      </div>

                    </div>

                    {/* Keyword */}
                    <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm flex flex-col justify-between space-y-4">

                      <span className="text-xs font-black text-slate-400 uppercase">
                        Keyword Match
                      </span>

                      <div className="flex items-baseline gap-2">

                        <span className="text-3xl font-black text-slate-900">

                          {getKeywordScore() !== null
                            ? `${Math.round(getKeywordScore())}%`
                            : 'N/A'}

                        </span>

                      </div>

                      <div className="w-full bg-slate-100 rounded-full h-2">

                        {getKeywordScore() !== null && (
                          <div
                            className="bg-purple-600 h-2 rounded-full transition-all"
                            style={{
                              width: `${clampScore(
                                getKeywordScore()
                              )}%`
                            }}
                          />
                        )}

                      </div>

                    </div>

                  </div>

                  {/* Semantic Score */}
                  {getSemanticScore() !== null && (
                    <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm">

                      <div className="flex justify-between items-center mb-3">

                        <span className="text-xs font-black text-slate-400 uppercase">
                          Semantic Similarity
                        </span>

                        <span className="text-sm font-black text-purple-600">
                          {Math.round(getSemanticScore())}%
                        </span>

                      </div>

                      <div className="w-full bg-slate-100 rounded-full h-2">

                        <div
                          className="bg-purple-600 h-2 rounded-full transition-all"
                          style={{
                            width: `${clampScore(
                              getSemanticScore()
                            )}%`
                          }}
                        />

                      </div>

                    </div>
                  )}

                  {/* ------------------------------------------------------- */}
                  {/* Missing Skills / Keywords */}
                  {/* ------------------------------------------------------- */}

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

                    {/* Missing Skills */}
                    <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm space-y-3">

                      <h3 className="text-xs font-black text-rose-600 uppercase tracking-wider flex items-center gap-2">

                        <AlertCircle className="w-4 h-4" />

                        Missing Core Skills

                      </h3>

                      <div className="flex flex-wrap gap-2 pt-2">

                        {Array.isArray(atsScore.missing_skills) &&
                        atsScore.missing_skills.length > 0 ? (

                          atsScore.missing_skills.map(
                            (skill, index) => (
                              <span
                                key={`${skill}-${index}`}
                                className="text-xs font-bold bg-rose-50 text-rose-700 border border-rose-200 px-3 py-1 rounded-xl"
                              >
                                + {skill}
                              </span>
                            )
                          )

                        ) : (

                          <span className="text-xs font-medium text-emerald-600 flex items-center gap-1">
                            <CheckCircle2 className="w-4 h-4" />
                            No missing core skills reported.
                          </span>

                        )}

                      </div>

                    </div>

                    {/* Missing Keywords */}
                    <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm space-y-3">

                      <h3 className="text-xs font-black text-purple-600 uppercase tracking-wider flex items-center gap-2">

                        <AlertCircle className="w-4 h-4" />

                        Missing Domain Keywords

                      </h3>

                      <div className="flex flex-wrap gap-2 pt-2">

                        {Array.isArray(atsScore.missing_keywords) &&
                        atsScore.missing_keywords.length > 0 ? (

                          atsScore.missing_keywords.map(
                            (keyword, index) => (
                              <span
                                key={`${keyword}-${index}`}
                                className="text-xs font-bold bg-purple-50 text-purple-700 border border-purple-200 px-3 py-1 rounded-xl"
                              >
                                + {keyword}
                              </span>
                            )
                          )

                        ) : (

                          <span className="text-xs font-medium text-emerald-600 flex items-center gap-1">
                            <CheckCircle2 className="w-4 h-4" />
                            No missing keywords reported.
                          </span>

                        )}

                      </div>

                    </div>

                  </div>

                  {/* ------------------------------------------------------- */}
                  {/* AI Suggestions */}
                  {/* ------------------------------------------------------- */}

                  <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm space-y-4">

                    <h3 className="text-xs font-black text-slate-900 uppercase tracking-wider flex items-center gap-2">

                      <Lightbulb className="w-4 h-4 text-purple-600" />

                      AI Resume Optimization Suggestions

                    </h3>

                    {suggestions.length > 0 ? (

                      <div className="space-y-3">

                        {suggestions.map((suggestion, index) => (

                          <div
                            key={
                              suggestion.id ||
                              `${suggestion.title}-${index}`
                            }
                            className="p-4 bg-slate-50 border border-slate-200 rounded-2xl flex items-start gap-3"
                          >

                            <ChevronRight className="w-4 h-4 text-purple-600 flex-shrink-0 mt-0.5" />

                            <div>

                              <h4 className="text-xs font-bold text-slate-900">
                                {suggestion.title ||
                                  'Resume Improvement'}
                              </h4>

                              <p className="text-[11px] text-slate-500 font-medium mt-0.5">
                                {suggestion.detail ||
                                  suggestion.description ||
                                  'Review this recommendation from the AI/ML service.'}
                              </p>

                              {suggestion.category && (
                                <span className="inline-block mt-2 text-[9px] font-bold text-purple-600 uppercase">
                                  {suggestion.category}
                                </span>
                              )}

                            </div>

                          </div>

                        ))}

                      </div>

                    ) : (

                      <div className="p-4 bg-slate-50 border border-slate-200 rounded-2xl text-xs font-medium text-slate-500">
                        The AI/ML service did not return any optimization suggestions for this resume/job combination.
                      </div>

                    )}

                  </div>

                </div>
              )}

            </>
          )}

        </main>
      </div>
    </div>
  );
}