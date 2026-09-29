import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Building2, PlusCircle, CheckSquare, Zap, LogOut, 
  Menu, X, Bell, Briefcase, Sparkles, CheckCircle2, 
  Plus, DollarSign, MapPin, Layers, ArrowRight, Eye, UserCheck
} from 'lucide-react';

export default function PostJob() {
  const navigate = useNavigate();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isProfileDropdownOpen, setIsProfileDropdownOpen] = useState(false);
  const [toastMessage, setToastMessage] = useState(null);

  // Form State
  const [jobTitle, setJobTitle] = useState('');
  const [category, setCategory] = useState('Startups');
  const [roleType, setRoleType] = useState('Full-Time');
  const [location, setLocation] = useState('');
  const [salaryMin, setSalaryMin] = useState('');
  const [salaryMax, setSalaryMax] = useState('');
  const [description, setDescription] = useState('');
  
  // Skills Management
  const [requiredSkills, setRequiredSkills] = useState(['React', 'TypeScript']);
  const [newSkill, setNewSkill] = useState('');

  const showToast = (msg) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 2500);
  };

  const handleAddSkill = (e) => {
    e.preventDefault();
    if (newSkill.trim() && !requiredSkills.includes(newSkill.trim())) {
      setRequiredSkills([...requiredSkills, newSkill.trim()]);
      setNewSkill('');
    }
  };

  const handleRemoveSkill = (skillToRemove) => {
    setRequiredSkills(requiredSkills.filter(s => s !== skillToRemove));
  };

  const handlePublishJob = (e) => {
    e.preventDefault();
    if (!jobTitle || !location || !description) {
      showToast('Please fill out all required fields.');
      return;
    }
    showToast('Job published! Opening candidate matches...');
    
    // REDIRECT TO CANDIDATE REVIEW AFTER PUBLISHING
    setTimeout(() => {
      navigate('/candidate-review', { state: { role: jobTitle } });
    }, 1200);
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex font-sans selection:bg-purple-500 selection:text-white">
      
      {/* Toast Alert */}
      {toastMessage && (
        <div className="fixed top-6 right-6 z-50 bg-slate-900 text-white px-4 py-2.5 rounded-2xl shadow-xl text-xs font-bold flex items-center gap-2 animate-bounce">
          <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          {toastMessage}
        </div>
      )}

      {/* 1. RECRUITER PORTAL SIDEBAR */}
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
              className="w-full py-2.5 px-3 text-slate-400 hover:bg-slate-800 hover:text-white rounded-xl flex items-center gap-3 transition"
            >
              <Building2 className="w-4 h-4" />
              <span>Overview Dashboard</span>
            </button>

            <button 
              onClick={() => { navigate('/post-job'); setIsMobileMenuOpen(false); }}
              className="w-full py-2.5 px-3 bg-purple-600 text-white rounded-xl flex items-center gap-3 shadow-2xs"
            >
              <PlusCircle className="w-4 h-4" />
              <span>Job Posting Wizard</span>
            </button>

            <button 
              onClick={() => { navigate('/ats-ranker'); setIsMobileMenuOpen(false); }}
              className="w-full py-2.5 px-3 text-slate-400 hover:bg-slate-800 hover:text-white rounded-xl flex items-center gap-3 transition"
            >
              <CheckSquare className="w-4 h-4" />
              <span>Applicant ATS Ranker</span>
            </button>

            <button 
              onClick={() => { navigate('/candidate-review'); setIsMobileMenuOpen(false); }}
              className="w-full py-2.5 px-3 text-slate-400 hover:bg-slate-800 hover:text-white rounded-xl flex items-center gap-3 transition"
            >
              <UserCheck className="w-4 h-4" />
              <span>Candidate Review</span>
            </button>
          </nav>
        </div>

        <div className="pt-3 border-t border-slate-800">
          <button 
            onClick={() => navigate('/login')}
            className="w-full py-2.5 px-3 text-rose-400 hover:bg-rose-950/30 rounded-xl font-bold text-xs flex items-center gap-2 transition"
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
            <button 
              onClick={() => setIsMobileMenuOpen(true)}
              className="lg:hidden p-2 rounded-xl text-slate-600 hover:bg-slate-100 transition"
              title="Open Menu"
            >
              <Menu className="w-5 h-5" />
            </button>

            <h1 className="text-lg font-black text-slate-900 tracking-tight hidden sm:block">Job Posting & Lifecycle Wizard</h1>
          </div>

          <div className="flex items-center gap-3">
            <button className="p-2 text-slate-600 hover:bg-slate-100 rounded-xl relative transition">
              <Bell className="w-4 h-4" />
              <span className="bg-purple-600 text-white text-[9px] font-black w-4 h-4 rounded-full absolute -top-0.5 -right-0.5 ring-2 ring-white flex items-center justify-center">
                2
              </span>
            </button>

            <div className="relative">
              <div 
                onClick={() => setIsProfileDropdownOpen(!isProfileDropdownOpen)}
                className="w-8 h-8 rounded-xl bg-purple-100 border border-purple-300 text-purple-700 font-bold text-xs flex items-center justify-center cursor-pointer hover:bg-purple-200 transition"
              >
                HR
              </div>

              {isProfileDropdownOpen && (
                <div className="absolute right-0 mt-2 w-48 bg-white border border-slate-200 rounded-2xl shadow-xl p-1.5 z-50 text-xs font-bold space-y-0.5">
                  <div className="px-3 py-2 border-b border-slate-100 mb-1">
                    <p className="text-slate-900 font-black">NexusTech Hiring</p>
                    <p className="text-[10px] text-slate-400 font-medium">recruiter@nexustech.com</p>
                  </div>
                  <button onClick={() => navigate('/login')} className="w-full py-2 px-3 hover:bg-rose-50 text-rose-600 rounded-xl flex items-center gap-2 transition">
                    <LogOut className="w-3.5 h-3.5" /> Logout
                  </button>
                </div>
              )}
            </div>
          </div>
        </header>

        {/* Wizard Form Workspace */}
        <main className="flex-grow p-6 max-w-6xl mx-auto w-full grid grid-cols-1 lg:grid-cols-3 gap-6">
          
          {/* Left 2-Cols: Creation Form */}
          <div className="lg:col-span-2 bg-white border border-slate-200 rounded-3xl p-6 shadow-2xs space-y-5">
            <div>
              <h2 className="text-xl font-black text-slate-900">Create New Job Listing</h2>
              <p className="text-xs text-slate-500 font-medium mt-0.5">
                Define role requirements to match candidates in the Swipe discovery engine.
              </p>
            </div>

            <form onSubmit={handlePublishJob} className="space-y-4 text-xs font-bold text-slate-700">
              
              {/* Role Title */}
              <div>
                <label className="block text-[10px] uppercase text-slate-400 mb-1">Job Title *</label>
                <input 
                  type="text" 
                  required
                  placeholder="e.g. Senior Full Stack Engineer"
                  value={jobTitle}
                  onChange={(e) => setJobTitle(e.target.value)}
                  className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl font-medium focus:outline-none focus:border-purple-600 transition"
                />
              </div>

              {/* Category & Role Type */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-[10px] uppercase text-slate-400 mb-1">Company Category</label>
                  <select 
                    value={category}
                    onChange={(e) => setCategory(e.target.value)}
                    className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl font-bold text-slate-700 focus:outline-none focus:border-purple-600 cursor-pointer"
                  >
                    <option value="MNCs">MNCs</option>
                    <option value="Startups">Startups</option>
                    <option value="Newly Founded">Newly Founded</option>
                    <option value="Fresher Friendly">Fresher Friendly</option>
                    <option value="Low Competition">Low Competition</option>
                  </select>
                </div>

                <div>
                  <label className="block text-[10px] uppercase text-slate-400 mb-1">Role Type</label>
                  <select 
                    value={roleType}
                    onChange={(e) => setRoleType(e.target.value)}
                    className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl font-bold text-slate-700 focus:outline-none focus:border-purple-600 cursor-pointer"
                  >
                    <option value="Full-Time">Full-Time</option>
                    <option value="Internship">Internship</option>
                    <option value="Contract">Contract</option>
                  </select>
                </div>
              </div>

              {/* Location & Salary Range */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-[10px] uppercase text-slate-400 mb-1">Location *</label>
                  <input 
                    type="text" 
                    required
                    placeholder="e.g. Bangalore (Hybrid) or Remote"
                    value={location}
                    onChange={(e) => setLocation(e.target.value)}
                    className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl font-medium focus:outline-none focus:border-purple-600 transition"
                  />
                </div>

                <div>
                  <label className="block text-[10px] uppercase text-slate-400 mb-1">Salary Range</label>
                  <div className="flex gap-2">
                    <input 
                      type="text" 
                      placeholder="Min ($80k)"
                      value={salaryMin}
                      onChange={(e) => setSalaryMin(e.target.value)}
                      className="w-1/2 px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl font-medium focus:outline-none focus:border-purple-600 transition"
                    />
                    <input 
                      type="text" 
                      placeholder="Max ($110k)"
                      value={salaryMax}
                      onChange={(e) => setSalaryMax(e.target.value)}
                      className="w-1/2 px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl font-medium focus:outline-none focus:border-purple-600 transition"
                    />
                  </div>
                </div>
              </div>

              {/* Required Skills for ATS Engine */}
              <div>
                <label className="block text-[10px] uppercase text-slate-400 mb-1">ATS Required Skills</label>
                <div className="flex flex-wrap gap-1.5 mb-2">
                  {requiredSkills.map((skill, index) => (
                    <span key={index} className="text-xs font-bold bg-purple-50 text-purple-700 border border-purple-200 px-3 py-1 rounded-xl flex items-center gap-1.5">
                      {skill}
                      <button type="button" onClick={() => handleRemoveSkill(skill)} className="text-purple-400 hover:text-purple-900 cursor-pointer">
                        <X className="w-3 h-3" />
                      </button>
                    </span>
                  ))}
                </div>

                <div className="flex gap-2">
                  <input 
                    type="text" 
                    placeholder="Add skill tag (e.g. Node.js, Python)..."
                    value={newSkill}
                    onChange={(e) => setNewSkill(e.target.value)}
                    className="flex-grow px-3.5 py-2 bg-slate-50 border border-slate-200 rounded-xl font-medium focus:outline-none focus:border-purple-600"
                  />
                  <button type="button" onClick={handleAddSkill} className="px-3.5 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold rounded-xl flex items-center gap-1 cursor-pointer">
                    <Plus className="w-3.5 h-3.5" /> Add
                  </button>
                </div>
              </div>

              {/* Description */}
              <div>
                <label className="block text-[10px] uppercase text-slate-400 mb-1">Job Summary & Responsibilities *</label>
                <textarea 
                  rows="4"
                  required
                  placeholder="Describe core project responsibilities and requirements..."
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl font-medium text-slate-800 focus:outline-none focus:border-purple-600 transition"
                />
              </div>

              <button 
                type="submit" 
                className="w-full py-3 bg-purple-600 hover:bg-purple-700 text-white font-bold text-xs rounded-xl shadow-md shadow-purple-600/20 transition flex items-center justify-center gap-2 cursor-pointer"
              >
                <span>Publish Job & Inspect Candidates</span>
                <ArrowRight className="w-4 h-4" />
              </button>

            </form>
          </div>

          {/* Right Col: Live Card Preview */}
          <div className="space-y-4">
            <h3 className="text-xs font-black text-slate-900 uppercase tracking-wider flex items-center gap-1.5">
              <Eye className="w-4 h-4 text-purple-600" /> Candidate Card Preview
            </h3>

            <div className="bg-white border border-slate-200 rounded-3xl p-6 shadow-lg space-y-4 pointer-events-none select-none">
              <div className="flex justify-between items-start gap-2">
                <div>
                  <div className="flex items-center gap-1.5 mb-1">
                    <span className="text-[10px] font-bold bg-purple-50 text-purple-700 border border-purple-200 px-2 py-0.5 rounded-full">
                      {category}
                    </span>
                    <span className="text-[10px] font-bold bg-slate-100 text-slate-700 px-2 py-0.5 rounded-full">
                      {roleType}
                    </span>
                  </div>
                  <h4 className="text-lg font-black text-slate-900 leading-snug">
                    {jobTitle || "Job Title Preview"}
                  </h4>
                  <p className="text-xs font-semibold text-slate-500 flex items-center gap-1 mt-0.5">
                    <Building2 className="w-3.5 h-3.5 text-slate-400" /> NexusTech Global
                  </p>
                </div>

                <div className="bg-purple-600 text-white text-xs font-black px-2.5 py-1 rounded-xl flex items-center gap-1">
                  <Sparkles className="w-3 h-3" /> AI Match
                </div>
              </div>

              <div className="grid grid-cols-2 gap-2 py-2 border-y border-slate-100 text-[11px] text-slate-600 font-medium">
                <div className="flex items-center gap-1 truncate">
                  <MapPin className="w-3.5 h-3.5 text-purple-600" /> {location || "Location"}
                </div>
                <div className="flex items-center gap-1 truncate">
                  <DollarSign className="w-3.5 h-3.5 text-emerald-600" /> {salaryMin && salaryMax ? `${salaryMin} - ${salaryMax}` : "$ Salary Range"}
                </div>
              </div>

              <div className="flex flex-wrap gap-1">
                {requiredSkills.map((skill, index) => (
                  <span key={index} className="text-[10px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200 px-2 py-0.5 rounded-md">
                    {skill}
                  </span>
                ))}
              </div>

              <p className="text-xs text-slate-500 line-clamp-3">
                {description || "Job description overview will appear here as you type in the form."}
              </p>
            </div>
          </div>

        </main>
      </div>

    </div>
  );
}