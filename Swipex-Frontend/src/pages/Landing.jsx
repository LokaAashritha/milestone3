import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Zap, ArrowRight, Sparkles, Search, FileText, CheckCircle2, 
  Building2, Users, Target, ShieldCheck, ChevronDown, Star, TrendingUp, Layers
} from 'lucide-react';

export default function Landing() {
  const navigate = useNavigate();
  const [openFaq, setOpenFaq] = useState(null);

  const toggleFaq = (index) => {
    setOpenFaq(openFaq === index ? null : index);
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col justify-between font-sans selection:bg-purple-500 selection:text-white scroll-smooth">
      
      {/* 1. Header Navigation */}
      <nav className="w-full bg-white/90 backdrop-blur-md border-b border-slate-200 sticky top-0 z-50 px-6 py-4 flex justify-between items-center shadow-xs">
        <div className="flex items-center gap-8">
          <div className="flex items-center gap-3 cursor-pointer" onClick={() => navigate('/')}>
            <div className="w-10 h-10 rounded-xl bg-purple-600 flex items-center justify-center shadow-md shadow-purple-600/20">
              <Zap className="w-5 h-5 text-white fill-white" />
            </div>
            <span className="text-2xl font-black tracking-tight text-slate-900">
              Swipe<span className="text-purple-600">X</span>
            </span>
          </div>

          <div className="hidden md:flex items-center gap-6 text-xs font-semibold text-slate-600">
            <a href="#features" className="hover:text-purple-600 transition">Features</a>
            <a href="#how-it-works" className="hover:text-purple-600 transition">How It Works</a>
            <a href="#roles" className="hover:text-purple-600 transition">For Candidates & Recruiters</a>
            <a href="#faq" className="hover:text-purple-600 transition">FAQ</a>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate('/login')}
            className="px-4 py-2 text-xs font-bold text-slate-700 hover:text-purple-600 transition"
          >
            Sign In
          </button>
          <button
            onClick={() => navigate('/register')}
            className="px-4 py-2 text-xs font-bold bg-purple-600 hover:bg-purple-700 text-white rounded-xl shadow-md transition flex items-center gap-1.5"
          >
            Get Started <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </nav>

      {/* 2. Hero Section */}
      <section className="relative px-6 pt-20 pb-16 flex flex-col items-center text-center overflow-hidden">
        <div className="max-w-4xl space-y-6 z-10">
          <div className="inline-flex items-center gap-2 bg-purple-50 border border-purple-200 text-purple-700 px-4 py-1.5 rounded-full text-xs font-bold">
            <Sparkles className="w-4 h-4 text-purple-600" />
            <span>Next-Gen AI Career Discovery Platform</span>
          </div>

          <h1 className="text-4xl sm:text-6xl font-black text-slate-900 tracking-tight leading-tight">
            Stop Applying Blindly. <br />
            <span className="text-purple-600">Swipe Right on Your Next Career Step.</span>
          </h1>

          <p className="text-slate-600 text-base sm:text-lg max-w-2xl mx-auto leading-relaxed">
            Replace tedious job forms with instant AI skill matching, real-time ATS optimization, and gesture-based job discovery.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
            <button
              onClick={() => navigate('/register')}
              className="w-full sm:w-auto px-8 py-4 bg-purple-600 hover:bg-purple-700 text-white text-sm font-bold rounded-2xl shadow-lg shadow-purple-600/20 transition flex items-center justify-center gap-2"
            >
              Start Discovery Free <ArrowRight className="w-4 h-4" />
            </button>
            <button
              onClick={() => navigate('/login')}
              className="w-full sm:w-auto px-8 py-4 bg-white border border-slate-300 hover:bg-slate-100 text-slate-700 text-sm font-bold rounded-2xl shadow-xs transition"
            >
              Hire Candidates (Recruiter Portal)
            </button>
          </div>
        </div>

        {/* Hero Card Visual */}
        <div className="w-full max-w-md mt-12 bg-white border border-slate-200 rounded-3xl p-6 shadow-2xl relative text-left">
          <div className="flex justify-between items-center mb-3">
            <span className="text-[11px] font-bold bg-purple-50 text-purple-700 border border-purple-200 px-3 py-1 rounded-full flex items-center gap-1">
              <Sparkles className="w-3 h-3 text-purple-600" /> 98% AI Match Score
            </span>
            <span className="text-xs text-slate-400 font-semibold">Active Hiring</span>
          </div>

          <h3 className="text-xl font-extrabold text-slate-900">Lead AI Software Engineer</h3>
          <p className="text-xs text-slate-500 font-semibold mb-4">TechCorp Global • Remote / Hybrid</p>

          <div className="space-y-2 mb-6">
            <div className="flex items-center gap-2 text-xs text-slate-700">
              <CheckCircle2 className="w-4 h-4 text-emerald-500" /> Matched: React, Python, Dynamic Programming
            </div>
            <div className="flex items-center gap-2 text-xs text-slate-700">
              <CheckCircle2 className="w-4 h-4 text-emerald-500" /> Verified Salary: $110k - $140k / yr
            </div>
          </div>

          <div className="flex gap-3">
            <button className="flex-1 py-2.5 rounded-xl border border-slate-200 text-slate-600 font-bold text-xs hover:bg-slate-50 transition">
              Pass (Swipe Left)
            </button>
            <button className="flex-1 py-2.5 rounded-xl bg-purple-600 text-white font-bold text-xs hover:bg-purple-700 transition shadow-md shadow-purple-600/20">
              Apply (Swipe Right)
            </button>
          </div>
        </div>
      </section>

      {/* 3. Platform Statistics Bar */}
      <section className="bg-white border-y border-slate-200 py-10 px-6">
        <div className="max-w-6xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
          <div>
            <p className="text-3xl font-black text-slate-900">120k+</p>
            <p className="text-xs text-slate-500 font-semibold mt-1">Matched Candidates</p>
          </div>
          <div>
            <p className="text-3xl font-black text-purple-600">85%</p>
            <p className="text-xs text-slate-500 font-semibold mt-1">Faster Hiring Cycle</p>
          </div>
          <div>
            <p className="text-3xl font-black text-slate-900">500+</p>
            <p className="text-xs text-slate-500 font-semibold mt-1">Active MNCs & Startups</p>
          </div>
          <div>
            <p className="text-3xl font-black text-purple-600">94%</p>
            <p className="text-xs text-slate-500 font-semibold mt-1">ATS Optimization Accuracy</p>
          </div>
        </div>
      </section>

      {/* 4. Core Features Section */}
      <section id="features" className="py-20 px-6 max-w-6xl mx-auto">
        <div className="text-center max-w-2xl mx-auto mb-16 space-y-3">
          <h2 className="text-3xl font-black text-slate-900">Engineered for Modern Hiring</h2>
          <p className="text-slate-600 text-sm">Everything you need to streamline discovery and land high-converting interviews.</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="bg-white p-8 rounded-3xl border border-slate-200 shadow-xs space-y-4">
            <div className="w-12 h-12 rounded-2xl bg-purple-50 border border-purple-200 flex items-center justify-center text-purple-600">
              <Zap className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-slate-900">Gesture Swipe Discovery</h3>
            <p className="text-slate-600 text-xs leading-relaxed">
              Skip endless application forms. Swipe right to apply instantly with your verified AI profile or swipe left to move to the next role.
            </p>
          </div>

          <div className="bg-white p-8 rounded-3xl border border-slate-200 shadow-xs space-y-4">
            <div className="w-12 h-12 rounded-2xl bg-purple-50 border border-purple-200 flex items-center justify-center text-purple-600">
              <FileText className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-slate-900">AI ATS Resume Score</h3>
            <p className="text-slate-600 text-xs leading-relaxed">
              Get real-time feedback on your resume structure, keyword gaps, and ATS compliance before applying to top companies.
            </p>
          </div>

          <div className="bg-white p-8 rounded-3xl border border-slate-200 shadow-xs space-y-4">
            <div className="w-12 h-12 rounded-2xl bg-purple-50 border border-purple-200 flex items-center justify-center text-purple-600">
              <Target className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-slate-900">Smart Job Filters</h3>
            <p className="text-slate-600 text-xs leading-relaxed">
              Filter roles dynamically by Top MNCs, Early-Stage Startups, Fresher-Friendly Roles, and Low Competition opportunities.
            </p>
          </div>
        </div>
      </section>

      {/* 5. Dual Solutions (Candidates vs Recruiters) */}
      <section id="roles" className="bg-white py-20 px-6 border-y border-slate-200">
        <div className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-12">
          
          <div className="bg-slate-50 p-8 rounded-3xl border border-slate-200 space-y-6">
            <span className="text-xs font-bold text-purple-700 bg-purple-100 px-3 py-1 rounded-full">For Job Seekers</span>
            <h3 className="text-2xl font-black text-slate-900">Land Interviews 3x Faster</h3>
            <ul className="space-y-3 text-xs text-slate-700 font-medium">
              <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-purple-600" /> One-click application via Swipe Gesture</li>
              <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-purple-600" /> Real-time keyword gap analysis for every job</li>
              <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-purple-600" /> Visual Kanban board to track application states</li>
            </ul>
            <button onClick={() => navigate('/register')} className="w-full py-3 bg-purple-600 hover:bg-purple-700 text-white font-bold text-xs rounded-xl shadow-md transition">
              Create Candidate Profile
            </button>
          </div>

          <div className="bg-slate-50 p-8 rounded-3xl border border-slate-200 space-y-6">
            <span className="text-xs font-bold text-slate-700 bg-slate-200 px-3 py-1 rounded-full">For Recruiters</span>
            <h3 className="text-2xl font-black text-slate-900">Automate Candidate Sourcing</h3>
            <ul className="space-y-3 text-xs text-slate-700 font-medium">
              <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-slate-900" /> Pre-screened candidates ranked by AI Skill Match</li>
              <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-slate-900" /> Zero spam applications with verified candidate profiles</li>
              <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-slate-900" /> Direct pipeline management & interview scheduling</li>
            </ul>
            <button onClick={() => navigate('/login')} className="w-full py-3 bg-slate-900 hover:bg-slate-800 text-white font-bold text-xs rounded-xl shadow-md transition">
              Access Recruiter Workspace
            </button>
          </div>

        </div>
      </section>

      {/* 6. How It Works Section */}
      <section id="how-it-works" className="py-20 px-6 max-w-6xl mx-auto">
        <div className="text-center max-w-2xl mx-auto mb-16 space-y-3">
          <h2 className="text-3xl font-black text-slate-900">How SwipeX Works</h2>
          <p className="text-slate-600 text-sm">Four simple steps from setup to job placement.</p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-6">
          {[
            { step: '01', title: 'Upload Resume', desc: 'Drag and drop your resume. Our AI extracts skills and projects automatically.' },
            { step: '02', title: 'Get Match Score', desc: 'Receive instant ATS scoring and tailored keyword optimization tips.' },
            { step: '03', title: 'Swipe & Apply', desc: 'Browse curated job cards. Swipe right to apply instantly without forms.' },
            { step: '04', title: 'Track Progress', desc: 'Monitor application status on your personal candidate dashboard.' },
          ].map((item, idx) => (
            <div key={idx} className="bg-white p-6 rounded-3xl border border-slate-200 space-y-3">
              <span className="text-2xl font-black text-purple-600">{item.step}</span>
              <h4 className="text-base font-bold text-slate-900">{item.title}</h4>
              <p className="text-slate-600 text-xs leading-relaxed">{item.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* 7. FAQ Accordion Section */}
      <section id="faq" className="bg-white py-20 px-6 border-t border-slate-200">
        <div className="max-w-4xl mx-auto space-y-8">
          <div className="text-center space-y-2">
            <h2 className="text-3xl font-black text-slate-900">Frequently Asked Questions</h2>
            <p className="text-slate-600 text-sm">Everything you need to know about SwipeX.</p>
          </div>

          <div className="space-y-4">
            {[
              { q: 'How does the AI Match Score work?', a: 'Our AI compares your resume skills, experience level, and project tech stack directly against real job descriptions to generate a percentage match score.' },
              { q: 'Is SwipeX free for job seekers?', a: 'Yes! SwipeX is completely free for candidate profile creation, swipe discovery, ATS scoring, and job applications.' },
              { q: 'How do recruiters receive my application?', a: 'When you swipe right, your verified AI profile and formatted resume are sent directly into the recruiter’s pipeline dashboard.' },
            ].map((faq, idx) => (
              <div key={idx} className="border border-slate-200 rounded-2xl p-5 bg-slate-50 cursor-pointer" onClick={() => toggleFaq(idx)}>
                <div className="flex justify-between items-center font-bold text-sm text-slate-900">
                  <span>{faq.q}</span>
                  <ChevronDown className={`w-4 h-4 transition-transform ${openFaq === idx ? 'rotate-180' : ''}`} />
                </div>
                {openFaq === idx && (
                  <p className="text-xs text-slate-600 mt-3 pt-3 border-t border-slate-200 leading-relaxed">
                    {faq.a}
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* 8. Call To Action Footer Banner */}
      <section className="bg-purple-600 text-white py-16 px-6 text-center">
        <div className="max-w-3xl mx-auto space-y-6">
          <h2 className="text-3xl sm:text-4xl font-black">Ready to Swipe Your Way into Your Next Role?</h2>
          <p className="text-purple-100 text-sm max-w-xl mx-auto">
            Join thousands of developers, designers, and tech professionals discovering roles with AI precision.
          </p>
          <button
            onClick={() => navigate('/register')}
            className="px-8 py-4 bg-white text-purple-700 font-extrabold text-xs rounded-2xl shadow-xl hover:bg-slate-100 transition inline-flex items-center gap-2"
          >
            Create Your Free Account <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </section>

      {/* 9. Footer */}
      <footer className="w-full bg-slate-900 text-slate-400 py-12 px-6 border-t border-slate-800 text-xs">
        <div className="max-w-6xl mx-auto flex flex-col sm:flex-row justify-between items-center gap-6">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-purple-600 flex items-center justify-center">
              <Zap className="w-4 h-4 text-white fill-white" />
            </div>
            <span className="text-lg font-black text-white">SwipeX</span>
          </div>
          <p>© 2026 SwipeX Platform. Built for Intelligent Career Discovery.</p>
        </div>
      </footer>

    </div>
  );
}