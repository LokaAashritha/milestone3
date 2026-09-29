import React, { useState, useEffect } from 'react';
import { motion, useMotionValue, useTransform, AnimatePresence } from 'framer-motion';
import { 
  Building2, MapPin, Sparkles, X, Bookmark, Heart, RotateCcw, RefreshCw 
} from 'lucide-react';
import { RecommendationService, SwipeService, JobService } from '../services/api';

const FALLBACK_DECK = [
  {
    job_id: "101",
    company_name: "SwipeX Tech",
    title: "Senior Python Backend Engineer",
    location: "Remote / Bengaluru",
    salary_range: "₹18 LPA - ₹28 LPA",
    skills: ["Python", "FastAPI", "PostgreSQL", "Docker"],
    semantic_match_score: 94.5,
    recommendation_tags: ["🔥 94.5% AI Match", "High Skill Alignment"]
  },
  {
    job_id: "102",
    company_name: "Razorpay",
    title: "Frontend React Developer",
    location: "Bengaluru, India",
    salary_range: "₹14 LPA - ₹22 LPA",
    skills: ["React", "TypeScript", "Tailwind CSS"],
    semantic_match_score: 89.0,
    recommendation_tags: ["✨ Top Skill Fit", "Fresher Friendly"]
  }
];

export default function SwipeDeck() {
  const [deck, setDeck] = useState([]);
  const [swipeHistory, setSwipeHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  const currentUserId = localStorage.getItem('swipex_user_id') || 'demo-user-1';

  // Framer Motion Drag Variables
  const x = useMotionValue(0);
  const y = useMotionValue(0);
  const rotate = useTransform(x, [-200, 200], [-20, 20]);
  const opacity = useTransform(x, [-200, -150, 0, 150, 200], [0, 1, 1, 1, 0]);

  useEffect(() => {
    loadDeck();
  }, []);

  const loadDeck = async () => {
    setLoading(true);
    try {
      const res = await RecommendationService.getUpgradedRecommendations(10);
      if (res && res.recommendations && res.recommendations.length > 0) {
        setDeck(res.recommendations);
      } else {
        const catalog = await JobService.getJobs(1, 10);
        const list = catalog?.results || catalog || [];
        setDeck(list.length > 0 ? list : FALLBACK_DECK);
      }
    } catch (err) {
      console.warn("Backend offline, loading fallback cards:", err);
      setDeck(FALLBACK_DECK);
    } finally {
      setLoading(false);
    }
  };

  const currentJob = deck[0];

  const handleSwipe = async (actionType) => {
    if (!currentJob) return;
    const targetJob = currentJob;
    const direction = actionType === 'skip' ? 'left' : 'right';

    setDeck(prev => prev.slice(1));
    setSwipeHistory(prev => [targetJob, ...prev]);

    try {
      await SwipeService.recordCandidateSwipe(currentUserId, targetJob.job_id || targetJob.id, actionType);
    } catch (err) {
      console.warn("Swipe logging notice:", err);
    }
  };

  const handleDragEnd = (event, info) => {
    if (info.offset.x > 100) handleSwipe('like');
    else if (info.offset.x < -100) handleSwipe('skip');
    else if (info.offset.y < -100) handleSwipe('save');
  };

  const handleUndo = async () => {
    if (swipeHistory.length === 0) return;
    const lastJob = swipeHistory[0];
    setDeck(prev => [lastJob, ...prev]);
    setSwipeHistory(prev => prev.slice(1));
    try {
      await SwipeService.undoSwipe(lastJob.job_id || lastJob.id);
    } catch (err) {
      console.warn("Undo notice:", err);
    }
  };

  if (loading) {
    return (
      <div className="text-center py-20 space-y-3">
        <RefreshCw className="w-8 h-8 text-purple-600 animate-spin mx-auto" />
        <p className="text-xs font-bold text-slate-400">Fetching AI Career Recommendations...</p>
      </div>
    );
  }

  if (!currentJob) {
    return (
      <div className="text-center p-8 bg-white border border-slate-200 rounded-3xl space-y-4 shadow-sm max-w-sm w-full">
        <Sparkles className="w-10 h-10 text-purple-600 mx-auto" />
        <h3 className="text-base font-black text-slate-900">You're all caught up!</h3>
        <p className="text-xs text-slate-500 font-medium">No more unswiped opportunities in your feed right now.</p>
        <button 
          onClick={loadDeck} 
          className="px-5 py-2.5 bg-purple-600 hover:bg-purple-700 text-white rounded-xl text-xs font-bold transition cursor-pointer shadow-sm"
        >
          Refresh Feed
        </button>
      </div>
    );
  }

  return (
    <div className="w-full max-w-md relative flex flex-col items-center">
      <AnimatePresence>
        <motion.div
          key={currentJob.job_id || currentJob.id}
          style={{ x, y, rotate, opacity }}
          drag
          dragConstraints={{ left: 0, right: 0, top: 0, bottom: 0 }}
          onDragEnd={handleDragEnd}
          className="w-full bg-white border border-slate-200 rounded-3xl p-6 shadow-xl space-y-5 cursor-grab active:cursor-grabbing select-none"
        >
          {/* Header & Match Badge */}
          <div className="flex justify-between items-start">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-2xl border border-slate-100 bg-purple-50 flex items-center justify-center">
                <Building2 className="w-6 h-6 text-purple-600" />
              </div>
              <div>
                <h3 className="text-xs font-bold text-slate-400">{currentJob.company_name || currentJob.company || "Employer"}</h3>
                <h2 className="text-base font-black text-slate-900">{currentJob.title}</h2>
              </div>
            </div>

            {/* Match Score Badge */}
            <div className="bg-purple-600 text-white px-3 py-1 rounded-full flex items-center gap-1 text-xs font-black shadow-xs">
              <Sparkles className="w-3 h-3 fill-white" /> 
              <span>{Math.round(currentJob.semantic_match_score || currentJob.matchScore || 88)}%</span>
            </div>
          </div>

          {/* Location & Salary */}
          <div className="flex items-center gap-3 text-xs font-bold text-slate-500">
            <span className="flex items-center gap-1">
              <MapPin className="w-3.5 h-3.5 text-purple-600" /> {currentJob.location}
            </span>
            {currentJob.salary_range && (
              <span className="bg-slate-100 text-slate-700 px-2.5 py-0.5 rounded-lg">
                {currentJob.salary_range}
              </span>
            )}
          </div>

          {/* AI Recommendation Tags */}
          {currentJob.recommendation_tags && currentJob.recommendation_tags.length > 0 && (
            <div className="flex flex-wrap gap-1.5 pt-1">
              {currentJob.recommendation_tags.map((tag, idx) => (
                <span key={idx} className="text-[10px] font-black bg-purple-50 text-purple-700 border border-purple-200 px-2.5 py-0.5 rounded-md">
                  {tag}
                </span>
              ))}
            </div>
          )}

          {/* Skills Chips */}
          {currentJob.skills && (
            <div className="flex flex-wrap gap-1.5 pt-2 border-t border-slate-100">
              {currentJob.skills.map((skill, i) => (
                <span key={i} className="text-[11px] font-bold bg-slate-100 text-slate-700 px-2.5 py-1 rounded-lg">
                  {skill}
                </span>
              ))}
            </div>
          )}
        </motion.div>
      </AnimatePresence>

      {/* Floating Action Buttons */}
      <div className="flex justify-center items-center gap-4 pt-6">
        <button 
          onClick={() => handleSwipe('skip')} 
          className="w-12 h-12 rounded-full bg-white border border-slate-200 text-rose-600 shadow-md flex items-center justify-center hover:bg-rose-50 cursor-pointer transition"
          title="Skip Job"
        >
          <X className="w-6 h-6" />
        </button>
        <button 
          onClick={handleUndo} 
          disabled={swipeHistory.length === 0}
          className="w-10 h-10 rounded-full bg-white border border-slate-200 text-slate-600 shadow-md flex items-center justify-center disabled:opacity-40 hover:bg-slate-50 cursor-pointer transition"
          title="Undo Last Action"
        >
          <RotateCcw className="w-4 h-4" />
        </button>
        <button 
          onClick={() => handleSwipe('save')} 
          className="w-10 h-10 rounded-full bg-white border border-slate-200 text-purple-600 shadow-md flex items-center justify-center hover:bg-purple-50 cursor-pointer transition"
          title="Save Job"
        >
          <Bookmark className="w-4 h-4" />
        </button>
        <button 
          onClick={() => handleSwipe('like')} 
          className="w-12 h-12 rounded-full bg-purple-600 text-white shadow-md flex items-center justify-center hover:bg-purple-700 cursor-pointer transition"
          title="Apply Now"
        >
          <Heart className="w-6 h-6 fill-white" />
        </button>
      </div>
    </div>
  );
}