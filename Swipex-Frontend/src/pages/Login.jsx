// import React, { useState } from 'react';
// import { useNavigate } from 'react-router-dom';
// import { Zap, ArrowRight, Mail, Lock, User, Building2, ShieldCheck, Sparkles, CheckCircle2, RefreshCw } from 'lucide-react';
// import { AuthService } from '../services/api';

// export default function Login() {
//   const navigate = useNavigate();
//   const [role, setRole] = useState('candidate'); // 'candidate' | 'recruiter' | 'admin'
//   const [email, setEmail] = useState('');
//   const [password, setPassword] = useState('');
//   const [loading, setLoading] = useState(false);

//   const handleLogin = async (e) => {
//     e.preventDefault();
//     setLoading(true);

//     try {
//       // Connect to backend auth service
//       const res = await AuthService.login(email, password);
//       const token = res?.access_token || res?.token || 'mock-jwt-token-123';
      
//       // Store session data
//       localStorage.setItem('swipex_auth_token', token);
//       localStorage.setItem('swipex_role', role);
//       localStorage.setItem('swipex_user_email', email);

//       // Navigate based on selected role
//       if (role === 'candidate') {
//         navigate('/discovery');
//       } else if (role === 'recruiter') {
//         navigate('/recruiter-dashboard');
//       } else if (role === 'admin') {
//         navigate('/admin-dashboard');
//       }
//     } catch (err) {
//       console.warn("Backend login offline, running fallback authentication:", err);
      
//       // Fallback session state so offline testing works seamlessly
//       localStorage.setItem('swipex_auth_token', 'demo-jwt-token');
//       localStorage.setItem('swipex_role', role);
//       localStorage.setItem('swipex_user_email', email || 'candidate@swipex.ai');

//       if (role === 'candidate') navigate('/discovery');
//       else if (role === 'recruiter') navigate('/recruiter-dashboard');
//       else if (role === 'admin') navigate('/admin-dashboard');
//     } finally {
//       setLoading(false);
//     }
//   };

//   return (
//     <div className="relative h-screen w-full flex items-center justify-center font-sans text-white selection:bg-purple-500 selection:text-white overflow-hidden px-6 sm:px-12">
      
//       {/* 1. Full Screen Violet Background */}
//       <img 
//         src="https://wallpapers.com/images/hd/violet-background-61jy6ewdwsuhozak.jpg" 
//         alt="Violet Background" 
//         className="absolute inset-0 w-full h-full object-cover scale-105"
//       />
//       <div className="absolute inset-0 bg-slate-950/60 backdrop-blur-[2px]" />

//       {/* 2. Main Container (Fitted viewport height) */}
//       <div className="relative z-10 w-full max-w-6xl mx-auto flex flex-col lg:flex-row items-center justify-between gap-8 max-h-[92vh]">
        
//         {/* LEFT SIDE: Transparent Glass Login Box */}
//         <div className="w-full max-w-md bg-white/10 backdrop-blur-md border border-white/20 rounded-3xl p-6 sm:p-7 shadow-2xl transition-all duration-300 hover:border-white/30 space-y-4">
          
//           {/* Brand Header */}
//           <div className="text-center space-y-1">
//             <div 
//               onClick={() => navigate('/')}
//               className="w-10 h-10 rounded-xl bg-purple-600/90 flex items-center justify-center mx-auto shadow-lg shadow-purple-600/40 cursor-pointer transform hover:scale-105 transition duration-200"
//             >
//               <Zap className="w-5 h-5 text-white fill-white" />
//             </div>
//             <h2 className="text-xl font-black tracking-tight text-white">Welcome Back to SwipeX</h2>
//             <p className="text-[11px] text-purple-200/80 font-medium">Sign in to access your intelligent workspace</p>
//           </div>

//           {/* Role Selector Tabs */}
//           <div className="grid grid-cols-3 gap-1 bg-black/20 p-1 rounded-xl border border-white/10 text-xs font-bold">
//             <button
//               type="button"
//               onClick={() => setRole('candidate')}
//               className={`py-1.5 rounded-lg transition-all duration-200 flex items-center justify-center gap-1 cursor-pointer ${
//                 role === 'candidate' ? 'bg-purple-600 text-white shadow-md' : 'text-purple-200/70 hover:text-white'
//               }`}
//             >
//               <User className="w-3 h-3" /> Candidate
//             </button>
            
