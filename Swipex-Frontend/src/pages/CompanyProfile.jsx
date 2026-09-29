import React, { useState, useEffect } from 'react';
import Navbar from '../components/Navbar';
import Sidebar from '../components/Sidebar';
import { 
  Building2, MapPin, Globe, Users, Briefcase, 
  Sparkles, RefreshCw, ExternalLink, ArrowUpRight 
} from 'lucide-react';
import { CompanyService } from '../services/api';

export default function CompanyProfile() {
  const [companies, setCompanies] = useState([]);
  const [selectedCompany, setSelectedCompany] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadCompanies();
  }, []);

  const loadCompanies = async () => {
    setLoading(true);
    try {
      const res = await CompanyService.getCompanies();
      const list = res?.results || res || [];
      
      if (list.length > 0) {
        setCompanies(list);
        setSelectedCompany(list[0]);
      } else {
        setCompanies(FALLBACK_COMPANIES);
        setSelectedCompany(FALLBACK_COMPANIES[0]);
      }
    } catch (err) {
      console.warn("Backend offline, loading fallback companies:", err);
      setCompanies(FALLBACK_COMPANIES);
      setSelectedCompany(FALLBACK_COMPANIES[0]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col font-sans">
      <Navbar />

      <div className="flex flex-1">
        <Sidebar />

        <main className="flex-1 p-8 max-w-6xl space-y-8">
          {/* Header */}
          <div>
            <h1 className="text-2xl font-black text-slate-900 tracking-tight">Featured Employers & Companies</h1>
            <p className="text-xs text-slate-500 font-medium">Explore company cultures, engineering stacks, and active job openings</p>
          </div>

          {loading ? (
            <div className="text-center py-20 space-y-3">
              <RefreshCw className="w-8 h-8 text-purple-600 animate-spin mx-auto" />
              <p className="text-xs font-bold text-slate-400">Loading company profiles...</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
              
              {/* Left Selector Column (4 cols) */}
              <div className="lg:col-span-4 space-y-3">
                <h2 className="text-xs font-black text-slate-400 uppercase tracking-wider px-1">Directory</h2>
                <div className="space-y-2">
                  {companies.map((comp) => {
                    const id = comp.id || comp.company_id;
                    const isSelected = selectedCompany && (selectedCompany.id === id || selectedCompany.company_id === id);

                    return (
                      <div
                        key={id}
                        onClick={() => setSelectedCompany(comp)}
                        className={`p-4 rounded-2xl border cursor-pointer transition flex items-center justify-between ${
                          isSelected
                            ? 'bg-purple-50/70 border-purple-300 shadow-2xs'
                            : 'bg-white border-slate-200 hover:bg-slate-100'
                        }`}
                      >
                        <div className="flex items-center gap-3">
                          <div className={`w-10 h-10 rounded-xl flex items-center justify-center font-bold ${
                            isSelected ? 'bg-purple-600 text-white' : 'bg-slate-100 text-slate-600'
                          }`}>
                            <Building2 className="w-5 h-5" />
                          </div>
                          <div>
                            <h3 className="text-xs font-black text-slate-900">{comp.name || comp.company_name}</h3>
                            <p className="text-[10px] text-slate-400 font-medium">{comp.industry || "Tech & Software"}</p>
                          </div>
                        </div>

                        {isSelected && (
                          <span className="w-2 h-2 rounded-full bg-purple-600" />
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Right Detail Pane (8 cols) */}
              {selectedCompany && (
                <div className="lg:col-span-8 space-y-6">
                  {/* Company Hero Card */}
                  <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm space-y-6">
                    <div className="flex justify-between items-start">
                      <div className="flex items-center gap-4">
                        <div className="w-14 h-14 rounded-2xl bg-purple-600 text-white flex items-center justify-center shadow-md">
                          <Building2 className="w-7 h-7" />
                        </div>
                        <div>
                          <h2 className="text-xl font-black text-slate-900">{selectedCompany.name || selectedCompany.company_name}</h2>
                          <p className="text-xs font-bold text-slate-400">{selectedCompany.industry || "Tech Platform"}</p>
                        </div>
                      </div>

                      {selectedCompany.website && (
                        <a 
                          href={selectedCompany.website} 
                          target="_blank" 
                          rel="noreferrer"
                          className="px-3.5 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl text-xs font-bold flex items-center gap-1.5 transition"
                        >
                          <span>Website</span>
                          <ExternalLink className="w-3.5 h-3.5" />
                        </a>
                      )}
                    </div>

                    <p className="text-xs text-slate-600 leading-relaxed font-medium">
                      {selectedCompany.description || "Leading innovator building high-impact platforms and engineering solutions."}
                    </p>

                    <div className="grid grid-cols-2 md:grid-cols-3 gap-3 pt-2">
                      <div className="p-3 bg-slate-50 border border-slate-100 rounded-2xl space-y-1">
                        <span className="text-[10px] font-black uppercase text-slate-400 flex items-center gap-1">
                          <MapPin className="w-3 h-3 text-purple-600" /> Headquarters
                        </span>
                        <p className="text-xs font-bold text-slate-800">{selectedCompany.location || "Bengaluru, India"}</p>
                      </div>

                      <div className="p-3 bg-slate-50 border border-slate-100 rounded-2xl space-y-1">
                        <span className="text-[10px] font-black uppercase text-slate-400 flex items-center gap-1">
                          <Users className="w-3 h-3 text-purple-600" /> Company Size
                        </span>
                        <p className="text-xs font-bold text-slate-800">{selectedCompany.employee_count || "250 - 500 Employees"}</p>
                      </div>

                      <div className="p-3 bg-slate-50 border border-slate-100 rounded-2xl space-y-1">
                        <span className="text-[10px] font-black uppercase text-slate-400 flex items-center gap-1">
                          <Sparkles className="w-3 h-3 text-purple-600" /> Match Rating
                        </span>
                        <p className="text-xs font-bold text-purple-600">92% Candidate Alignment</p>
                      </div>
                    </div>
                  </div>

                  {/* Tech Stack */}
                  {selectedCompany.tech_stack && selectedCompany.tech_stack.length > 0 && (
                    <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm space-y-3">
                      <h3 className="text-xs font-black text-slate-900 uppercase tracking-wider">Tech Stack & Ecosystem</h3>
                      <div className="flex flex-wrap gap-2">
                        {selectedCompany.tech_stack.map((tech, idx) => (
                          <span key={idx} className="text-xs font-bold bg-purple-50 text-purple-700 border border-purple-200 px-3 py-1 rounded-xl">
                            {tech}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Active Job Openings List */}
                  <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm space-y-4">
                    <h3 className="text-xs font-black text-slate-900 uppercase tracking-wider flex items-center gap-2">
                      <Briefcase className="w-4 h-4 text-purple-600" /> Open Positions
                    </h3>

                    <div className="space-y-3">
                      {(selectedCompany.openings || DEFAULT_OPENINGS).map((op, i) => (
                        <div key={i} className="p-4 bg-slate-50 border border-slate-200 rounded-2xl flex items-center justify-between">
                          <div>
                            <h4 className="text-xs font-bold text-slate-900">{op.title}</h4>
                            <p className="text-[10px] text-slate-400 font-medium">{op.location} • {op.salary}</p>
                          </div>
                          <button 
                            onClick={() => window.location.href = '/discovery'}
                            className="text-xs font-black text-purple-600 hover:text-purple-700 flex items-center gap-1 cursor-pointer"
                          >
                            <span>Swipe to Apply</span>
                            <ArrowUpRight className="w-4 h-4" />
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>

                </div>
              )}

            </div>
          )}
        </main>
      </div>
    </div>
  );
}

const DEFAULT_OPENINGS = [
  { title: "Senior Python Engineer", location: "Remote / Bengaluru", salary: "₹18 LPA - ₹28 LPA" },
  { title: "Frontend React Specialist", location: "Bengaluru, India", salary: "₹14 LPA - ₹22 LPA" }
];

const FALLBACK_COMPANIES = [
  {
    id: "comp-1",
    name: "SwipeX Tech",
    industry: "AI & Recruitment Intelligence",
    location: "Bengaluru, India",
    employee_count: "100 - 250 Employees",
    website: "https://swipex.ai",
    description: "Building next-generation gesture-driven career intelligence tools connecting candidates and recruiters seamlessly.",
    tech_stack: ["Python", "Django", "React", "Tailwind CSS", "PostgreSQL", "Docker"],
    openings: [
      { title: "Senior Python Engineer", location: "Remote / Bengaluru", salary: "₹18 LPA - ₹28 LPA" },
      { title: "Full Stack AI Developer", location: "Bengaluru", salary: "₹16 LPA - ₹24 LPA" }
    ]
  },
  {
    id: "comp-2",
    name: "Razorpay",
    industry: "Fintech & Payments",
    location: "Bengaluru, India",
    employee_count: "1000+ Employees",
    website: "https://razorpay.com",
    description: "Empowering businesses with seamless digital payment gateways and financial software infrastructure.",
    tech_stack: ["Go", "React", "Node.js", "Kubernetes", "Redis"],
    openings: [
      { title: "Frontend React Specialist", location: "Bengaluru", salary: "₹14 LPA - ₹22 LPA" }
    ]
  }
];