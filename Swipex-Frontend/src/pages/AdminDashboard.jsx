import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  ShieldCheck, Users, Briefcase, Activity, Zap, LogOut, 
  Menu, X, Bell, Search, AlertCircle, CheckCircle2, 
  Settings, Server, Cpu, RefreshCw, Sliders
} from 'lucide-react';

export default function AdminDashboard() {
  const navigate = useNavigate();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [toastMessage, setToastMessage] = useState(null);

  // System Health States
  const [atsEngineActive, setAtsEngineActive] = useState(true);
  const [autoMatchmaking, setAutoMatchmaking] = useState(true);

  const showToast = (msg) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 2500);
  };

  const systemLogs = [
    { id: 1, event: "ATS Matching Engine re-indexed 42 new candidate profiles", time: "2 mins ago", status: "Success" },
    { id: 2, event: "Recruiter 'NexusTech' published job posting #804", time: "14 mins ago", status: "Success" },
    { id: 3, event: "Candidate resume parsing API latency spike detected (240ms)", time: "1 hour ago", status: "Warning" }
  ];

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex font-sans selection:bg-purple-500 selection:text-white">
      
      {/* Toast Alert */}
      {toastMessage && (
        <div className="fixed top-6 right-6 z-50 bg-slate-900 text-white px-4 py-2.5 rounded-2xl shadow-xl text-xs font-bold flex items-center gap-2 animate-bounce">
          <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          {toastMessage}
        </div>
      )}

      {/* 1. ADMIN PORTAL SIDEBAR */}
      <aside className={`
        fixed lg:static inset-y-0 left-0 z-50 w-64 bg-slate-950 text-white p-5 flex flex-col justify-between transition-transform duration-300
        ${isMobileMenuOpen ? 'translate-x-0 shadow-2xl' : '-translate-x-full lg:translate-x-0'}
      `}>
        <div className="space-y-6">
          <div className="flex justify-between items-center pb-4 border-b border-slate-800">
            <div className="flex items-center gap-2.5 cursor-pointer" onClick={() => navigate('/')}>
              <div className="w-9 h-9 rounded-xl bg-purple-600 flex items-center justify-center shadow-md shadow-purple-600/20">
                <ShieldCheck className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-black tracking-tight text-white">
                Swipe<span className="text-purple-400">X</span> <span className="text-[10px] font-bold text-slate-400 block uppercase tracking-wider">Admin</span>
              </span>
            </div>
            
            <button onClick={() => setIsMobileMenuOpen(false)} className="lg:hidden p-1 text-slate-400">
              <X className="w-5 h-5" />
            </button>
          </div>

          <nav className="space-y-1.5 text-xs font-bold">
            <button 
              onClick={() => { navigate('/admin-dashboard'); setIsMobileMenuOpen(false); }}
              className="w-full py-2.5 px-3 bg-purple-600 text-white rounded-xl flex items-center gap-3 shadow-2xs cursor-pointer"
            >
              <Activity className="w-4 h-4" />
              <span>Platform System Control</span>
            </button>

            <button 
              onClick={() => { navigate('/admin-users'); setIsMobileMenuOpen(false); }}
              className="w-full py-2.5 px-3 text-slate-400 hover:bg-slate-900 hover:text-white rounded-xl flex items-center gap-3 transition cursor-pointer"
            >
              <Users className="w-4 h-4" />
              <span>User & Recruiter Audit</span>
            </button>
          </nav>
        </div>

        <div className="pt-3 border-t border-slate-800">
          <button 
            onClick={() => navigate('/login')}
            className="w-full py-2.5 px-3 text-rose-400 hover:bg-rose-950/30 rounded-xl font-bold text-xs flex items-center gap-2 transition cursor-pointer"
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
        
        {/* Top Header */}
        <header className="w-full bg-white/90 backdrop-blur-md border-b border-slate-200 sticky top-0 z-30 px-6 py-3 flex justify-between items-center shadow-2xs">
          <div className="flex items-center gap-4">
            <button onClick={() => setIsMobileMenuOpen(true)} className="lg:hidden p-2 text-slate-600">
              <Menu className="w-5 h-5" />
            </button>
            <h1 className="text-lg font-black text-slate-900 hidden sm:block">Platform System Administration</h1>
          </div>

          <div className="flex items-center gap-3">
            <span className="text-xs font-bold bg-emerald-50 text-emerald-700 border border-emerald-200 px-3 py-1 rounded-xl flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping" /> System Operational
            </span>
          </div>
        </header>

        {/* Workspace Body */}
        <main className="flex-grow p-6 max-w-6xl mx-auto w-full space-y-6">
          
          {/* Key Platform Metrics */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-white border border-slate-200 p-4 rounded-3xl shadow-2xs space-y-1">
              <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Total Candidates</p>
              <p className="text-2xl font-black text-slate-900">1,420 Users</p>
            </div>
            <div className="bg-white border border-slate-200 p-4 rounded-3xl shadow-2xs space-y-1">
              <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Verified Recruiters</p>
              <p className="text-2xl font-black text-purple-600">84 Accounts</p>
            </div>
            <div className="bg-white border border-slate-200 p-4 rounded-3xl shadow-2xs space-y-1">
              <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Active Job Posts</p>
              <p className="text-2xl font-black text-emerald-600">312 Roles</p>
            </div>
            <div className="bg-white border border-slate-200 p-4 rounded-3xl shadow-2xs space-y-1">
              <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">ATS API Latency</p>
              <p className="text-2xl font-black text-slate-900">42 ms</p>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            
            {/* System Controls & Feature Toggles */}
            <div className="lg:col-span-2 bg-white border border-slate-200 rounded-3xl p-6 shadow-2xs space-y-5">
              <h2 className="text-xs font-black text-slate-900 uppercase tracking-wider flex items-center gap-2">
                <Sliders className="w-4 h-4 text-purple-600" /> System Feature Flags & Operations
              </h2>

              <div className="space-y-4 text-xs font-bold">
                <div className="p-4 bg-slate-50 border border-slate-200 rounded-2xl flex justify-between items-center">
                  <div>
                    <p className="text-slate-900 font-bold">AI ATS Matchmaking Engine</p>
                    <p className="text-[10px] text-slate-400 font-medium">Controls background calculations of candidate match percentages</p>
                  </div>
                  <button 
                    onClick={() => {
                      setAtsEngineActive(!atsEngineActive);
                      showToast(`ATS Engine ${!atsEngineActive ? 'Enabled' : 'Disabled'}`);
                    }}
                    className={`px-3 py-1.5 rounded-xl text-xs font-bold transition cursor-pointer ${
                      atsEngineActive ? 'bg-emerald-600 text-white' : 'bg-slate-300 text-slate-700'
                    }`}
                  >
                    {atsEngineActive ? 'Active' : 'Paused'}
                  </button>
                </div>

                <div className="p-4 bg-slate-50 border border-slate-200 rounded-2xl flex justify-between items-center">
                  <div>
                    <p className="text-slate-900 font-bold">Automated Recruiter Notification Pipeline</p>
                    <p className="text-[10px] text-slate-400 font-medium">Triggers automated emails on candidate shortlist status changes</p>
                  </div>
                  <button 
                    onClick={() => {
                      setAutoMatchmaking(!autoMatchmaking);
                      showToast(`Automated Notifications ${!autoMatchmaking ? 'Enabled' : 'Disabled'}`);
                    }}
                    className={`px-3 py-1.5 rounded-xl text-xs font-bold transition cursor-pointer ${
                      autoMatchmaking ? 'bg-emerald-600 text-white' : 'bg-slate-300 text-slate-700'
                    }`}
                  >
                    {autoMatchmaking ? 'Active' : 'Paused'}
                  </button>
                </div>
              </div>
            </div>

            {/* Realtime System Logs Feed */}
            <div className="bg-white border border-slate-200 rounded-3xl p-6 shadow-2xs space-y-4">
              <h2 className="text-xs font-black text-slate-900 uppercase tracking-wider flex items-center gap-2">
                <Server className="w-4 h-4 text-purple-600" /> System Activity Log
              </h2>

              <div className="space-y-3">
                {systemLogs.map((log) => (
                  <div key={log.id} className="p-3 bg-slate-50 border border-slate-200/80 rounded-2xl space-y-1">
                    <div className="flex justify-between items-center text-[10px]">
                      <span className={`font-bold ${log.status === 'Success' ? 'text-emerald-600' : 'text-amber-600'}`}>{log.status}</span>
                      <span className="text-slate-400 font-medium">{log.time}</span>
                    </div>
                    <p className="text-xs font-semibold text-slate-800 leading-snug">{log.event}</p>
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