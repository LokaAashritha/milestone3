import React, { useState, useEffect } from 'react';
import Navbar from '../components/Navbar';
import Sidebar from '../components/Sidebar';
import { 
  Search, MapPin, Building2, Sparkles, Filter, 
  Bookmark, RefreshCw, Briefcase, ArrowUpRight
} from 'lucide-react';
import { JobService, SavedJobService } from '../services/api';

export default function JobSearch() {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [query, setQuery] = useState('');
  const [location, setLocation] = useState('');
  const [jobType, setJobType] = useState('all');
  const [savedJobIds, setSavedJobIds] = useState(new Set());

  useEffect(() => {
    fetchJobs();
  }, []);

  const fetchJobs = async () => {
    setLoading(true);
    try {
      const res = await JobService.getJobs(1, 20, { type: jobType !== 'all' ? jobType : undefined });
      const list = res?.results || res || [];
      
      if (list.length > 0) {
        setJobs(list);
      } else {
        setJobs(FALLBACK_JOBS);
      }
    } catch (err) {
      console.warn("Backend offline, loading fallback search listings:", err);
      setJobs(FALLBACK_JOBS);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (e) => {
    e?.preventDefault();
    setLoading(true);
    try {
      const res = await JobService.searchJobs({
        q: query,
        location: location,
        type: jobType !== 'all' ? jobType : undefined
      });
      const list = res?.results || res || [];
      setJobs(list.length > 0 ? list : FALLBACK_JOBS);
    } catch (err) {
      console.warn("Search endpoint notice:", err);
      // Filter locally as fallback
      const filtered = FALLBACK_JOBS.filter(j => 
        j.title.toLowerCase().includes(query.toLowerCase()) ||
        j.company_name.toLowerCase().includes(query.toLowerCase())
      );
      setJobs(filtered.length > 0 ? filtered : FALLBACK_JOBS);
    } finally {
      setLoading(false);
    }
  };

  const handleSaveJob = async (jobId, e) => {
    e.stopPropagation();
    setSavedJobIds(prev => new Set(prev).add(jobId));
    try {
      await SavedJobService.saveJob(jobId);
    } catch (err) {
      console.warn("Save job notice:", err);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col font-sans">
      <Navbar />

      <div className="flex flex-1">
        <Sidebar />

        <main className="flex-1 p-8 max-w-6xl space-y-8">
          {/* Header */}
          <div>
            <h1 className="text-2xl font-black text-slate-900 tracking-tight">Explore & Search Opportunities</h1>
            <p className="text-xs text-slate-500 font-medium">Filter curated positions by tech stack, role, or preferred work location</p>
          </div>

          {/* Search & Filter Bar */}
          <form onSubmit={handleSearch} className="bg-white p-4 rounded-3xl border border-slate-200 shadow-sm grid grid-cols-1 md:grid-cols-12 gap-3">
            <div className="md:col-span-5 flex items-center gap-2 bg-slate-50 border border-slate-200 rounded-2xl px-3.5 py-2.5">
              <Search className="w-4 h-4 text-purple-600 flex-shrink-0" />
              <input 
                type="text"
                placeholder="Job title, skill (e.g. React, Python)..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="bg-transparent text-xs font-bold text-slate-800 placeholder:text-slate-400 focus:outline-hidden w-full"
              />
            </div>

            <div className="md:col-span-4 flex items-center gap-2 bg-slate-50 border border-slate-200 rounded-2xl px-3.5 py-2.5">
              <MapPin className="w-4 h-4 text-purple-600 flex-shrink-0" />
              <input 
                type="text"
                placeholder="City, region, or 'Remote'..."
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                className="bg-transparent text-xs font-bold text-slate-800 placeholder:text-slate-400 focus:outline-hidden w-full"
              />
            </div>

            <div className="md:col-span-3 flex gap-2">
              <button 
                type="submit"
                className="w-full bg-purple-600 hover:bg-purple-700 text-white rounded-2xl text-xs font-bold py-2.5 transition flex items-center justify-center gap-2 shadow-xs cursor-pointer"
              >
                <Search className="w-4 h-4" />
                <span>Search</span>
              </button>
            </div>
          </form>

          {/* Quick Filter Chips */}
          <div className="flex flex-wrap items-center justify-between gap-3 pt-1">
            <div className="flex items-center gap-2 overflow-x-auto pb-1">
              <span className="text-xs font-black text-slate-400 flex items-center gap-1 uppercase tracking-wider mr-1">
                <Filter className="w-3.5 h-3.5" /> Type:
              </span>
              {['all', 'Full-time', 'Remote', 'Internship', 'Contract'].map((type) => (
                <button
                  key={type}
                  onClick={() => { setJobType(type); fetchJobs(); }}
                  className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition cursor-pointer ${
                    jobType === type
                      ? 'bg-purple-600 text-white shadow-xs'
                      : 'bg-white border border-slate-200 text-slate-600 hover:bg-slate-100'
                  }`}
                >
                  {type === 'all' ? 'All Roles' : type}
                </button>
              ))}
            </div>

            <span className="text-xs font-bold text-slate-400">
              Showing {jobs.length} open positions
            </span>
          </div>

          {/* Job Listings Grid */}
          {loading ? (
            <div className="text-center py-20 space-y-3">
              <RefreshCw className="w-8 h-8 text-purple-600 animate-spin mx-auto" />
              <p className="text-xs font-bold text-slate-400">Loading catalog positions...</p>
            </div>
          ) : jobs.length === 0 ? (
            <div className="bg-white p-12 rounded-3xl border border-slate-200 text-center space-y-3">
              <Briefcase className="w-8 h-8 text-slate-300 mx-auto" />
              <h3 className="text-sm font-black text-slate-800">No jobs matched your query</h3>
              <p className="text-xs text-slate-400">Try adjusting your keyword filters or location search.</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {jobs.map((job) => {
                const id = job.job_id || job.id;
                const isSaved = savedJobIds.has(id);

                return (
                  <div 
                    key={id}
                    className="bg-white p-6 rounded-3xl border border-slate-200 hover:border-purple-300 transition shadow-xs hover:shadow-md space-y-4 flex flex-col justify-between"
                  >
                    <div className="space-y-3">
                      {/* Top Row: Company & Bookmark */}
                      <div className="flex justify-between items-start">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 rounded-xl bg-purple-50 border border-purple-100 flex items-center justify-center text-purple-600 font-bold">
                            <Building2 className="w-5 h-5" />
                          </div>
                          <div>
                            <h4 className="text-xs font-bold text-slate-400">{job.company_name || job.company || "Enterprise Employer"}</h4>
                            <h3 className="text-base font-black text-slate-900 line-clamp-1">{job.title}</h3>
                          </div>
                        </div>

                        <button 
                          onClick={(e) => handleSaveJob(id, e)}
                          className={`p-2 rounded-xl transition cursor-pointer ${
                            isSaved 
                              ? 'bg-purple-50 text-purple-600 border border-purple-200' 
                              : 'text-slate-400 hover:bg-slate-100 border border-slate-200'
                          }`}
                          title="Save Position"
                        >
                          <Bookmark className={`w-4 h-4 ${isSaved ? 'fill-purple-600' : ''}`} />
                        </button>
                      </div>

                      {/* Location & Salary Chips */}
                      <div className="flex flex-wrap items-center gap-2 text-xs font-bold text-slate-500">
                        <span className="flex items-center gap-1 bg-slate-50 border border-slate-200 px-2.5 py-1 rounded-lg">
                          <MapPin className="w-3.5 h-3.5 text-purple-600" /> {job.location || 'Remote'}
                        </span>
                        {job.salary_range && (
                          <span className="bg-purple-50 text-purple-700 border border-purple-100 px-2.5 py-1 rounded-lg">
                            {job.salary_range}
                          </span>
                        )}
                      </div>

                      {/* Required Skills */}
                      {job.skills && job.skills.length > 0 && (
                        <div className="flex flex-wrap gap-1.5 pt-1">
                          {job.skills.map((skill, idx) => (
                            <span key={idx} className="text-[10px] font-bold bg-slate-100 text-slate-700 px-2 py-0.5 rounded-md">
                              {skill}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>

                    {/* Bottom Action Footer */}
                    <div className="pt-3 border-t border-slate-100 flex items-center justify-between">
                      {job.semantic_match_score ? (
                        <span className="text-[11px] font-black text-purple-700 bg-purple-50 border border-purple-200 px-2.5 py-1 rounded-full flex items-center gap-1">
                          <Sparkles className="w-3 h-3 text-purple-600" /> {Math.round(job.semantic_match_score)}% AI Match
                        </span>
                      ) : (
                        <span className="text-[11px] font-bold text-slate-400">Full Time Role</span>
                      )}

                      <button 
                        onClick={() => window.location.href = `/discovery`}
                        className="text-xs font-black text-purple-600 hover:text-purple-700 flex items-center gap-1 cursor-pointer"
                      >
                        <span>Apply via Swipe Feed</span>
                        <ArrowUpRight className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

const FALLBACK_JOBS = [
  {
    job_id: "job-101",
    company_name: "SwipeX Tech",
    title: "Senior Python Backend Engineer",
    location: "Remote / Bengaluru",
    salary_range: "₹18 LPA - ₹28 LPA",
    skills: ["Python", "FastAPI", "PostgreSQL", "Docker"],
    semantic_match_score: 94.5
  },
  {
    job_id: "job-102",
    company_name: "Razorpay",
    title: "Frontend React Developer",
    location: "Bengaluru, India",
    salary_range: "₹14 LPA - ₹22 LPA",
    skills: ["React", "TypeScript", "Tailwind CSS"],
    semantic_match_score: 89.0
  },
  {
    job_id: "job-103",
    company_name: "TCS Innovation Labs",
    title: "Full Stack AI Engineer",
    location: "Hyderabad, India",
    salary_range: "₹12 LPA - ₹20 LPA",
    skills: ["Python", "Django", "React", "PyTorch"],
    semantic_match_score: 86.2
  },
  {
    job_id: "job-104",
    company_name: "Swiggy",
    title: "DevOps & Cloud Infrastructure Specialist",
    location: "Remote",
    salary_range: "₹16 LPA - ₹26 LPA",
    skills: ["Kubernetes", "AWS", "CI/CD", "Terraform"],
    semantic_match_score: 82.0
  }
];