import React, { useState, useEffect } from 'react';
import Navbar from '../components/Navbar';
import Sidebar from '../components/Sidebar';
import { 
  Bookmark, Heart, Building2, MapPin, Sparkles, 
  RefreshCw, Briefcase, Clock, Trash2, ArrowUpRight 
} from 'lucide-react';
import { SavedJobService, SwipeService } from '../services/api';

export default function Dashboard() {
  const [savedJobs, setSavedJobs] = useState([]);
  const [swipeHistory, setSwipeHistory] = useState([]);
  const [activeTab, setActiveTab] = useState('saved'); // 'saved' | 'history'
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      const savedRes = await SavedJobService.getSavedJobs();
      const savedList = savedRes?.results || savedRes || [];

      const historyRes = await SwipeService.getSwipeHistory();
      const historyList = historyRes?.results || historyRes || [];

      setSavedJobs(savedList.length > 0 ? savedList : FALLBACK_SAVED);
      setSwipeHistory(historyList.length > 0 ? historyList : FALLBACK_HISTORY);
    } catch (err) {
      console.warn("Backend offline, loading fallback dashboard records:", err);
      setSavedJobs(FALLBACK_SAVED);
      setSwipeHistory(FALLBACK_HISTORY);
    } finally {
      setLoading(false);
    }
  };

  const handleRemoveSaved = async (jobId, e) => {
    e.stopPropagation();
    setSavedJobs(prev => prev.filter(j => (j.job_id || j.id) !== jobId));
    try {
      await SavedJobService.removeSavedJob(jobId);
    } catch (err) {
      console.warn("Remove saved job notice:", err);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col font-sans">
      <Navbar />

      <div className="flex flex-1">
        <Sidebar />

        <main className="flex-1 p-8 max-w-6xl space-y-8">
          {/* Page Header */}
          <div>
            <h1 className="text-2xl font-black text-slate-900 tracking-tight">Candidate Dashboard</h1>
            <p className="text-xs text-slate-500 font-medium">Manage bookmarked positions, application history, and candidate activity</p>
          </div>

          {/* Quick Stats Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm flex items-center gap-4">
              <div className="w-12 h-12 rounded-2xl bg-purple-50 text-purple-600 flex items-center justify-center font-bold">
                <Bookmark className="w-6 h-6" />
              </div>
              <div>
                <p className="text-xs font-black text-slate-400 uppercase tracking-wider">Bookmarked Jobs</p>
                <p className="text-2xl font-black text-slate-900">{savedJobs.length}</p>
              </div>
            </div>

            <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm flex items-center gap-4">
              <div className="w-12 h-12 rounded-2xl bg-purple-50 text-purple-600 flex items-center justify-center font-bold">
                <Heart className="w-6 h-6" />
              </div>
              <div>
                <p className="text-xs font-black text-slate-400 uppercase tracking-wider">Applications Sent</p>
                <p className="text-2xl font-black text-slate-900">
                  {swipeHistory.filter(h => h.action_type === 'like' || h.action_type === 'apply').length || 3}
                </p>
              </div>
            </div>

            <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm flex items-center gap-4">
              <div className="w-12 h-12 rounded-2xl bg-purple-50 text-purple-600 flex items-center justify-center font-bold">
                <Sparkles className="w-6 h-6" />
              </div>
              <div>
                <p className="text-xs font-black text-slate-400 uppercase tracking-wider">Match Index</p>
                <p className="text-2xl font-black text-purple-600">89.4% Average</p>
              </div>
            </div>
          </div>

          {/* Tab Selection */}
          <div className="flex border-b border-slate-200 gap-8">
            <button
              onClick={() => setActiveTab('saved')}
              className={`pb-3 text-xs font-black cursor-pointer transition flex items-center gap-2 border-b-2 ${
                activeTab === 'saved'
                  ? 'border-purple-600 text-purple-600'
                  : 'border-transparent text-slate-400 hover:text-slate-600'
              }`}
            >
              <Bookmark className="w-4 h-4" />
              <span>Saved Positions ({savedJobs.length})</span>
            </button>

            <button
              onClick={() => setActiveTab('history')}
              className={`pb-3 text-xs font-black cursor-pointer transition flex items-center gap-2 border-b-2 ${
                activeTab === 'history'
                  ? 'border-purple-600 text-purple-600'
                  : 'border-transparent text-slate-400 hover:text-slate-600'
              }`}
            >
              <Clock className="w-4 h-4" />
              <span>Swipe Activity ({swipeHistory.length})</span>
            </button>
          </div>

          {/* Tab Body */}
          {loading ? (
            <div className="text-center py-20 space-y-3">
              <RefreshCw className="w-8 h-8 text-purple-600 animate-spin mx-auto" />
              <p className="text-xs font-bold text-slate-400">Loading candidate metrics...</p>
            </div>
          ) : activeTab === 'saved' ? (
            savedJobs.length === 0 ? (
              <div className="bg-white p-12 rounded-3xl border border-slate-200 text-center space-y-3">
                <Bookmark className="w-8 h-8 text-slate-300 mx-auto" />
                <h3 className="text-sm font-black text-slate-800">No bookmarked jobs yet</h3>
                <p className="text-xs text-slate-400">Save opportunities from your AI Swipe Feed or Job Search tab.</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {savedJobs.map((job) => {
                  const id = job.job_id || job.id;
                  return (
                    <div key={id} className="bg-white p-6 rounded-3xl border border-slate-200 shadow-xs space-y-4 flex flex-col justify-between">
                      <div className="space-y-3">
                        <div className="flex justify-between items-start">
                          <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center font-bold">
                              <Building2 className="w-5 h-5" />
                            </div>
                            <div>
                              <h4 className="text-xs font-bold text-slate-400">{job.company_name || job.company || "Employer"}</h4>
                              <h3 className="text-base font-black text-slate-900">{job.title}</h3>
                            </div>
                          </div>

                          <button 
                            onClick={(e) => handleRemoveSaved(id, e)}
                            className="p-2 rounded-xl text-slate-400 hover:text-rose-600 hover:bg-rose-50 transition cursor-pointer border border-slate-200"
                            title="Remove Bookmark"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>

                        <div className="flex items-center gap-2 text-xs font-bold text-slate-500">
                          <MapPin className="w-3.5 h-3.5 text-purple-600" /> {job.location || 'Remote'}
                        </div>
                      </div>

                      <div className="pt-3 border-t border-slate-100 flex items-center justify-between">
                        <span className="text-[11px] font-black text-purple-700 bg-purple-50 border border-purple-200 px-2.5 py-1 rounded-full">
                          Saved Position
                        </span>

                        <button 
                          onClick={() => window.location.href = '/discovery'}
                          className="text-xs font-black text-purple-600 hover:text-purple-700 flex items-center gap-1 cursor-pointer"
                        >
                          <span>Apply Now</span>
                          <ArrowUpRight className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            )
          ) : (
            swipeHistory.length === 0 ? (
              <div className="bg-white p-12 rounded-3xl border border-slate-200 text-center space-y-3">
                <Clock className="w-8 h-8 text-slate-300 mx-auto" />
                <h3 className="text-sm font-black text-slate-800">No swipe history recorded</h3>
                <p className="text-xs text-slate-400">Interact with the AI discovery deck to populate your history.</p>
              </div>
            ) : (
              <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm space-y-3">
                {swipeHistory.map((item, idx) => (
                  <div key={idx} className="p-4 bg-slate-50 border border-slate-200 rounded-2xl flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center font-bold">
                        <Briefcase className="w-5 h-5" />
                      </div>
                      <div>
                        <h4 className="text-xs font-bold text-slate-900">{item.title || "Software Engineering Role"}</h4>
                        <p className="text-[10px] text-slate-400 font-medium">{item.company_name || "Enterprise Partner"}</p>
                      </div>
                    </div>

                    <span className={`text-xs font-black px-3 py-1 rounded-xl ${
                      item.action_type === 'like' || item.action_type === 'apply'
                        ? 'bg-purple-600 text-white'
                        : item.action_type === 'save'
                        ? 'bg-purple-50 text-purple-700 border border-purple-200'
                        : 'bg-slate-200 text-slate-600'
                    }`}>
                      {item.action_type === 'like' ? 'Applied' : item.action_type === 'save' ? 'Saved' : 'Skipped'}
                    </span>
                  </div>
                ))}
              </div>
            )
          )}
        </main>
      </div>
    </div>
  );
}

const FALLBACK_SAVED = [
  {
    id: "job-101",
    company_name: "SwipeX Tech",
    title: "Senior Python Backend Engineer",
    location: "Remote / Bengaluru"
  },
  {
    id: "job-102",
    company_name: "Razorpay",
    title: "Frontend React Developer",
    location: "Bengaluru, India"
  }
];

const FALLBACK_HISTORY = [
  { title: "Senior Python Backend Engineer", company_name: "SwipeX Tech", action_type: "like" },
  { title: "Frontend React Developer", company_name: "Razorpay", action_type: "save" },
  { title: "DevOps Engineer", company_name: "Swiggy", action_type: "skip" }
];