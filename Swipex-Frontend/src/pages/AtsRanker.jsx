import React, { useState, useEffect } from 'react';
import Navbar from '../components/Navbar';
import Sidebar from '../components/Sidebar';
import { 
  BarChart3, Sparkles, CheckCircle2, AlertTriangle, 
  Lightbulb, RefreshCw, Briefcase, ChevronRight
} from 'lucide-react';
import { AtsService, JobService, ResumeService } from '../services/api';

export default function AtsRanker() {
  const [jobs, setJobs] = useState([]);
  const [selectedJobId, setSelectedJobId] = useState('');
  const [resumes, setResumes] = useState([]);
  const [activeResume, setActiveResume] = useState(null);

  const [loading, setLoading] = useState(false);
  const [atsScore, setAtsScore] = useState(null);
  const [suggestions, setSuggestions] = useState([]);

  useEffect(() => {
    initData();
  }, []);

  const initData = async () => {
    try {
      const jobRes = await JobService.getJobs(1, 10);
      const jobList = jobRes?.results || jobRes || [];
      
      const fallbackJobs = jobList.length > 0 ? jobList : [
        { id: "job-101", title: "Senior Python Backend Engineer", company_name: "SwipeX Tech" },
        { id: "job-102", title: "Frontend React Developer", company_name: "Razorpay" },
        { id: "job-103", title: "Full Stack AI Engineer", company_name: "TCS Innovation Labs" }
      ];
      setJobs(fallbackJobs);
      setSelectedJobId(fallbackJobs[0].id || fallbackJobs[0].job_id);

      const resumeList = await ResumeService.getResumes();
      if (resumeList && resumeList.length > 0) {
        setResumes(resumeList);
        const active = resumeList.find(r => r.is_active_version) || resumeList[0];
        setActiveResume(active);
      } else {
        setActiveResume({ id: "res-default-1", file_name: "asha_resume_v1.pdf" });
      }
    } catch (err) {
      console.warn("Using fallback job list:", err);
      const fallbackJobs = [
        { id: "job-101", title: "Senior Python Backend Engineer", company_name: "SwipeX Tech" },
        { id: "job-102", title: "Frontend React Developer", company_name: "Razorpay" }
      ];
      setJobs(fallbackJobs);
      setSelectedJobId(fallbackJobs[0].id);
      setActiveResume({ id: "res-default-1", file_name: "asha_resume_v1.pdf" });
    }
  };

  const handleRunAnalysis = async () => {
    if (!selectedJobId || !activeResume) return;

    setLoading(true);
    try {
      const scoreRes = await AtsService.getAtsScore(activeResume.id, selectedJobId);
      const suggestionsRes = await AtsService.getAtsSuggestions(activeResume.id, selectedJobId);

      setAtsScore(scoreRes);
      setSuggestions(suggestionsRes?.suggestions || []);
    } catch (err) {
      console.warn("Backend offline, loading mock ATS score calculation:", err);
      setAtsScore({
        overall_score: 84.5,
        skill_score: 85.0,
        keyword_score: 83.3,
        missing_skills: ["Docker", "Kubernetes", "Redis Caching"],
        missing_keywords: ["Microservices", "CI/CD Pipeline", "REST API Optimization"],
        summary: "Strong overall match! High alignment with core Python programming skills."
      });
      setSuggestions([
        { id: 1, title: "Include Containerization Terms", detail: "Adding Docker & Kubernetes keywords will boost your score by ~12%." },
        { id: 2, title: "Highlight Backend Performance", detail: "Quantify past achievements with metric impact (e.g., 'Reduced response latency by 30%')." }
      ]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (selectedJobId && activeResume) {
      handleRunAnalysis();
    }
  }, [selectedJobId]);

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col font-sans">
      <Navbar />

      <div className="flex flex-1">
        <Sidebar />

        <main className="flex-1 p-8 max-w-5xl space-y-8">
          <div className="flex justify-between items-end">
            <div>
              <h1 className="text-2xl font-black text-slate-900 tracking-tight">ATS Resume Ranker</h1>
              <p className="text-xs text-slate-500 font-medium">Evaluate resume compatibility against target job descriptions using AI scoring</p>
            </div>
            
            <div className="bg-purple-50 border border-purple-200 px-3.5 py-1.5 rounded-xl flex items-center gap-2">
              <span className="text-[10px] font-black uppercase text-purple-600">Active Resume:</span>
              <span className="text-xs font-bold text-slate-800">{activeResume?.file_name || 'Loading...'}</span>
            </div>
          </div>

          <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm space-y-4">
            <label className="text-xs font-black text-slate-700 uppercase tracking-wider flex items-center gap-2">
              <Briefcase className="w-4 h-4 text-purple-600" /> Select Target Job Position
            </label>
            <select
              value={selectedJobId}
              onChange={(e) => setSelectedJobId(e.target.value)}
              className="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3 text-xs font-bold text-slate-800 focus:outline-hidden focus:border-purple-600 transition cursor-pointer"
            >
              {jobs.map((j) => (
                <option key={j.id || j.job_id} value={j.id || j.job_id}>
                  {j.title} — {j.company_name || j.company || 'Tech Employer'}
                </option>
              ))}
            </select>
          </div>

          {loading ? (
            <div className="bg-white p-12 rounded-3xl border border-slate-200 text-center space-y-3">
              <RefreshCw className="w-8 h-8 text-purple-600 animate-spin mx-auto" />
              <p className="text-xs font-bold text-slate-700">Evaluating 70/30 Skill-Keyword ATS Vectors...</p>
            </div>
          ) : atsScore && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm flex flex-col justify-between space-y-4">
                  <span className="text-xs font-black text-slate-400 uppercase">Overall Match</span>
                  <div className="flex items-baseline gap-2">
                    <span className="text-4xl font-black text-purple-600">
                      {Math.round(atsScore.overall_score || 80)}%
                    </span>
                    <span className="text-xs font-bold text-slate-400">Target Fit</span>
                  </div>
                  <p className="text-[11px] text-slate-500 font-medium">{atsScore.summary}</p>
                </div>

                <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm flex flex-col justify-between space-y-4">
                  <span className="text-xs font-black text-slate-400 uppercase">Skill Overlap (70%)</span>
                  <div className="flex items-baseline gap-2">
                    <span className="text-3xl font-black text-slate-900">
                      {Math.round(atsScore.skill_score || 75)}%
                    </span>
                  </div>
                  <div className="w-full bg-slate-100 rounded-full h-2">
                    <div className="bg-purple-600 h-2 rounded-full" style={{ width: `${atsScore.skill_score || 75}%` }} />
                  </div>
                </div>

                <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm flex flex-col justify-between space-y-4">
                  <span className="text-xs font-black text-slate-400 uppercase">Keyword Density (30%)</span>
                  <div className="flex items-baseline gap-2">
                    <span className="text-3xl font-black text-slate-900">
                      {Math.round(atsScore.keyword_score || 80)}%
                    </span>
                  </div>
                  <div className="w-full bg-slate-100 rounded-full h-2">
                    <div className="bg-purple-600 h-2 rounded-full" style={{ width: `${atsScore.keyword_score || 80}%` }} />
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm space-y-3">
                  <h3 className="text-xs font-black text-rose-600 uppercase tracking-wider flex items-center gap-2">
                    <AlertTriangle className="w-4 h-4" /> Missing Core Skills
                  </h3>
                  <div className="flex flex-wrap gap-2 pt-2">
                    {(atsScore.missing_skills || ["Docker", "Kubernetes"]).map((skill, i) => (
                      <span key={i} className="text-xs font-bold bg-rose-50 text-rose-700 border border-rose-200 px-3 py-1 rounded-xl">
                        + {skill}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm space-y-3">
                  <h3 className="text-xs font-black text-purple-600 uppercase tracking-wider flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4" /> Missing Domain Keywords
                  </h3>
                  <div className="flex flex-wrap gap-2 pt-2">
                    {(atsScore.missing_keywords || ["Microservices", "REST APIs"]).map((kw, i) => (
                      <span key={i} className="text-xs font-bold bg-purple-50 text-purple-700 border border-purple-200 px-3 py-1 rounded-xl">
                        + {kw}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm space-y-4">
                <h3 className="text-xs font-black text-slate-900 uppercase tracking-wider flex items-center gap-2">
                  <Lightbulb className="w-4 h-4 text-purple-600" /> AI Resume Optimization Suggestions
                </h3>
                <div className="space-y-3">
                  {suggestions.map((sug, idx) => (
                    <div key={idx} className="p-4 bg-slate-50 border border-slate-200 rounded-2xl flex items-start gap-3">
                      <ChevronRight className="w-4 h-4 text-purple-600 flex-shrink-0 mt-0.5" />
                      <div>
                        <h4 className="text-xs font-bold text-slate-900">{sug.title}</h4>
                        <p className="text-[11px] text-slate-500 font-medium mt-0.5">{sug.detail}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}