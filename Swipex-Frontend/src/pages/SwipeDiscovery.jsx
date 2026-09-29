import React from 'react';
import Navbar from '../components/Navbar';
import Sidebar from '../components/Sidebar';
import SwipeDeck from '../components/SwipeDeck';
import { Sparkles, SlidersHorizontal } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function SwipeDiscovery() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col font-sans">
      {/* Top Navbar */}
      <Navbar />

      <div className="flex flex-1">
        {/* Left Sidebar */}
        <Sidebar />

        {/* Main Feed Content Area */}
        <main className="flex-1 p-8 max-w-5xl flex flex-col items-center justify-between">
          {/* Section Header */}
          <div className="w-full max-w-md flex items-center justify-between mb-4">
            <div>
              <h1 className="text-2xl font-black text-slate-900 tracking-tight flex items-center gap-2">
                AI Career Match <Sparkles className="w-5 h-5 text-purple-600 fill-purple-600" />
              </h1>
              <p className="text-xs text-slate-500 font-medium">Swipe right to apply or left to skip</p>
            </div>

            {/* Quick Filter Navigation Button */}
            <button 
              onClick={() => navigate('/job-search')}
              className="p-2.5 bg-white border border-slate-200 rounded-2xl shadow-xs text-slate-700 hover:bg-slate-100 transition cursor-pointer"
              title="Advanced Search & Filters"
            >
              <SlidersHorizontal className="w-5 h-5" />
            </button>
          </div>

          {/* Central Interactive Swipe Deck Container */}
          <div className="w-full my-auto flex justify-center py-4">
            <SwipeDeck />
          </div>

          {/* Helper Instructions Footer */}
          <div className="w-full max-w-md text-center mt-4">
            <p className="text-xs text-slate-400 font-medium">
              Swipe <span className="text-purple-600 font-semibold">Right</span> to Apply • Swipe <span className="text-rose-500 font-semibold">Left</span> to Skip • <span className="text-amber-500 font-semibold">Up</span> to Save
            </p>
          </div>
        </main>
      </div>
    </div>
  );
}