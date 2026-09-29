import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Zap, Sparkles, Building2, User, FileText, Bell, LogOut, Search, 
  Menu, X, Command, Settings, BarChart2, TrendingUp, CheckCircle2, 
  AlertCircle, ArrowUpRight, Award, Target, ChevronRight
} from 'lucide-react';

export default function Analytics() {
  const navigate = useNavigate();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isProfileDropdownOpen, setIsProfileDropdownOpen] = useState(false);

  // Analytics Metrics Data
  const metrics = {
    avgAtsScore: 88,
    atsTrend: "+12% this month",
    totalApplications: 14,
    interviewRate: "28%",
    topSkillGaps: [
      { name: "GraphQL", frequency: "High (45% of MNC roles)" },
      { name: "Docker / Kubernetes", frequency: "Medium (30% of Startup roles)" },
      { name: "Jest / Unit Testing", frequency: "Low (15% of roles)" }
    ],
    funnel: [
      { stage: "Jobs Discovered", count: 120, percentage: "100%" },
      { stage: "Applied (Swiped Right)", count: 14, percentage: "11.6%" },
      { stage: "Shortlisted", count: 6, percentage: "42.8%" },
      { stage: "Interview Calls", count: 4, percentage: "28.5%" }
    ]
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex font-sans selection:bg-purple-500 selection:text-white">
      
      {/* 1. GLOBAL LEFT SIDEBAR NAVIGATION */}
      <aside className={`
        fixed lg:static inset-y-0 left-0 z-50 w-64 bg-white border-r border-slate-200 p-5 flex flex-col justify-between transition-transform duration-300
        ${isMobileMenuOpen ? 'translate-x-0 shadow-2xl' : '-translate-x-full lg:translate-x-0'}
      `}>
        <div className="space-y-6">
          <div className="flex justify-between items-center pb-4 border-b border-slate-100">
            <div className="flex items-center gap-2.5 cursor-pointer" onClick={() => navigate('/')}>
              <div className="w-9 h-9 rounded-xl bg-purple-600 flex items-center justify-center shadow-md shadow-purple-600/20">
                <Zap className="w-5 h-5 text-white fill-white" />
              </div>
              <span className="text-xl font-black tracking-tight text-slate-900">
                Swipe<span className="text-purple-600">X</span>
              </span>
            </div>
            
            <button 
              onClick={() => setIsMobileMenuOpen(false)} 
              className="lg:hidden p-1 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          <nav className="space-y-1.5 text-xs font-bold">
            <button 
              onClick={() => { navigate('/discovery'); setIsMobileMenuOpen(false); }}
              className="w-full py-2.5 px-3 text-slate-600 hover:bg-slate-100 rounded-xl flex items-center gap-3 transition"
            >
              <span className="text-sm">🔥</span>
              <span>Discover (Swipe View)</span>
            </button>

            <button 
              onClick={() => { navigate('/job-search'); setIsMobileMenuOpen(false); }}
              className="w-full py-2.5 px-3 text-slate-600 hover:bg-slate-100 rounded-xl flex items-center gap-3 transition"
            >
              <span className="text-sm">🔍</span>
              <span>Search & Explore</span>
            </button>

            <button 
  onClick={() => { navigate('/companies'); setIsMobileMenuOpen(false); }} 
  className={`w-full py-2.5 px-3 rounded-xl flex items-center gap-3 transition ${
    window.location.pathname === '/companies' 
      ? 'bg-purple-50 text-purple-700 shadow-2xs' 
      : 'text-slate-600 hover:bg-slate-100'
  }`}
>
  <span className="text-sm">🏢</span>
  <span>Company Directory</span>
</button>

            <button 
              onClick={() => { navigate('/resume-upload'); setIsMobileMenuOpen(false); }}
              className="w-full py-2.5 px-3 text-slate-600 hover:bg-slate-100 rounded-xl flex items-center gap-3 transition"
            >
              <span className="text-sm">📑</span>
              <span>Resume & ATS Builder</span>
            </button>

            <button 
              onClick={() => { navigate('/dashboard'); setIsMobileMenuOpen(false); }}
              className="w-full py-2.5 px-3 text-slate-600 hover:bg-slate-100 rounded-xl flex items-center gap-3 transition"
            >
              <span className="text-sm">📊</span>
              <span>Applications Tracker</span>
            </button>

            <button 
              onClick={() => { navigate('/analytics'); setIsMobileMenuOpen(false); }}
              className="w-full py-2.5 px-3 bg-purple-50 text-purple-700 rounded-xl flex items-center gap-3 shadow-2xs"
            >
              <span className="text-sm">📈</span>
              <span>Analytics & Insights</span>
            </button>

            <button 
              onClick={() => { navigate('/profile'); setIsMobileMenuOpen(false); }}
              className="w-full py-2.5 px-3 text-slate-600 hover:bg-slate-100 rounded-xl flex items-center gap-3 transition"
            >
              <span className="text-sm">👤</span>
              <span>Profile</span>
            </button>

            <button 
              onClick={() => { navigate('/settings'); setIsMobileMenuOpen(false); }}
              className="w-full py-2.5 px-3 text-slate-600 hover:bg-slate-100 rounded-xl flex items-center gap-3 transition"
            >
              <span className="text-sm">⚙️</span>
              <span>Settings</span>
            </button>
          </nav>
        </div>

        <div className="pt-3 border-t border-slate-100">
          <button 
            onClick={() => navigate('/login')}
            className="w-full py-2.5 px-3 text-rose-600 hover:bg-rose-50 rounded-xl font-bold text-xs flex items-center gap-2 transition"
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

      {/* 2. MAIN WORKSPACE */}
      <div className="flex-grow flex flex-col min-w-0">
        
        {/* Global Header */}
        <header className="w-full bg-white/90 backdrop-blur-md border-b border-slate-200 sticky top-0 z-30 px-6 py-3 flex justify-between items-center shadow-2xs">
          <div className="flex items-center gap-4">
            <button 
              onClick={() => setIsMobileMenuOpen(true)}
              className="lg:hidden p-2 rounded-xl text-slate-600 hover:bg-slate-100 transition"
              title="Open Menu"
            >
              <Menu className="w-5 h-5" />
            </button>

            <h1 className="text-lg font-black text-slate-900 tracking-tight hidden sm:block">Career Analytics & Insights</h1>
          </div>

          <div className="flex items-center gap-3">
            <button 
              onClick={() => navigate('/notifications')}
              className="p-2 text-slate-600 hover:bg-slate-100 rounded-xl relative transition"
              title="Notifications"
            >
              <Bell className="w-4 h-4" />
              <span className="bg-purple-600 text-white text-[9px] font-black w-4 h-4 rounded-full absolute -top-0.5 -right-0.5 ring-2 ring-white flex items-center justify-center">
                3
              </span>
            </button>

            <div className="relative">
              <div 
                onClick={() => setIsProfileDropdownOpen(!isProfileDropdownOpen)}
                className="w-8 h-8 rounded-xl bg-purple-100 border border-purple-300 text-purple-700 font-bold text-xs flex items-center justify-center cursor-pointer hover:bg-purple-200 transition"
              >
                AM
              </div>

              {isProfileDropdownOpen && (
                <div className="absolute right-0 mt-2 w-48 bg-white border border-slate-200 rounded-2xl shadow-xl p-1.5 z-50 text-xs font-bold space-y-0.5">
                  <div className="px-3 py-2 border-b border-slate-100 mb-1">
                    <p className="text-slate-900 font-black">Alex Morgan</p>
                    <p className="text-[10px] text-slate-400 font-medium">alex@example.com</p>
                  </div>
                  <button onClick={() => navigate('/profile')} className="w-full py-2 px-3 hover:bg-slate-100 rounded-xl text-slate-700 flex items-center gap-2 transition">
                    <User className="w-3.5 h-3.5 text-slate-400" /> Profile
                  </button>
                  <button onClick={() => navigate('/settings')} className="w-full py-2 px-3 hover:bg-slate-100 rounded-xl text-slate-700 flex items-center gap-2 transition">
                    <Settings className="w-3.5 h-3.5 text-slate-400" /> Settings
                  </button>
                  <div className="border-t border-slate-100 my-1"></div>
                  <button onClick={() => navigate('/login')} className="w-full py-2 px-3 hover:bg-rose-50 text-rose-600 rounded-xl flex items-center gap-2 transition">
                    <LogOut className="w-3.5 h-3.5" /> Logout
                  </button>
                </div>
              )}
            </div>
          </div>
        </header>

        {/* 3. ANALYTICS WORKSPACE CONTENT */}
        <main className="flex-grow p-6 max-w-6xl mx-auto w-full space-y-6">
          
          {/* Top High-Level Performance Metrics */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="bg-white border border-slate-200 rounded-3xl p-5 shadow-2xs space-y-2">
              <div className="flex justify-between items-center text-slate-400">
                <span className="text-[10px] font-bold uppercase tracking-wider">Average ATS Score</span>
                <Award className="w-4 h-4 text-purple-600" />
              </div>
              <p className="text-3xl font-black text-slate-900">{metrics.avgAtsScore}%</p>
              <p className="text-xs font-bold text-emerald-600 flex items-center gap-1">
                <TrendingUp className="w-3.5 h-3.5" /> {metrics.atsTrend}
              </p>
            </div>

            <div className="bg-white border border-slate-200 rounded-3xl p-5 shadow-2xs space-y-2">
              <div className="flex justify-between items-center text-slate-400">
                <span className="text-[10px] font-bold uppercase tracking-wider">Interview Conversion Rate</span>
                <Target className="w-4 h-4 text-emerald-600" />
              </div>
              <p className="text-3xl font-black text-slate-900">{metrics.interviewRate}</p>
              <p className="text-xs text-slate-500 font-medium">Top 5% among React candidates</p>
            </div>

            <div className="bg-white border border-slate-200 rounded-3xl p-5 shadow-2xs space-y-2">
              <div className="flex justify-between items-center text-slate-400">
                <span className="text-[10px] font-bold uppercase tracking-wider">Active Applications</span>
                <BarChart2 className="w-4 h-4 text-purple-600" />
              </div>
              <p className="text-3xl font-black text-slate-900">{metrics.totalApplications}</p>
              <p className="text-xs text-slate-500 font-medium">4 interview rounds active</p>
            </div>
          </div>

          {/* Application Funnel & Skill Gap Analysis */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            
            {/* Funnel Progress */}
            <div className="bg-white border border-slate-200 rounded-3xl p-6 shadow-2xs space-y-4">
              <h3 className="text-xs font-black text-slate-900 uppercase tracking-wider">Application Funnel</h3>
              <div className="space-y-3">
                {metrics.funnel.map((item, index) => (
                  <div key={index} className="space-y-1">
                    <div className="flex justify-between text-xs font-bold text-slate-700">
                      <span>{item.stage}</span>
                      <span>{item.count} ({item.percentage})</span>
                    </div>
                    <div className="w-full bg-slate-100 rounded-full h-2">
                      <div 
                        className="bg-purple-600 h-2 rounded-full transition-all duration-500" 
                        style={{ width: item.percentage }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* AI Skill Gap Analysis */}
            <div className="bg-white border border-slate-200 rounded-3xl p-6 shadow-2xs space-y-4">
              <h3 className="text-xs font-black text-slate-900 uppercase tracking-wider flex items-center gap-1.5">
                <AlertCircle className="w-4 h-4 text-amber-500" /> Skill Gap Recommendations
              </h3>
              <p className="text-xs text-slate-500 font-medium">
                Our AI matched your resume against target roles. Learning these skills will increase your match score.
              </p>

              <div className="space-y-2.5">
                {metrics.topSkillGaps.map((skill, index) => (
                  <div key={index} className="p-3 bg-slate-50 border border-slate-200/80 rounded-2xl flex justify-between items-center text-xs">
                    <div>
                      <p className="font-bold text-slate-900">{skill.name}</p>
                      <p className="text-[10px] text-slate-400 font-medium">{skill.frequency}</p>
                    </div>
                    <button 
                      onClick={() => navigate('/resume-upload')}
                      className="px-3 py-1 bg-purple-50 text-purple-700 font-bold rounded-lg border border-purple-200 text-[10px] hover:bg-purple-100 transition"
                    >
                      Update Resume
                    </button>
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