//             <button
//               type="button"
//               onClick={() => setRole('recruiter')}
//               className={`py-1.5 rounded-lg transition-all duration-200 flex items-center justify-center gap-1 cursor-pointer ${
//                 role === 'recruiter' ? 'bg-purple-600 text-white shadow-md' : 'text-purple-200/70 hover:text-white'
//               }`}
//             >
//               <Building2 className="w-3 h-3" /> Recruiter
//             </button>

//             <button
//               type="button"
//               onClick={() => setRole('admin')}
//               className={`py-1.5 rounded-lg transition-all duration-200 flex items-center justify-center gap-1 cursor-pointer ${
//                 role === 'admin' ? 'bg-purple-600 text-white shadow-md' : 'text-purple-200/70 hover:text-white'
//               }`}
//             >
//               <ShieldCheck className="w-3 h-3" /> Admin
//             </button>
//           </div>

//           {/* Transparent Input Form */}
//           <form onSubmit={handleLogin} className="space-y-3">
//             <div>
//               <label className="block text-[11px] font-bold text-purple-200 mb-1">Email Address</label>
//               <div className="relative">
//                 <Mail className="w-3.5 h-3.5 text-purple-300/60 absolute left-3.5 top-3" />
//                 <input 
//                   type="email" 
//                   required 
//                   value={email}
//                   onChange={(e) => setEmail(e.target.value)}
//                   placeholder={
//                     role === 'candidate' ? 'alex@example.com' :
//                     role === 'recruiter' ? 'hr@techcorp.com' : 'admin@swipex.io'
//                   } 
//                   className="w-full pl-9 pr-3 py-2 bg-black/20 border border-white/10 rounded-xl text-xs text-white placeholder:text-purple-200/40 focus:outline-none focus:border-purple-400 focus:bg-black/40 transition"
//                 />
//               </div>
//             </div>

//             <div>
//               <div className="flex justify-between items-center mb-1">
//                 <label className="text-[11px] font-bold text-purple-200">Password</label>
//                 <a href="#" className="text-[10px] font-bold text-purple-300 hover:text-white transition">Forgot password?</a>
//               </div>
//               <div className="relative">
//                 <Lock className="w-3.5 h-3.5 text-purple-300/60 absolute left-3.5 top-3" />
//                 <input 
//                   type="password" 
//                   required 
//                   value={password}
//                   onChange={(e) => setPassword(e.target.value)}
//                   placeholder="••••••••" 
//                   className="w-full pl-9 pr-3 py-2 bg-black/20 border border-white/10 rounded-xl text-xs text-white placeholder:text-purple-200/40 focus:outline-none focus:border-purple-400 focus:bg-black/40 transition"
//                 />
//               </div>
//             </div>

//             <div className="flex items-center gap-2 pt-0.5">
//               <input type="checkbox" id="remember" className="w-3.5 h-3.5 accent-purple-500 rounded cursor-pointer" />
//               <label htmlFor="remember" className="text-[11px] text-purple-200/80 font-medium cursor-pointer">Keep me signed in</label>
//             </div>

//             <button 
//               type="submit" 
//               disabled={loading}
//               className="w-full py-2.5 bg-purple-600 hover:bg-purple-500 text-white text-xs font-bold rounded-xl shadow-lg shadow-purple-600/40 transform hover:-translate-y-0.5 transition-all duration-200 flex items-center justify-center gap-2 mt-2 cursor-pointer disabled:opacity-50"
//             >
//               {loading ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <ArrowRight className="w-3.5 h-3.5" />}
//               <span>Sign In as {role.charAt(0).toUpperCase() + role.slice(1)}</span>
//             </button>
//           </form>

//           {/* Divider */}
//           <div className="relative flex py-0.5 items-center">
//             <div className="flex-grow border-t border-white/10"></div>
//             <span className="flex-shrink mx-3 text-[9px] text-purple-200/60 font-bold uppercase tracking-wider">Or</span>
//             <div className="flex-grow border-t border-white/10"></div>
//           </div>

