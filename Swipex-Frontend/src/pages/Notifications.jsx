import React, { useState } from 'react';
import Navbar from '../components/Navbar';
import Sidebar from '../components/Sidebar';
import { 
  Bell, Sparkles, CheckCircle2, Briefcase, 
  Trash2, Check, ArrowUpRight 
} from 'lucide-react';

export default function Notifications() {
  const [notifications, setNotifications] = useState(INITIAL_NOTIFICATIONS);

  const handleMarkAllRead = () => {
    setNotifications(prev => prev.map(n => ({ ...n, is_read: true })));
  };

  const handleDelete = (id) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  };

  const unreadCount = notifications.filter(n => !n.is_read).length;

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col font-sans">
      <Navbar />

      <div className="flex flex-1">
        <Sidebar />

        <main className="flex-1 p-8 max-w-4xl space-y-8">
          {/* Header */}
          <div className="flex justify-between items-end">
            <div>
              <h1 className="text-2xl font-black text-slate-900 tracking-tight">Notifications & Alerts</h1>
              <p className="text-xs text-slate-500 font-medium">Recruiter matches, application status changes, and AI feed recommendations</p>
            </div>

            {unreadCount > 0 && (
              <button 
                onClick={handleMarkAllRead}
                className="px-3.5 py-2 bg-purple-50 hover:bg-purple-100 text-purple-700 border border-purple-200 rounded-xl text-xs font-bold flex items-center gap-1.5 transition cursor-pointer"
              >
                <Check className="w-3.5 h-3.5 text-purple-600" />
                <span>Mark All as Read ({unreadCount})</span>
              </button>
            )}
          </div>

          {/* Notifications List */}
          {notifications.length === 0 ? (
            <div className="bg-white p-12 rounded-3xl border border-slate-200 text-center space-y-3">
              <Bell className="w-8 h-8 text-slate-300 mx-auto" />
              <h3 className="text-sm font-black text-slate-800">No notifications right now</h3>
              <p className="text-xs text-slate-400">You're all caught up! New application alerts will appear here.</p>
            </div>
          ) : (
            <div className="space-y-3">
              {notifications.map((notif) => (
                <div 
                  key={notif.id}
                  className={`p-5 rounded-3xl border transition flex items-start justify-between ${
                    notif.is_read 
                      ? 'bg-white border-slate-200' 
                      : 'bg-purple-50/50 border-purple-200 shadow-2xs'
                  }`}
                >
                  <div className="flex items-start gap-3.5">
                    <div className={`w-10 h-10 rounded-2xl flex items-center justify-center flex-shrink-0 font-bold ${
                      notif.type === 'match' 
                        ? 'bg-purple-600 text-white' 
                        : 'bg-slate-100 text-slate-600'
                    }`}>
                      {notif.type === 'match' ? <Sparkles className="w-5 h-5 fill-white" /> : <Briefcase className="w-5 h-5" />}
                    </div>

                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <h3 className="text-xs font-black text-slate-900">{notif.title}</h3>
                        {!notif.is_read && (
                          <span className="w-2 h-2 rounded-full bg-purple-600" />
                        )}
                      </div>
                      <p className="text-xs text-slate-600 font-medium leading-relaxed">{notif.message}</p>
                      <p className="text-[10px] text-slate-400 font-bold">{notif.timestamp}</p>
                    </div>
                  </div>

                  <div className="flex items-center gap-2 flex-shrink-0">
                    <button 
                      onClick={() => window.location.href = notif.action_url}
                      className="p-2 text-purple-600 hover:bg-purple-50 rounded-xl transition cursor-pointer"
                      title="View Details"
                    >
                      <ArrowUpRight className="w-4 h-4" />
                    </button>
                    <button 
                      onClick={() => handleDelete(notif.id)}
                      className="p-2 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-xl transition cursor-pointer"
                      title="Dismiss Notification"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

const INITIAL_NOTIFICATIONS = [
  {
    id: "notif-1",
    type: "match",
    title: "New 94.5% AI Career Match!",
    message: "SwipeX Tech posted Senior Python Backend Engineer matching your uploaded active resume.",
    timestamp: "10 mins ago",
    is_read: false,
    action_url: "/discovery"
  },
  {
    id: "notif-2",
    type: "status",
    title: "Application Reviewed",
    message: "Razorpay viewed your profile for Frontend React Developer position.",
    timestamp: "2 hours ago",
    is_read: false,
    action_url: "/dashboard"
  },
  {
    id: "notif-3",
    type: "ats",
    title: "ATS Resume Analysis Complete",
    message: "Your active resume achieved an 84.5% alignment score for Python Engineer roles.",
    timestamp: "1 day ago",
    is_read: true,
    action_url: "/ats-ranker"
  }
];