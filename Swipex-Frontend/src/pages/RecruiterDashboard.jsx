import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Building2, PlusCircle, Users, CheckSquare, Zap, LogOut, 
  Menu, X, Bell, User, Briefcase, TrendingUp, Sparkles, ArrowUpRight, Clock, ArrowRight
} from 'lucide-react';

export default function RecruiterDashboard() {
  const navigate = useNavigate();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isProfileDropdownOpen, setIsProfileDropdownOpen] = useState(false);

  // Recruiter Dashboard Metrics
  const activePostings = [
    {
      id: 1,
      title: "Senior React Architect",
      category: "MNCs",
      applicantsCount: 42,
      shortlistedCount: 8,
      postedDate: "2 days ago",
      status: "Active"
    },
    {
      id: 2,
      title: "Frontend Developer Intern",
      category: "Startups",
      applicantsCount: 18,
      shortlistedCount: 4,
      postedDate: "5 hours ago",
      status: "Active"
    }
  ];

  // Seeded Recent Applicants Data for Direct Inspection
  const recentApplicants = [
    { id: 101, name: "Alex Morgan", roleApplied: "Senior React Architect", atsScore: 96, status: "Shortlisted" },
    { id: 102, name: "Priya Sharma", roleApplied: "Senior React Architect", atsScore: 88, status: "Under Review" },
    { id: 103, name: "Rahul Verma", roleApplied: "Frontend Developer Intern", atsScore: 92, status: "Shortlisted" }
  ];

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex font-sans selection:bg-purple-500 selection:text-white">
      
      {/* 1. RECRUITER PORTAL SIDEBAR */}
      <aside className={`
        fixed lg:static inset-y-0 left-0 z-50 w-64 bg-slate-900 text-white p-5 flex flex-col justify-between transition-transform duration-300
        ${isMobileMenuOpen ? 'translate-x-0 shadow-2xl' : '-translate-x-full lg:translate-x-0'}
      `}>
        <div className="space-y-6">
          <div className="flex justify-between items-center pb-4 border-b border-slate-800">
            <div className="flex items-center gap-2.5 cursor-pointer" onClick={() => navigate('/')}>
              <div className="w-9 h-9 rounded-xl bg-purple-600 flex items-center justify-center shadow-md shadow-purple-600/20">
                <Zap className="w-5 h-5 text-white fill-white" />
              </div>
              <span className="text-xl font-black tracking-tight text-white">
                Swipe<span className="text-purple-400">X</span> <span className="text-[10px] font-bold text-slate-400 block uppercase tracking-wider">Recruiter</span>
              </span>
            </div>
            
            <button onClick={() => setIsMobileMenuOpen(false)} className="lg:hidden p-1 text-slate-400">
              <X className="w-5 h-5" />
            </button>
          </div>

          <nav className="space-y-1.5 text-xs font-bold">
            <button 
              onClick={() => { navigate('/recruiter-dashboard'); setIsMobileMenuOpen(false); }}
              className="w-full py-2.5 px-3 bg-purple-600 text-white rounded-xl flex items-center gap-3 shadow-2xs"
            >
              <Building2 className="w-4 h-4" />
              <span>Overview Dashboard</span>
            </button>

            <button 
              onClick={() => { navigate('/post-job'); setIsMobileMenuOpen(false); }}
              className="w-full py-2.5 px-3 text-slate-400 hover:bg-slate-800 hover:text-white rounded-xl flex items-center gap-3 transition"
            >
              <PlusCircle className="w-4 h-4" />
              <span>Job Posting</span>
            </button>

            <button 
              onClick={() => { navigate('/ats-ranker'); setIsMobileMenuOpen(false); }}
              className="w-full py-2.5 px-3 text-slate-400 hover:bg-slate-800 hover:text-white rounded-xl flex items-center gap-3 transition"
            >
              <CheckSquare className="w-4 h-4" />
              <span>Applicant ATS Ranker</span>
            </button>
          </nav>
        </div>

        <div className="pt-3 border-t border-slate-800">
          <button 
            onClick={() => navigate('/login')}
            className="w-full py-2.5 px-3 text-rose-400 hover:bg-rose-950/30 rounded-xl font-bold text-xs flex items-center gap-2 transition"
          >
            <LogOut className="w-3.5 h-3.5" /> Sign Out
          </button>
        </div>
      </aside>

      {/* Backdrop for Mobile Drawer */}
      {isMobileMenuOpen && (
        <div 
          className="fixed inset-0 bg-slate-950/50 backdrop-blur-xs z-40 lg:hidden" 
          onClick={() => setIsMobileMenuOpen(false)} 
        />
      )}

      {/* 2. MAIN RECRUITER WORKSPACE */}
      <div className="flex-grow flex flex-col min-w-0">
        
        {/* Top Header Bar */}
        <header className="w-full bg-white/90 backdrop-blur-md border-b border-slate-200 sticky top-0 z-30 px-6 py-3 flex justify-between items-center shadow-2xs">
          <div className="flex items-center gap-4">
            <button 
              onClick={() => setIsMobileMenuOpen(true)}
              className="lg:hidden p-2 rounded-xl text-slate-600 hover:bg-slate-100 transition"
              title="Open Menu"
            >
              <Menu className="w-5 h-5" />
            </button>

            <h1 className="text-lg font-black text-slate-900 tracking-tight hidden sm:block">Recruiter Overview Dashboard</h1>
          </div>

          <div className="flex items-center gap-3">
            <button className="p-2 text-slate-600 hover:bg-slate-100 rounded-xl relative transition">
              <Bell className="w-4 h-4" />
              <span className="bg-purple-600 text-white text-[9px] font-black w-4 h-4 rounded-full absolute -top-0.5 -right-0.5 ring-2 ring-white flex items-center justify-center">
                2
              </span>
            </button>

            <div className="relative">
              <div 
                onClick={() => setIsProfileDropdownOpen(!isProfileDropdownOpen)}
                className="w-8 h-8 rounded-xl bg-purple-100 border border-purple-300 text-purple-700 font-bold text-xs flex items-center justify-center cursor-pointer hover:bg-purple-200 transition"
              >
                HR
              </div>

              {isProfileDropdownOpen && (
                <div className="absolute right-0 mt-2 w-48 bg-white border border-slate-200 rounded-2xl shadow-xl p-1.5 z-50 text-xs font-bold space-y-0.5">
                  <div className="px-3 py-2 border-b border-slate-100 mb-1">
                    <p className="text-slate-900 font-black">NexusTech Hiring</p>
                    <p className="text-[10px] text-slate-400 font-medium">recruiter@nexustech.com</p>
                  </div>
                  <button onClick={() => navigate('/login')} className="w-full py-2 px-3 hover:bg-rose-50 text-rose-600 rounded-xl flex items-center gap-2 transition">
                    <LogOut className="w-3.5 h-3.5" /> Logout
                  </button>
                </div>
              )}
            </div>
          </div>
        </header>

        {/* Workspace Body */}
        <main className="flex-grow p-6 max-w-6xl mx-auto w-full space-y-6">
          
          {/* Quick Metrics Bar */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="bg-white border border-slate-200 p-5 rounded-3xl shadow-2xs space-y-1">
              <div className="flex justify-between items-center text-slate-400">
                <span className="text-[10px] font-bold uppercase tracking-wider">Active Job Listings</span>
                <Briefcase className="w-4 h-4 text-purple-600" />
              </div>
              <p className="text-3xl font-black text-slate-900">2</p>
              <p className="text-xs text-emerald-600 font-bold flex items-center gap-1">
                <TrendingUp className="w-3.5 h-3.5" /> +1 posted this week
              </p>
            </div>

            <div className="bg-white border border-slate-200 p-5 rounded-3xl shadow-2xs space-y-1">
              <div className="flex justify-between items-center text-slate-400">
                <span className="text-[10px] font-bold uppercase tracking-wider">Total Applicants</span>
                <Users className="w-4 h-4 text-purple-600" />
              </div>
              <p className="text-3xl font-black text-slate-900">60</p>
              <p className="text-xs text-slate-500 font-medium">Across all active roles</p>
            </div>

            <div className="bg-white border border-slate-200 p-5 rounded-3xl shadow-2xs space-y-1">
              <div className="flex justify-between items-center text-slate-400">
                <span className="text-[10px] font-bold uppercase tracking-wider">Shortlisted Candidates</span>
                <Sparkles className="w-4 h-4 text-emerald-600" />
              </div>
              <p className="text-3xl font-black text-slate-900">12</p>
              <p className="text-xs text-purple-600 font-bold">20% Shortlist Conversion Rate</p>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            
            {/* Active Job Postings List */}
            <div className="lg:col-span-2 bg-white border border-slate-200 rounded-3xl p-6 shadow-2xs space-y-4">
              <div className="flex justify-between items-center pb-3 border-b border-slate-100">
                <h3 className="text-xs font-black text-slate-900 uppercase tracking-wider">
                  Active Job Postings
                </h3>
                <button 
                  onClick={() => navigate('/post-job')}
                  className="px-3.5 py-1.5 bg-purple-600 hover:bg-purple-700 text-white font-bold text-xs rounded-xl shadow-xs transition flex items-center gap-1.5 cursor-pointer"
                >
                  <PlusCircle className="w-3.5 h-3.5" /> Create Job Listing
                </button>
              </div>

              <div className="space-y-3">
                {activePostings.map((job) => (
                  <div key={job.id} className="p-4 bg-slate-50 border border-slate-200/80 rounded-2xl flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <span className="text-[10px] font-bold bg-purple-100 text-purple-700 px-2 py-0.5 rounded-full">
                          {job.category}
                        </span>
                        <span className="text-[10px] text-slate-400 font-medium flex items-center gap-1">
                          <Clock className="w-3 h-3" /> {job.postedDate}
                        </span>
                      </div>
                      <h4 className="text-base font-black text-slate-900">{job.title}</h4>
                      <p className="text-xs text-slate-500 font-medium">
                        {job.applicantsCount} Total Applicants • {job.shortlistedCount} Shortlisted
                      </p>
                    </div>

                    <div className="flex items-center gap-2 self-end sm:self-auto">
                      <button 
                        onClick={() => navigate('/ats-ranker')}
                        className="px-3.5 py-2 bg-white border border-slate-200 hover:border-purple-600 text-purple-700 font-bold text-xs rounded-xl shadow-2xs transition flex items-center gap-1.5 cursor-pointer"
                      >
                        Rankings <ArrowUpRight className="w-3.5 h-3.5" />
                      </button>

                      {/* DIRECT REDIRECT TO CANDIDATE REVIEW */}
                      <button 
                        onClick={() => navigate('/candidate-review', { state: { applicantId: 101 } })}
                        className="px-3.5 py-2 bg-purple-50 text-purple-700 hover:bg-purple-100 font-bold text-xs rounded-xl transition flex items-center gap-1 cursor-pointer"
                      >
                        Inspect Candidates <ArrowRight className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Recent Applicants Widget (DIRECT REDIRECT TO CANDIDATE REVIEW) */}
            <div className="bg-white border border-slate-200 rounded-3xl p-6 shadow-2xs space-y-4">
              <div className="flex justify-between items-center pb-2 border-b border-slate-100">
                <h3 className="text-xs font-black text-slate-900 uppercase tracking-wider">Recent Applicants</h3>
                <button 
                  onClick={() => navigate('/ats-ranker')} 
                  className="text-[11px] font-bold text-purple-600 hover:underline cursor-pointer"
                >
                  View All
                </button>
              </div>

              <div className="space-y-3">
                {recentApplicants.map((applicant) => (
                  <div 
                    key={applicant.id}
                    onClick={() => navigate('/candidate-review', { state: { applicantId: applicant.id } })}
                    className="p-3 bg-slate-50 border border-slate-200/80 hover:border-purple-300 rounded-2xl flex justify-between items-center cursor-pointer transition"
                  >
                    <div>
                      <p className="font-bold text-xs text-slate-900">{applicant.name}</p>
                      <p className="text-[10px] text-slate-400">{applicant.roleApplied}</p>
                    </div>
                    <span className="text-xs font-black text-purple-700 bg-purple-100 px-2 py-0.5 rounded-lg flex items-center gap-1">
                      <Sparkles className="w-3 h-3" /> {applicant.atsScore}%
                    </span>
                  </div>
                ))}
              </div>
            </div>

          </div>

        </main>
      </div>

    </div>
  );
}