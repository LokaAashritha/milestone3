import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Zap, ArrowRight, Mail, Lock, User, Building2, ShieldCheck, Code2, Sparkles, RefreshCw, AlertCircle } from 'lucide-react';
import { AuthService } from '../services/api';

export default function Register() {
  const navigate = useNavigate();
  const [role, setRole] = useState('candidate');
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [skills, setSkills] = useState('React, Python, SQL');
  const [company, setCompany] = useState('');
  const [adminCode, setAdminCode] = useState('');
  
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState(null);

  const handleRegister = async (e) => {
    e.preventDefault();
    setLoading(true);
    setErrorMessage(null);

    // Format skills string into clean array for FastAPI
    const formattedSkills = skills
      ? skills.split(',').map((s) => s.trim()).filter(Boolean)
      : [];

    // Correct payload schema for FastAPI backend
    const payload = {
      full_name: fullName,
      email: email.trim(),
      password,
      role: role === 'candidate' ? 'job_seeker' : role,
      skills: role === 'candidate' ? formattedSkills : [],
      company: role === 'recruiter' ? company : undefined,
      adminCode: role === 'admin' ? adminCode : undefined,
    };

    try {
      // 1. Send registration data to save in backend database
      const res = await AuthService.register(payload);
      const token = res?.access_token || res?.token;

      if (!token) {
        // Redirect to login on successful creation without auto-login token
        navigate('/login');
        return;
      }

      // 2. Persist real registered user session
      localStorage.setItem('swipex_auth_token', token);
      localStorage.setItem('swipex_role', role);
      localStorage.setItem('swipex_user_email', email);

      // 3. Route to workspace
      if (role === 'candidate') navigate('/discovery');
      else if (role === 'recruiter') navigate('/recruiter-dashboard');
      else if (role === 'admin') navigate('/admin-dashboard');

    } catch (err) {
      console.error("Registration failed:", err);
      const message = err?.response?.data?.detail 
        || err?.message 
        || "Registration failed. Email may already be registered or backend service is unreachable.";
      setErrorMessage(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative h-screen w-full flex items-center justify-center font-sans text-white selection:bg-purple-500 selection:text-white overflow-hidden px-6 sm:px-12">
      <img 
        src="https://wallpapers.com/images/hd/violet-background-61jy6ewdwsuhozak.jpg" 
        alt="Violet Background" 
        className="absolute inset-0 w-full h-full object-cover scale-105"
      />
      <div className="absolute inset-0 bg-slate-950/60 backdrop-blur-[2px]" />

      <div className="relative z-10 w-full max-w-6xl mx-auto flex flex-col lg:flex-row items-center justify-between gap-8 max-h-[92vh]">
        <div className="w-full max-w-md bg-white/10 backdrop-blur-md border border-white/20 rounded-3xl p-6 sm:p-7 shadow-2xl space-y-4">
          
          <div className="text-center space-y-1">
            <div 
              onClick={() => navigate('/')}
              className="w-10 h-10 rounded-xl bg-purple-600/90 flex items-center justify-center mx-auto cursor-pointer"
            >
              <Zap className="w-5 h-5 text-white fill-white" />
            </div>
            <h2 className="text-xl font-black text-white">Create SwipeX Account</h2>
            <p className="text-[11px] text-purple-200/80">Join the intelligent career discovery network</p>
          </div>

          {errorMessage && (
            <div className="p-3 bg-rose-500/20 border border-rose-500/40 rounded-xl flex items-center gap-2 text-xs font-bold text-rose-200">
              <AlertCircle className="w-4 h-4 flex-shrink-0 text-rose-400" />
              <span>{errorMessage}</span>
            </div>
          )}

          <div className="grid grid-cols-3 gap-1 bg-black/20 p-1 rounded-xl border border-white/10 text-xs font-bold">
            <button
              type="button"
              onClick={() => setRole('candidate')}
              className={`py-1.5 rounded-lg flex items-center justify-center gap-1 cursor-pointer ${
                role === 'candidate' ? 'bg-purple-600 text-white' : 'text-purple-200/70 hover:text-white'
              }`}
            >
              <User className="w-3 h-3" /> Candidate
            </button>
            <button
              type="button"
              onClick={() => setRole('recruiter')}
              className={`py-1.5 rounded-lg flex items-center justify-center gap-1 cursor-pointer ${
                role === 'recruiter' ? 'bg-purple-600 text-white' : 'text-purple-200/70 hover:text-white'
              }`}
            >
              <Building2 className="w-3 h-3" /> Recruiter
            </button>
            <button
              type="button"
              onClick={() => setRole('admin')}
              className={`py-1.5 rounded-lg flex items-center justify-center gap-1 cursor-pointer ${
                role === 'admin' ? 'bg-purple-600 text-white' : 'text-purple-200/70 hover:text-white'
              }`}
            >
              <ShieldCheck className="w-3 h-3" /> Admin
            </button>
          </div>

          <form onSubmit={handleRegister} className="space-y-3">
            <div>
              <label className="block text-[11px] font-bold text-purple-200 mb-1">Full Name</label>
              <div className="relative">
                <User className="w-3.5 h-3.5 text-purple-300/60 absolute left-3.5 top-3" />
                <input 
                  type="text" 
                  required 
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="Alex Morgan" 
                  className="w-full pl-9 pr-3 py-2 bg-black/20 border border-white/10 rounded-xl text-xs text-white focus:outline-none focus:border-purple-400"
                />
              </div>
            </div>

            <div>
              <label className="block text-[11px] font-bold text-purple-200 mb-1">Email Address</label>
              <div className="relative">
                <Mail className="w-3.5 h-3.5 text-purple-300/60 absolute left-3.5 top-3" />
                <input 
                  type="email" 
                  required 
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="alex@example.com" 
                  className="w-full pl-9 pr-3 py-2 bg-black/20 border border-white/10 rounded-xl text-xs text-white focus:outline-none focus:border-purple-400"
                />
              </div>
            </div>

            <div>
              <label className="block text-[11px] font-bold text-purple-200 mb-1">Password</label>
              <div className="relative">
                <Lock className="w-3.5 h-3.5 text-purple-300/60 absolute left-3.5 top-3" />
                <input 
                  type="password" 
                  required 
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••" 
                  className="w-full pl-9 pr-3 py-2 bg-black/20 border border-white/10 rounded-xl text-xs text-white focus:outline-none focus:border-purple-400"
                />
              </div>
            </div>

            {role === 'candidate' && (
              <div>
                <label className="block text-[11px] font-bold text-purple-200 mb-1">Primary Skills</label>
                <div className="relative">
                  <Code2 className="w-3.5 h-3.5 text-purple-300/60 absolute left-3.5 top-3" />
                  <input 
                    type="text" 
                    value={skills}
                    onChange={(e) => setSkills(e.target.value)}
                    placeholder="React, Python, Java, SQL" 
                    className="w-full pl-9 pr-3 py-2 bg-black/20 border border-white/10 rounded-xl text-xs text-white focus:outline-none focus:border-purple-400"
                  />
                </div>
              </div>
            )}

            {role === 'recruiter' && (
              <div>
                <label className="block text-[11px] font-bold text-purple-200 mb-1">Company Name</label>
                <div className="relative">
                  <Building2 className="w-3.5 h-3.5 text-purple-300/60 absolute left-3.5 top-3" />
                  <input 
                    type="text" 
                    required
                    value={company}
                    onChange={(e) => setCompany(e.target.value)}
                    placeholder="NexusTech Global" 
                    className="w-full pl-9 pr-3 py-2 bg-black/20 border border-white/10 rounded-xl text-xs text-white focus:outline-none focus:border-purple-400"
                  />
                </div>
              </div>
            )}

            {role === 'admin' && (
              <div>
                <label className="block text-[11px] font-bold text-purple-200 mb-1">Admin Security Key</label>
                <div className="relative">
                  <ShieldCheck className="w-3.5 h-3.5 text-purple-300/60 absolute left-3.5 top-3" />
                  <input 
                    type="text" 
                    required
                    value={adminCode}
                    onChange={(e) => setAdminCode(e.target.value)}
                    placeholder="SPX-ADMIN-KEY" 
                    className="w-full pl-9 pr-3 py-2 bg-black/20 border border-white/10 rounded-xl text-xs text-white focus:outline-none focus:border-purple-400"
                  />
                </div>
              </div>
            )}

            <button 
              type="submit" 
              disabled={loading}
              className="w-full py-2.5 bg-purple-600 hover:bg-purple-500 text-white text-xs font-bold rounded-xl shadow-lg flex items-center justify-center gap-2 mt-2 cursor-pointer disabled:opacity-50"
            >
              {loading ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <ArrowRight className="w-3.5 h-3.5" />}
              <span>Create Account</span>
            </button>
          </form>

          <p className="text-center text-[11px] text-purple-200/80">
            Already registered?{' '}
            <span onClick={() => navigate('/login')} className="text-white font-bold cursor-pointer hover:underline">
              Sign In
            </span>
          </p>

        </div>

        <div className="hidden lg:flex flex-col justify-center max-w-lg space-y-6 pl-6">
          <div className="inline-flex items-center gap-2 bg-purple-500/20 border border-purple-400/30 text-purple-200 px-3.5 py-1 rounded-full text-xs font-bold w-fit">
            <Sparkles className="w-3.5 h-3.5 text-purple-300" />
            <span>AI Career Intelligence & Matching Engine</span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-black text-white">
            Build Your Profile. <br />
            <span className="text-purple-300">Unlock Targeted Roles.</span>
          </h1>
        </div>

      </div>
    </div>
  );
}