import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { 
  Sparkles, Search, Building2, FileText, BarChart3, Bookmark, User, Bell
} from 'lucide-react';

export const Sidebar = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems = [
    { label: 'AI Swipe Feed', path: '/discovery', icon: Sparkles },
    { label: 'Search Jobs', path: '/job-search', icon: Search },
    { label: 'Companies', path: '/companies', icon: Building2 },
    { label: 'Resume Upload', path: '/resume-upload', icon: FileText },
    { label: 'ATS Ranker', path: '/ats-ranker', icon: BarChart3 },
    { label: 'Dashboard', path: '/dashboard', icon: Bookmark },
    { label: 'Notifications', path: '/notifications', icon: Bell },
    { label: 'Profile', path: '/profile', icon: User },
  ];

  return (
    <aside className="w-64 bg-white border-r border-slate-200 p-5 hidden lg:flex flex-col justify-between font-sans min-h-[calc(100vh-4rem)]">
      <div className="space-y-6">
        <div className="text-[11px] font-black uppercase tracking-wider text-slate-400 px-3">
          Candidate Workspace
        </div>

        <nav className="space-y-1">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;

            return (
              <button
                key={item.path}
                onClick={() => navigate(item.path)}
                className={`w-full py-2.5 px-3 rounded-xl text-xs font-bold transition flex items-center gap-3 cursor-pointer ${
                  isActive
                    ? 'bg-purple-50 text-purple-700 border border-purple-100 shadow-2xs'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? 'text-purple-600' : 'text-slate-400'}`} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>
      </div>

      <div className="p-3 bg-purple-50/60 border border-purple-100 rounded-2xl text-center space-y-1">
        <p className="text-xs font-black text-purple-900">SwipeX AI Engine</p>
      </div>
    </aside>
  );
};

export default Sidebar;