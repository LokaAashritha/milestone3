import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  ShieldCheck, Users, Activity, LogOut, Menu, X, 
  Search, CheckCircle2, UserCheck, UserX, ShieldAlert, Sparkles, Filter
} from 'lucide-react';

const SEEDED_USERS = [
  {
    id: 1,
    name: "Alex Morgan",
    email: "alex@example.com",
    role: "Candidate",
    organization: "N/A",
    status: "Active",
    joinedDate: "Aug 12, 2026"
  },
  {
    id: 2,
    name: "NexusTech Hiring",
    email: "recruiter@nexustech.com",
    role: "Recruiter",
    organization: "NexusTech Global",
    status: "Active",
    joinedDate: "Jul 28, 2026"
  },
  {
    id: 3,
    name: "Priya Sharma",
    email: "priya.sharma@example.com",
    role: "Candidate",
    organization: "N/A",
    status: "Active",
    joinedDate: "Sep 01, 2026"
  },
  {
    id: 4,
    name: "ApexTalent HR",
    email: "hr@apextalent.io",
    role: "Recruiter",
    organization: "ApexTalent Inc",
    status: "Suspended",
    joinedDate: "Jun 15, 2026"
  }
];

export default function AdminUsers() {
  const navigate = useNavigate();
  const [users, setUsers] = useState(SEEDED_USERS);
  const [searchQuery, setSearchQuery] = useState('');
  const [roleFilter, setRoleFilter] = useState('All');
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [toastMessage, setToastMessage] = useState(null);

  const showToast = (msg) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 2500);
  };

  const toggleUserStatus = (id) => {
    setUsers(prev => prev.map(u => {
      if (u.id === id) {
        const newStatus = u.status === 'Active' ? 'Suspended' : 'Active';
        showToast(`Account status updated to ${newStatus}`);
        return { ...u, status: newStatus };
      }
      return u;
    }));
  };

  const filteredUsers = users.filter(user => {
    const matchesSearch = user.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          user.email.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          user.organization.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesRole = roleFilter === 'All' || user.role === roleFilter;
    return matchesSearch && matchesRole;
  });

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex font-sans selection:bg-purple-500 selection:text-white">
      
      {/* Toast Alert */}
      {toastMessage && (
        <div className="fixed top-6 right-6 z-50 bg-slate-900 text-white px-4 py-2.5 rounded-2xl shadow-xl text-xs font-bold flex items-center gap-2 animate-bounce">
          <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          {toastMessage}
        </div>
      )}

      {/* 1. ADMIN SIDEBAR */}
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
              className="w-full py-2.5 px-3 text-slate-400 hover:bg-slate-900 hover:text-white rounded-xl flex items-center gap-3 transition cursor-pointer"
            >
              <Activity className="w-4 h-4" />
              <span>Platform System Control</span>
            </button>

            <button 
              onClick={() => { navigate('/admin-users'); setIsMobileMenuOpen(false); }}
              className="w-full py-2.5 px-3 bg-purple-600 text-white rounded-xl flex items-center gap-3 shadow-2xs cursor-pointer"
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
        
        {/* Header */}
        <header className="w-full bg-white/90 backdrop-blur-md border-b border-slate-200 sticky top-0 z-30 px-6 py-3 flex justify-between items-center shadow-2xs">
          <div className="flex items-center gap-4">
            <button onClick={() => setIsMobileMenuOpen(true)} className="lg:hidden p-2 text-slate-600">
              <Menu className="w-5 h-5" />
            </button>
            <h1 className="text-lg font-black text-slate-900 hidden sm:block">User Account Governance & Verification</h1>
          </div>

          <div className="flex items-center gap-3">
            <span className="text-xs font-bold bg-purple-50 text-purple-700 border border-purple-200 px-3 py-1 rounded-xl">
              {users.length} Total Registered Accounts
            </span>
          </div>
        </header>

        {/* Workspace Body */}
        <main className="flex-grow p-6 max-w-6xl mx-auto w-full space-y-6">
          
          {/* Search & Filter Controls */}
          <div className="flex flex-col sm:flex-row justify-between items-center gap-4 bg-white p-4 rounded-3xl border border-slate-200 shadow-2xs">
            <div className="relative w-full sm:w-80">
              <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
              <input 
                type="text" 
                placeholder="Search name, email, or company..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium focus:outline-none focus:border-purple-600 transition"
              />
            </div>

            <div className="flex items-center gap-3 w-full sm:w-auto justify-end">
              <select 
                value={roleFilter}
                onChange={(e) => setRoleFilter(e.target.value)}
                className="px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-bold text-slate-700 focus:outline-none focus:border-purple-600 cursor-pointer"
              >
                <option value="All">All Roles</option>
                <option value="Candidate">Candidates Only</option>
                <option value="Recruiter">Recruiters Only</option>
              </select>
            </div>
          </div>

          {/* User Audit Table */}
          <div className="bg-white border border-slate-200 rounded-3xl overflow-hidden shadow-2xs">
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="bg-slate-50 border-b border-slate-200 text-[10px] uppercase font-black text-slate-400 tracking-wider">
                    <th className="p-4">Account Holder</th>
                    <th className="p-4">Role</th>
                    <th className="p-4">Organization</th>
                    <th className="p-4">Status</th>
                    <th className="p-4">Joined Date</th>
                    <th className="p-4 text-right">Governance Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 text-xs font-medium text-slate-700">
                  {filteredUsers.map((u) => (
                    <tr key={u.id} className="hover:bg-slate-50/80 transition">
                      <td className="p-4">
                        <p className="font-bold text-slate-900">{u.name}</p>
                        <p className="text-[10px] text-slate-400">{u.email}</p>
                      </td>
                      <td className="p-4">
                        <span className={`text-[10px] font-black px-2.5 py-0.5 rounded-full ${
                          u.role === 'Recruiter' ? 'bg-purple-100 text-purple-700 border border-purple-200' : 'bg-slate-100 text-slate-700 border border-slate-200'
                        }`}>
                          {u.role}
                        </span>
                      </td>
                      <td className="p-4 font-bold text-slate-800">{u.organization}</td>
                      <td className="p-4">
                        <span className={`text-[10px] font-bold px-2 py-0.5 rounded-md ${
                          u.status === 'Active' ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' : 'bg-rose-50 text-rose-700 border border-rose-200'
                        }`}>
                          {u.status}
                        </span>
                      </td>
                      <td className="p-4 text-slate-500">{u.joinedDate}</td>
                      <td className="p-4 text-right">
                        <button 
                          onClick={() => toggleUserStatus(u.id)}
                          className={`px-3 py-1.5 rounded-xl font-bold text-xs transition cursor-pointer ${
                            u.status === 'Active' 
                              ? 'bg-rose-50 text-rose-600 hover:bg-rose-100 border border-rose-200' 
                              : 'bg-emerald-50 text-emerald-600 hover:bg-emerald-100 border border-emerald-200'
                          }`}
                        >
                          {u.status === 'Active' ? 'Suspend Account' : 'Reactivate Account'}
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

        </main>
      </div>

    </div>
  );
}