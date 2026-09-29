import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { 
  Building2, PlusCircle, CheckSquare, Zap, LogOut, 
  Menu, X, Sparkles, CheckCircle2, AlertTriangle, 
  FileText, ArrowLeft, Download, Mail, MapPin, UserCheck, UserX, Eye
} from 'lucide-react';

export default function CandidateReview() {
  const navigate = useNavigate();
  const location = useLocation();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [toastMessage, setToastMessage] = useState(null);

  // Reads passed applicantId from AtsRanker / RecruiterDashboard or defaults to 101
  const applicantId = location.state?.applicantId || 101;
  const [candidateStatus, setCandidateStatus] = useState("Under Review");

  // Mock candidate database mapped to passed IDs
  const candidateDatabase = {
    101: {
      name: "Alex Morgan",
      email: "alex@example.com",
      location: "Bangalore, India",
      roleApplied: "Senior React Architect",
      atsScore: 96,
      matchingSkills: ["React.js", "TypeScript", "Tailwind CSS", "Redux Toolkit", "Node.js"],
      missingSkills: ["GraphQL", "AWS Lambda"],
      summary: "Senior Frontend Engineer with 5+ years of experience building high-scale React web applications. Spearheaded micro-frontend migrations and optimized core web vitals for 2M+ active users."
    },
    102: {
      name: "Priya Sharma",
      email: "priya.sharma@example.com",
      location: "Remote",
      roleApplied: "Senior React Architect",
      atsScore: 88,
      matchingSkills: ["React.js", "Redux", "Tailwind CSS"],
      missingSkills: ["TypeScript", "FastAPI"],
      summary: "Frontend Developer with 4 years of experience delivering responsive user portals and design systems in fast-paced startup environments."
    },
    103: {
      name: "Rahul Verma",
      email: "rahul.v@example.com",
      location: "Hyderabad, India",
      roleApplied: "Frontend Developer Intern",
      atsScore: 92,
      matchingSkills: ["JavaScript", "React.js", "CSS3", "Git"],
      missingSkills: ["Docker"],
      summary: "Computer Science undergraduate with strong foundation in core web tech, data structures, and hands-on React project work."
    }
  };

  const candidate = candidateDatabase[applicantId] || candidateDatabase[101];

  const showToast = (msg) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 2500);
  };

  const handleStatusChange = (newStatus) => {
    setCandidateStatus(newStatus);
    showToast(`Updated ${candidate.name}'s status to ${newStatus}`);
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex font-sans selection:bg-purple-500 selection:text-white">
      
      {/* Toast Alert Notification */}
      {toastMessage && (
        <div className="fixed top-6 right-6 z-50 bg-slate-900 text-white px-4 py-2.5 rounded-2xl shadow-xl text-xs font-bold flex items-center gap-2 animate-bounce">
          <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          {toastMessage}
        </div>
      )}

      {/* 1. RECRUITER SIDEBAR */}
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
              className="w-full py-2.5 px-3 text-slate-400 hover:bg-slate-800 hover:text-white rounded-xl flex items-center gap-3 transition cursor-pointer"
            >
              <Building2 className="w-4 h-4" />
              <span>Overview Dashboard</span>
            </button>

            <button 
              onClick={() => { navigate('/post-job'); setIsMobileMenuOpen(false); }}
              className="w-full py-2.5 px-3 text-slate-400 hover:bg-slate-800 hover:text-white rounded-xl flex items-center gap-3 transition cursor-pointer"
            >
              <PlusCircle className="w-4 h-4" />
              <span>Job Posting Wizard</span>
            </button>

            <button 
              onClick={() => { navigate('/ats-ranker'); setIsMobileMenuOpen(false); }}
              className="w-full py-2.5 px-3 text-slate-400 hover:bg-slate-800 hover:text-white rounded-xl flex items-center gap-3 transition cursor-pointer"
            >
              <CheckSquare className="w-4 h-4" />
              <span>Applicant ATS Ranker</span>
            </button>

            <button 
              onClick={() => { navigate('/candidate-review'); setIsMobileMenuOpen(false); }}
              className="w-full py-2.5 px-3 bg-purple-600 text-white rounded-xl flex items-center gap-3 shadow-2xs cursor-pointer"
            >
              <Eye className="w-4 h-4" />
              <span>Candidate Review</span>
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
          <div className="flex items-center gap-3">
            <button onClick={() => setIsMobileMenuOpen(true)} className="lg:hidden p-2 text-slate-600">
              <Menu className="w-5 h-5" />
            </button>

            {/* BACK BUTTON REDIRECTS TO ATS RANKER */}
            <button 
              onClick={() => navigate('/ats-ranker')} 
              className="p-2 hover:bg-slate-100 rounded-xl text-slate-600 transition cursor-pointer flex items-center gap-1.5 text-xs font-bold"
              title="Return to Ranker Table"
            >
              <ArrowLeft className="w-4 h-4" /> Back to Applicants
            </button>
          </div>

          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-xl bg-purple-100 border border-purple-300 text-purple-700 font-bold text-xs flex items-center justify-center cursor-pointer">
              HR
            </div>
          </div>
        </header>

        {/* Workspace Body */}
        <main className="flex-grow p-6 max-w-5xl mx-auto w-full space-y-6">
          
          {/* Candidate Profile Header Card */}
          <div className="bg-white border border-slate-200 rounded-3xl p-6 shadow-2xs flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <h2 className="text-2xl font-black text-slate-900">{candidate.name}</h2>
                <span className="text-xs font-bold bg-purple-100 text-purple-700 border border-purple-200 px-2.5 py-0.5 rounded-full flex items-center gap-1">
                  <Sparkles className="w-3 h-3" /> {candidate.atsScore}% ATS Match Score
                </span>
              </div>
              <p className="text-xs text-slate-500 font-medium">Applied for <span className="font-bold text-slate-800">{candidate.roleApplied}</span></p>
              
              <div className="flex flex-wrap gap-3 text-xs text-slate-500 font-medium pt-1">
                <span className="flex items-center gap-1"><Mail className="w-3.5 h-3.5 text-purple-600" /> {candidate.email}</span>
                <span className="flex items-center gap-1"><MapPin className="w-3.5 h-3.5 text-purple-600" /> {candidate.location}</span>
              </div>
            </div>

            {/* Shortlist / Reject Pipeline Buttons */}
            <div className="flex items-center gap-2 self-end sm:self-auto">
              <button 
                onClick={() => handleStatusChange('Shortlisted')}
                className={`px-4 py-2 font-bold text-xs rounded-xl shadow-2xs transition flex items-center gap-1.5 cursor-pointer ${
                  candidateStatus === 'Shortlisted' ? 'bg-emerald-700 text-white ring-2 ring-emerald-300' : 'bg-emerald-600 hover:bg-emerald-700 text-white'
                }`}
              >
                <UserCheck className="w-4 h-4" /> {candidateStatus === 'Shortlisted' ? 'Shortlisted' : 'Shortlist'}
              </button>
              
              <button 
                onClick={() => handleStatusChange('Rejected')}
                className={`px-4 py-2 font-bold text-xs rounded-xl transition flex items-center gap-1.5 cursor-pointer ${
                  candidateStatus === 'Rejected' ? 'bg-rose-600 text-white' : 'bg-rose-50 text-rose-600 hover:bg-rose-100'
                }`}
              >
                <UserX className="w-4 h-4" /> Reject
              </button>
            </div>
          </div>

          {/* Detailed Skill Breakdown */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            
            <div className="md:col-span-2 space-y-6">
              
              {/* Executive Summary */}
              <div className="bg-white border border-slate-200 rounded-3xl p-6 shadow-2xs space-y-3">
                <h3 className="text-xs font-black text-slate-900 uppercase tracking-wider">Executive Summary</h3>
                <p className="text-xs text-slate-600 font-medium leading-relaxed">{candidate.summary}</p>
              </div>

              {/* AI Skill Overlap Analysis */}
              <div className="bg-white border border-slate-200 rounded-3xl p-6 shadow-2xs space-y-4">
                <h3 className="text-xs font-black text-slate-900 uppercase tracking-wider">AI Skill Overlap Analysis</h3>
                
                <div className="space-y-2">
                  <p className="text-[10px] font-bold text-slate-400 uppercase">Matched Required Skills</p>
                  <div className="flex flex-wrap gap-1.5">
                    {candidate.matchingSkills.map((skill, index) => (
                      <span key={index} className="text-xs font-bold bg-emerald-50 text-emerald-700 border border-emerald-200 px-3 py-1 rounded-xl flex items-center gap-1">
                        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" /> {skill}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="space-y-2 pt-2 border-t border-slate-100">
                  <p className="text-[10px] font-bold text-slate-400 uppercase">Missing Skill Gaps</p>
                  <div className="flex flex-wrap gap-1.5">
                    {candidate.missingSkills.map((skill, index) => (
                      <span key={index} className="text-xs font-bold bg-amber-50 text-amber-700 border border-amber-200 px-3 py-1 rounded-xl flex items-center gap-1">
                        <AlertTriangle className="w-3.5 h-3.5 text-amber-600" /> {skill}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

            </div>

            {/* Resume Preview & Quick Actions Sidebar */}
            <div className="bg-white border border-slate-200 rounded-3xl p-6 shadow-2xs space-y-4 h-fit">
              <h3 className="text-xs font-black text-slate-900 uppercase tracking-wider flex items-center gap-1.5">
                <FileText className="w-4 h-4 text-purple-600" /> Verified Resume
              </h3>
              
              <div className="p-4 bg-slate-50 border border-slate-200 rounded-2xl text-center space-y-2">
                <p className="text-xs font-bold text-slate-900">{candidate.name.replace(" ", "_")}_Resume.pdf</p>
                <p className="text-[10px] text-slate-400 font-medium">ATS Parsed PDF Document</p>
                
                <button className="w-full py-2 bg-white border border-slate-200 hover:border-purple-600 text-purple-700 font-bold text-xs rounded-xl transition flex items-center justify-center gap-1.5 cursor-pointer shadow-2xs">
                  <Download className="w-3.5 h-3.5" /> Download PDF
                </button>
              </div>

              <div className="pt-2 border-t border-slate-100">
                <p className="text-[10px] font-bold text-slate-400 uppercase mb-2">Quick Navigation</p>
                <button 
                  onClick={() => navigate('/ats-ranker')} 
                  className="w-full py-2 px-3 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs rounded-xl transition text-left cursor-pointer"
                >
                  ← Back to ATS Ranker Table
                </button>
              </div>
            </div>

          </div>

        </main>
      </div>

    </div>
  );
}