//           {/* Transparent Google Button */}
//           <button 
//             type="button" 
//             className="w-full py-2 px-3 bg-white/10 hover:bg-white/20 border border-white/20 rounded-xl text-xs font-bold text-white transition duration-200 flex items-center justify-center gap-2 cursor-pointer"
//           >
//             <svg className="w-3.5 h-3.5" viewBox="0 0 24 24">
//               <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
//               <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
//               <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z" />
//               <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z" />
//             </svg>
//             Continue with Google
//           </button>

//           {/* Navigation to Register */}
//           <p className="text-center text-[11px] text-purple-200/80">
//             Don't have an account?{' '}
//             <span onClick={() => navigate('/register')} className="text-white font-bold cursor-pointer hover:underline">
//               Create Profile
//             </span>
//           </p>

//         </div>

//         {/* RIGHT SIDE: Written Content & Feature Highlights */}
//         <div className="hidden lg:flex flex-col justify-center max-w-lg space-y-6 pl-6">
          
//           <div className="inline-flex items-center gap-2 bg-purple-500/20 border border-purple-400/30 text-purple-200 px-3.5 py-1 rounded-full text-xs font-bold w-fit">
//             <Sparkles className="w-3.5 h-3.5 text-purple-300" />
//             <span>AI Career Intelligence & Matching Engine</span>
//           </div>

//           <div className="space-y-3">
//             <h1 className="text-3xl sm:text-4xl font-black leading-tight tracking-tight text-white">
//               Swipe Right to Apply. <br />
//               <span className="text-purple-300">Match Smarter with AI.</span>
//             </h1>
//             <p className="text-purple-200/80 text-xs sm:text-sm leading-relaxed max-w-md">
//               SwipeX completely replaces tedious job search forms with real-time ATS match scoring, gesture discovery, and direct candidate-recruiter connections.
//             </p>
//           </div>

//           <div className="space-y-2.5">
//             <div className="flex items-center gap-2.5 text-xs text-purple-100 font-semibold">
//               <CheckCircle2 className="w-4 h-4 text-purple-400 flex-shrink-0" />
//               <span>Real-time ATS Keyword & Skill Gap Analysis</span>
//             </div>
//             <div className="flex items-center gap-2.5 text-xs text-purple-100 font-semibold">
//               <CheckCircle2 className="w-4 h-4 text-purple-400 flex-shrink-0" />
//               <span>Curated MNCs, Fast-Growing Startups & Low Competition Roles</span>
//             </div>
//             <div className="flex items-center gap-2.5 text-xs text-purple-100 font-semibold">
//               <CheckCircle2 className="w-4 h-4 text-purple-400 flex-shrink-0" />
//               <span>Direct Candidate Pipeline Management for Hiring Managers</span>
//             </div>
//           </div>

//           {/* Key Metrics Banner */}
//           <div className="grid grid-cols-3 gap-3 pt-3 border-t border-white/10">
//             <div>
//               <p className="text-xl font-black text-white">120k+</p>
//               <p className="text-[10px] text-purple-300/80">Matches Made</p>
//             </div>
//             <div>
//               <p className="text-xl font-black text-purple-300">85%</p>
//               <p className="text-[10px] text-purple-300/80">Faster Hiring</p>
//             </div>
//             <div>
//               <p className="text-xl font-black text-white">500+</p>
//               <p className="text-[10px] text-purple-300/80">Active Startups</p>
//             </div>
//           </div>

//         </div>

//       </div>
//     </div>
//   );
// }

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Zap, ArrowRight, Mail, Lock, User, Building2, ShieldCheck, Sparkles, CheckCircle2, RefreshCw, AlertCircle } from 'lucide-react';
import { AuthService } from '../services/api';

