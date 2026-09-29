import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Zap, Sparkles, Home, Bell, User } from 'lucide-react';

export const Navbar = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const navItems = [
    { label: 'Home', path: '/', icon: Home },
    { label: 'Discover', path: '/discovery', icon: Sparkles },
  ];

  return (
    <header className="bg-white border-b border-slate-200 sticky top-0 z-50 font-sans w-full">
      <div className="w-full px-8 h-16 flex items-center justify-between">
        
        {/* LEFT SECTION: Pinned to far left */}
        <div className="flex items-center">
          <div 
            onClick={() => navigate('/discovery')} 
            className="flex items-center gap-2.5 cursor-pointer select-none"
          >
            <div className="w-9 h-9 rounded-xl bg-purple-600 flex items-center justify-center text-white font-black shadow-sm">
              <Zap className="w-5 h-5 fill-white" />
            </div>
            <span className="text-xl font-black text-slate-900 tracking-tight">
              Swipe<span className="text-purple-600">X</span>
            </span>
          </div>
        </div>

        {/* CENTER SECTION: Exactly centered */}
        <nav className="absolute left-1/2 -translate-x-1/2 flex items-center gap-2">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;

            return (
              <button
                key={item.path}
                onClick={() => navigate(item.path)}
                className={`px-4 py-2 rounded-xl text-xs font-bold transition flex items-center gap-2 cursor-pointer ${
                  isActive
                    ? 'bg-purple-50 text-purple-700'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? 'text-purple-600' : 'text-slate-400'}`} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>

        {/* RIGHT SECTION: Pinned to far right */}
        <div className="flex items-center gap-3">
          <button 
            onClick={() => navigate('/notifications')}
            className="p-2.5 rounded-xl text-slate-600 hover:text-slate-900 hover:bg-slate-100 transition cursor-pointer relative border border-slate-200"
            title="Notifications"
          >
            <Bell className="w-4 h-4" />
            <span className="absolute top-2 right-2 w-2 h-2 bg-purple-600 rounded-full" />
          </button>

          <button 
            onClick={() => navigate('/profile')}
            className="w-9 h-9 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 flex items-center justify-center transition cursor-pointer border border-slate-200"
            title="Profile Settings"
          >
            <User className="w-4 h-4" />
          </button>
        </div>

      </div>
    </header>
  );
};

export default Navbar;