export default function Login() {
  const navigate = useNavigate();
  const [role, setRole] = useState('candidate'); // 'candidate' | 'recruiter' | 'admin'
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState(null);

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setErrorMessage(null);

    try {
      // 1. Send authentication request to live backend database
      const res = await AuthService.login(email, password);
      
      const token = res?.access_token || res?.token;
      const user = res?.user;

      if (!token) {
        throw new Error("Invalid response from authentication server.");
      }

      // 2. Save REAL JWT Token and user info returned by backend database
      localStorage.setItem('swipex_auth_token', token);
      localStorage.setItem('swipex_role', user?.role === 'job_seeker' ? 'candidate' : (user?.role || role));
      localStorage.setItem('swipex_user_email', user?.email || email);
      if (user?.id) localStorage.setItem('swipex_user_id', user.id);

      // 3. Route to user workspace based on verified role
      const userRole = user?.role === 'job_seeker' ? 'candidate' : (user?.role || role);
      if (userRole === 'candidate') navigate('/discovery');
      else if (userRole === 'recruiter') navigate('/recruiter-dashboard');
      else if (userRole === 'admin') navigate('/admin-dashboard');

    } catch (err) {
      console.error("Authentication failed:", err);
      // Display exact error message from backend or network
      const message = err?.response?.data?.detail 
        || err?.response?.data?.message 
        || err?.message
        || "Invalid email or password. Please check your credentials or register first.";
      setErrorMessage(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative h-screen w-full flex items-center justify-center font-sans text-white selection:bg-purple-500 selection:text-white overflow-hidden px-6 sm:px-12">
      
      {/* 1. Full Screen Violet Background */}
      <img 
        src="https://wallpapers.com/images/hd/violet-background-61jy6ewdwsuhozak.jpg" 
        alt="Violet Background" 
        className="absolute inset-0 w-full h-full object-cover scale-105"
      />
      <div className="absolute inset-0 bg-slate-950/60 backdrop-blur-[2px]" />

      {/* 2. Main Container */}
      <div className="relative z-10 w-full max-w-6xl mx-auto flex flex-col lg:flex-row items-center justify-between gap-8 max-h-[92vh]">
        
        {/* LEFT SIDE: Transparent Glass Login Box */}
        <div className="w-full max-w-md bg-white/10 backdrop-blur-md border border-white/20 rounded-3xl p-6 sm:p-7 shadow-2xl transition-all duration-300 hover:border-white/30 space-y-4">
          
          {/* Brand Header */}
          <div className="text-center space-y-1">
            <div 
              onClick={() => navigate('/')}
              className="w-10 h-10 rounded-xl bg-purple-600/90 flex items-center justify-center mx-auto shadow-lg shadow-purple-600/40 cursor-pointer transform hover:scale-105 transition duration-200"
            >
              <Zap className="w-5 h-5 text-white fill-white" />
            </div>
            <h2 className="text-xl font-black tracking-tight text-white">Welcome Back to SwipeX</h2>
            <p className="text-[11px] text-purple-200/80 font-medium">Sign in to access your intelligent workspace</p>
          </div>

          {/* Error Banner */}
          {errorMessage && (
            <div className="p-3 bg-rose-500/20 border border-rose-500/40 rounded-xl flex items-center gap-2 text-xs font-bold text-rose-200">
              <AlertCircle className="w-4 h-4 flex-shrink-0 text-rose-400" />
              <span>{errorMessage}</span>
            </div>
          )}

          {/* Role Selector Tabs */}
          <div className="grid grid-cols-3 gap-1 bg-black/20 p-1 rounded-xl border border-white/10 text-xs font-bold">
            <button
              type="button"
              onClick={() => setRole('candidate')}
              className={`py-1.5 rounded-lg transition-all duration-200 flex items-center justify-center gap-1 cursor-pointer ${
                role === 'candidate' ? 'bg-purple-600 text-white shadow-md' : 'text-purple-200/70 hover:text-white'
              }`}
            >
              <User className="w-3 h-3" /> Candidate
            </button>
            
            <button
              type="button"
              onClick={() => setRole('recruiter')}
              className={`py-1.5 rounded-lg transition-all duration-200 flex items-center justify-center gap-1 cursor-pointer ${
                role === 'recruiter' ? 'bg-purple-600 text-white shadow-md' : 'text-purple-200/70 hover:text-white'
              }`}
            >
              <Building2 className="w-3 h-3" /> Recruiter
            </button>

            <button
              type="button"
              onClick={() => setRole('admin')}
              className={`py-1.5 rounded-lg transition-all duration-200 flex items-center justify-center gap-1 cursor-pointer ${
                role === 'admin' ? 'bg-purple-600 text-white shadow-md' : 'text-purple-200/70 hover:text-white'
              }`}
            >
              <ShieldCheck className="w-3 h-3" /> Admin
            </button>
          </div>

          {/* Transparent Input Form */}
          <form onSubmit={handleLogin} className="space-y-3">
            <div>
              <label className="block text-[11px] font-bold text-purple-200 mb-1">Email Address</label>
              <div className="relative">
                <Mail className="w-3.5 h-3.5 text-purple-300/60 absolute left-3.5 top-3" />
                <input 
                  type="email" 
                  required 
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder={
                    role === 'candidate' ? 'alex@example.com' :
                    role === 'recruiter' ? 'hr@techcorp.com' : 'admin@swipex.io'
                  } 
                  className="w-full pl-9 pr-3 py-2 bg-black/20 border border-white/10 rounded-xl text-xs text-white placeholder:text-purple-200/40 focus:outline-none focus:border-purple-400 focus:bg-black/40 transition"
                />
              </div>
            </div>

            <div>
              <div className="flex justify-between items-center mb-1">
                <label className="text-[11px] font-bold text-purple-200">Password</label>
                <a href="#" className="text-[10px] font-bold text-purple-300 hover:text-white transition">Forgot password?</a>
              </div>
              <div className="relative">
                <Lock className="w-3.5 h-3.5 text-purple-300/60 absolute left-3.5 top-3" />
                <input 
                  type="password" 
                  required 
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••" 
                  className="w-full pl-9 pr-3 py-2 bg-black/20 border border-white/10 rounded-xl text-xs text-white placeholder:text-purple-200/40 focus:outline-none focus:border-purple-400 focus:bg-black/40 transition"
                />
              </div>
            </div>

            <button 
              type="submit" 
              disabled={loading}
              className="w-full py-2.5 bg-purple-600 hover:bg-purple-500 text-white text-xs font-bold rounded-xl shadow-lg shadow-purple-600/40 transform hover:-translate-y-0.5 transition-all duration-200 flex items-center justify-center gap-2 mt-2 cursor-pointer disabled:opacity-50"
            >
              {loading ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <ArrowRight className="w-3.5 h-3.5" />}
              <span>Sign In as {role.charAt(0).toUpperCase() + role.slice(1)}</span>
            </button>
          </form>

          {/* Divider & Google Button */}
          <div className="relative flex py-0.5 items-center">
            <div className="flex-grow border-t border-white/10"></div>
            <span className="flex-shrink mx-3 text-[9px] text-purple-200/60 font-bold uppercase tracking-wider">Or</span>
            <div className="flex-grow border-t border-white/10"></div>
          </div>

          <button 
            type="button" 
            className="w-full py-2 px-3 bg-white/10 hover:bg-white/20 border border-white/20 rounded-xl text-xs font-bold text-white transition duration-200 flex items-center justify-center gap-2 cursor-pointer"
          >
            Continue with Google
          </button>

          {/* Navigation to Register */}
          <p className="text-center text-[11px] text-purple-200/80">
            Don't have an account?{' '}
            <span onClick={() => navigate('/register')} className="text-white font-bold cursor-pointer hover:underline">
              Create Profile
            </span>
          </p>

        </div>

        {/* RIGHT SIDE: Written Content */}
        <div className="hidden lg:flex flex-col justify-center max-w-lg space-y-6 pl-6">
          <div className="inline-flex items-center gap-2 bg-purple-500/20 border border-purple-400/30 text-purple-200 px-3.5 py-1 rounded-full text-xs font-bold w-fit">
            <Sparkles className="w-3.5 h-3.5 text-purple-300" />
            <span>AI Career Intelligence & Matching Engine</span>
          </div>

          <div className="space-y-3">
            <h1 className="text-3xl sm:text-4xl font-black leading-tight tracking-tight text-white">
              Swipe Right to Apply. <br />
              <span className="text-purple-300">Match Smarter with AI.</span>
            </h1>
            <p className="text-purple-200/80 text-xs sm:text-sm leading-relaxed max-w-md">
              SwipeX completely replaces tedious job search forms with real-time ATS match scoring, gesture discovery, and direct candidate-recruiter connections.
            </p>
          </div>

          <div className="space-y-2.5">
            <div className="flex items-center gap-2.5 text-xs text-purple-100 font-semibold">
              <CheckCircle2 className="w-4 h-4 text-purple-400 flex-shrink-0" />
              <span>Real-time ATS Keyword & Skill Gap Analysis</span>
            </div>
            <div className="flex items-center gap-2.5 text-xs text-purple-100 font-semibold">
              <CheckCircle2 className="w-4 h-4 text-purple-400 flex-shrink-0" />
              <span>Curated MNCs, Fast-Growing Startups & Low Competition Roles</span>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}