import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Building2,
  PlusCircle,
  CheckSquare,
  Zap,
  LogOut,
  Menu,
  X,
  Bell,
  Briefcase,
  Sparkles,
  CheckCircle2,
  Plus,
  DollarSign,
  MapPin,
  ArrowRight,
  Eye,
  UserCheck,
  AlertCircle,
  Loader2
} from 'lucide-react';

import { CompanyService, JobService } from '../services/api';

export default function PostJob() {
  const navigate = useNavigate();

  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isProfileDropdownOpen, setIsProfileDropdownOpen] = useState(false);
  const [toastMessage, setToastMessage] = useState(null);
  const [errorMessage, setErrorMessage] = useState(null);
  const [isPublishing, setIsPublishing] = useState(false);

  // ---------------------------------------------------------------------------
  // Form State
  // ---------------------------------------------------------------------------

  const [jobTitle, setJobTitle] = useState('');
  const [category, setCategory] = useState('Startups');
  const [roleType, setRoleType] = useState('Full-Time');
  const [location, setLocation] = useState('');
  const [salaryMin, setSalaryMin] = useState('');
  const [salaryMax, setSalaryMax] = useState('');
  const [description, setDescription] = useState('');

  // Skills Management
  const [requiredSkills, setRequiredSkills] = useState([
    'React',
    'TypeScript'
  ]);
  const [newSkill, setNewSkill] = useState('');

  // ---------------------------------------------------------------------------
  // Toast
  // ---------------------------------------------------------------------------

  const showToast = (msg) => {
    setToastMessage(msg);

    setTimeout(() => {
      setToastMessage(null);
    }, 2500);
  };

  // ---------------------------------------------------------------------------
  // Skill Management
  // ---------------------------------------------------------------------------

  const handleAddSkill = (e) => {
    e.preventDefault();

    const skill = newSkill.trim();

    if (!skill) {
      return;
    }

    const alreadyExists = requiredSkills.some(
      (existingSkill) =>
        existingSkill.toLowerCase() === skill.toLowerCase()
    );

    if (!alreadyExists) {
      setRequiredSkills((previousSkills) => [
        ...previousSkills,
        skill
      ]);
    }

    setNewSkill('');
  };

  const handleRemoveSkill = (skillToRemove) => {
    setRequiredSkills((previousSkills) =>
      previousSkills.filter((skill) => skill !== skillToRemove)
    );
  };

  // ---------------------------------------------------------------------------
  // Backend Value Conversion
  // ---------------------------------------------------------------------------

  const mapRoleTypeToBackend = (value) => {
    switch (value) {
      case 'Internship':
        return 'internship';

      case 'Contract':
        return 'contract';

      case 'Full-Time':
      default:
        return 'full_time';
    }
  };

  const parseSalary = (value) => {
    if (!value || !String(value).trim()) {
      return null;
    }

    const cleaned = String(value)
      .replace(/[$₹,\s]/g, '')
      .replace(/[a-zA-Z]/g, '');

    const parsed = Number(cleaned);

    return Number.isFinite(parsed) ? parsed : null;
  };

  const generateKeywords = () => {
    const text = `${jobTitle} ${description} ${requiredSkills.join(' ')}`;

    const words = text
      .toLowerCase()
      .replace(/[^a-z0-9+#.\s-]/g, ' ')
      .split(/\s+/)
      .map((word) => word.trim())
      .filter((word) => word.length >= 3);

    return [...new Set(words)].slice(0, 30);
  };

  // ---------------------------------------------------------------------------
  // Find/Create Recruiter's Company
  // ---------------------------------------------------------------------------

  const getRecruiterCompanyId = async () => {
    /*
     * The Gateway requires company_id when creating a job.
     *
     * First try to retrieve an existing company.
     * If there is no company available, create the recruiter's company.
     */

    const companyResponse = await CompanyService.getCompanies();

    const companies =
      companyResponse?.companies ||
      companyResponse?.data?.companies ||
      companyResponse?.data ||
      [];

    if (Array.isArray(companies) && companies.length > 0) {
      const firstCompany = companies[0];

      return (
        firstCompany.id ||
        firstCompany.company_id ||
        firstCompany.companyId
      );
    }

    // -----------------------------------------------------------------------
    // No company exists for the recruiter.
    // Create the company through Gateway.
    // -----------------------------------------------------------------------

    const companyName = 'SwipeX Recruiter Company';

    const slug = `${companyName
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/^-|-$/g, '')}-${Date.now()}`;

    const companyPayload = {
      name: companyName,
      slug,
      company_type: 'Startup',
      is_newly_founded: false,
      industry: 'Technology',
      headquarters: location || 'India',
      funding_stage: 'Growth',
      description:
        'Company profile created through the SwipeX recruiter job posting workflow.',
      founded_year: new Date().getFullYear(),
      employee_count_range: '1-50'
    };

    const createdCompany = await CompanyService.createCompany(
      companyPayload
    );

    const company =
      createdCompany?.company ||
      createdCompany?.data?.company ||
      createdCompany?.data ||
      createdCompany;

    const companyId =
      company?.id ||
      company?.company_id ||
      company?.companyId;

    if (!companyId) {
      throw new Error(
        'Company was created, but the Gateway did not return a company ID.'
      );
    }

    return companyId;
  };

  // ---------------------------------------------------------------------------
  // Publish Job
  // ---------------------------------------------------------------------------

  const handlePublishJob = async (e) => {
    e.preventDefault();

    setErrorMessage(null);

    // Basic validation
    if (!jobTitle.trim()) {
      setErrorMessage('Please enter a job title.');
      return;
    }

    if (!location.trim()) {
      setErrorMessage('Please enter a job location.');
      return;
    }

    if (!description.trim()) {
      setErrorMessage('Please enter the job description.');
      return;
    }

    if (requiredSkills.length === 0) {
      setErrorMessage('Please add at least one required skill.');
      return;
    }

    const minimumSalary = parseSalary(salaryMin);
    const maximumSalary = parseSalary(salaryMax);

    if (
      minimumSalary !== null &&
      maximumSalary !== null &&
      minimumSalary > maximumSalary
    ) {
      setErrorMessage(
        'Minimum salary cannot be greater than maximum salary.'
      );
      return;
    }

    setIsPublishing(true);

    try {
      // ---------------------------------------------------------------------
      // 1. Get the canonical company ID from Gateway.
      // ---------------------------------------------------------------------

      const companyId = await getRecruiterCompanyId();

      // ---------------------------------------------------------------------
      // 2. Build the Gateway Job payload.
      //
      // Gateway will create the corresponding canonical Job Data record.
      // ---------------------------------------------------------------------

      const jobPayload = {
        company_id: companyId,

        title: jobTitle.trim(),

        description: description.trim(),

        location: location.trim(),

        job_type: mapRoleTypeToBackend(roleType),

        experience_level: 'fresher',

        salary_min: minimumSalary,

        salary_max: maximumSalary,

        salary_currency: 'INR',

        skills_required: requiredSkills,

        fresher_friendly:
          category === 'Fresher Friendly' ||
          category === 'Startups' ||
          roleType === 'Internship',

        low_competition:
          category === 'Low Competition',

        applicant_count: 0,

        is_active: true
      };

      // ---------------------------------------------------------------------
      // 3. Create job through Gateway.
      //
      // IMPORTANT:
      // Frontend does NOT directly create a Job Data record.
      //
      // Flow:
      //
      // Frontend
      //    ↓
      // Gateway POST /jobs
      //    ↓
      // Job Data POST /jobs
      // ---------------------------------------------------------------------

      const createdJob = await JobService.createJob(jobPayload);

      // ---------------------------------------------------------------------
      // 4. Confirm that Gateway returned a real job.
      // ---------------------------------------------------------------------

      const createdJobData =
        createdJob?.job ||
        createdJob?.data ||
        createdJob;

      const createdJobId =
        createdJobData?.id ||
        createdJobData?.job_id ||
        createdJobData?.jobId;

      if (!createdJobId) {
        throw new Error(
          'The job request completed, but the Gateway did not return a job ID.'
        );
      }

      // ---------------------------------------------------------------------
      // 5. Success.
      // ---------------------------------------------------------------------

      showToast('Job published successfully.');

      // Navigate only after backend confirms creation.
      setTimeout(() => {
        navigate('/candidate-review', {
          state: {
            role: jobTitle,
            jobId: createdJobId
          }
        });
      }, 1000);

    } catch (error) {
      console.error('Failed to publish job:', error);

      let message =
        'Unable to publish the job. Please make sure the Gateway and Job Data services are running.';

      if (error?.message) {
        message = error.message;
      }

      setErrorMessage(message);
    } finally {
      setIsPublishing(false);
    }
  };

  // ---------------------------------------------------------------------------
  // JSX
  // ---------------------------------------------------------------------------

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex font-sans selection:bg-purple-500 selection:text-white">

      {/* Toast Alert */}
      {toastMessage && (
        <div className="fixed top-6 right-6 z-50 bg-slate-900 text-white px-4 py-2.5 rounded-2xl shadow-xl text-xs font-bold flex items-center gap-2 animate-bounce">
          <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          {toastMessage}
        </div>
      )}

      {/* Error Alert */}
      {errorMessage && (
        <div className="fixed top-6 right-6 z-50 max-w-md bg-rose-50 border border-rose-200 text-rose-700 px-4 py-3 rounded-2xl shadow-xl text-xs font-bold flex items-start gap-2">
          <AlertCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />

          <div className="flex-1">
            <p>{errorMessage}</p>
          </div>

          <button
            type="button"
            onClick={() => setErrorMessage(null)}
            className="text-rose-400 hover:text-rose-700"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* ------------------------------------------------------------------ */}
      {/* RECRUITER SIDEBAR */}
      {/* ------------------------------------------------------------------ */}

      <aside
        className={`
          fixed lg:static inset-y-0 left-0 z-50 w-64
          bg-slate-900 text-white p-5 flex flex-col justify-between
          transition-transform duration-300
          ${
            isMobileMenuOpen
              ? 'translate-x-0 shadow-2xl'
              : '-translate-x-full lg:translate-x-0'
          }
        `}
      >
        <div className="space-y-6">

          <div className="flex justify-between items-center pb-4 border-b border-slate-800">

            <div
              className="flex items-center gap-2.5 cursor-pointer"
              onClick={() => navigate('/')}
            >
              <div className="w-9 h-9 rounded-xl bg-purple-600 flex items-center justify-center shadow-md shadow-purple-600/20">
                <Zap className="w-5 h-5 text-white fill-white" />
              </div>

              <span className="text-xl font-black tracking-tight text-white">
                Swipe<span className="text-purple-400">X</span>

                <span className="text-[10px] font-bold text-slate-400 block uppercase tracking-wider">
                  Recruiter
                </span>
              </span>
            </div>

            <button
              onClick={() => setIsMobileMenuOpen(false)}
              className="lg:hidden p-1 text-slate-400"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          <nav className="space-y-1.5 text-xs font-bold">

            <button
              onClick={() => {
                navigate('/recruiter-dashboard');
                setIsMobileMenuOpen(false);
              }}
              className="w-full py-2.5 px-3 text-slate-400 hover:bg-slate-800 hover:text-white rounded-xl flex items-center gap-3 transition"
            >
              <Building2 className="w-4 h-4" />
              <span>Overview Dashboard</span>
            </button>

            <button
              onClick={() => {
                navigate('/post-job');
                setIsMobileMenuOpen(false);
              }}
              className="w-full py-2.5 px-3 bg-purple-600 text-white rounded-xl flex items-center gap-3 shadow-2xs"
            >
              <PlusCircle className="w-4 h-4" />
              <span>Job Posting Wizard</span>
            </button>

            <button
              onClick={() => {
                navigate('/ats-ranker');
                setIsMobileMenuOpen(false);
              }}
              className="w-full py-2.5 px-3 text-slate-400 hover:bg-slate-800 hover:text-white rounded-xl flex items-center gap-3 transition"
            >
              <CheckSquare className="w-4 h-4" />
              <span>Applicant ATS Ranker</span>
            </button>

            <button
              onClick={() => {
                navigate('/candidate-review');
                setIsMobileMenuOpen(false);
              }}
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
            <LogOut className="w-3.5 h-3.5" />
            Sign Out
          </button>

        </div>
      </aside>

      {/* Mobile Backdrop */}
      {isMobileMenuOpen && (
        <div
          className="fixed inset-0 bg-slate-950/50 backdrop-blur-xs z-40 lg:hidden"
          onClick={() => setIsMobileMenuOpen(false)}
        />
      )}

      {/* ------------------------------------------------------------------ */}
      {/* MAIN WORKSPACE */}
      {/* ------------------------------------------------------------------ */}

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

            <h1 className="text-lg font-black text-slate-900 tracking-tight hidden sm:block">
              Job Posting & Lifecycle Wizard
            </h1>

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
                onClick={() =>
                  setIsProfileDropdownOpen(!isProfileDropdownOpen)
                }
                className="w-8 h-8 rounded-xl bg-purple-100 border border-purple-300 text-purple-700 font-bold text-xs flex items-center justify-center cursor-pointer hover:bg-purple-200 transition"
              >
                HR
              </div>

              {isProfileDropdownOpen && (
                <div className="absolute right-0 mt-2 w-48 bg-white border border-slate-200 rounded-2xl shadow-xl p-1.5 z-50 text-xs font-bold space-y-0.5">

                  <div className="px-3 py-2 border-b border-slate-100 mb-1">

                    <p className="text-slate-900 font-black">
                      Recruiter
                    </p>

                    <p className="text-[10px] text-slate-400 font-medium">
                      Authenticated SwipeX account
                    </p>

                  </div>

                  <button
                    onClick={() => navigate('/login')}
                    className="w-full py-2 px-3 hover:bg-rose-50 text-rose-600 rounded-xl flex items-center gap-2 transition"
                  >
                    <LogOut className="w-3.5 h-3.5" />
                    Logout
                  </button>

                </div>
              )}

            </div>
          </div>

        </header>

        {/* ---------------------------------------------------------------- */}
        {/* FORM WORKSPACE */}
        {/* ---------------------------------------------------------------- */}

        <main className="flex-grow p-6 max-w-6xl mx-auto w-full grid grid-cols-1 lg:grid-cols-3 gap-6">

          {/* LEFT: FORM */}
          <div className="lg:col-span-2 bg-white border border-slate-200 rounded-3xl p-6 shadow-2xs space-y-5">

            <div>

              <h2 className="text-xl font-black text-slate-900">
                Create New Job Listing
              </h2>

              <p className="text-xs text-slate-500 font-medium mt-0.5">
                Define role requirements to match candidates in the Swipe discovery engine.
              </p>

            </div>

            <form
              onSubmit={handlePublishJob}
              className="space-y-4 text-xs font-bold text-slate-700"
            >

              {/* Job Title */}
              <div>

                <label className="block text-[10px] uppercase text-slate-400 mb-1">
                  Job Title *
                </label>

                <input
                  type="text"
                  required
                  placeholder="e.g. Full Stack Engineer"
                  value={jobTitle}
                  onChange={(e) => setJobTitle(e.target.value)}
                  className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl font-medium focus:outline-none focus:border-purple-600 transition"
                />

              </div>

              {/* Category & Role Type */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">

                <div>

                  <label className="block text-[10px] uppercase text-slate-400 mb-1">
                    Company Category
                  </label>

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

                  <label className="block text-[10px] uppercase text-slate-400 mb-1">
                    Role Type
                  </label>

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

              {/* Location & Salary */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">

                <div>

                  <label className="block text-[10px] uppercase text-slate-400 mb-1">
                    Location *
                  </label>

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

                  <label className="block text-[10px] uppercase text-slate-400 mb-1">
                    Salary Range
                  </label>

                  <div className="flex gap-2">

                    <input
                      type="text"
                      placeholder="Min (₹)"
                      value={salaryMin}
                      onChange={(e) => setSalaryMin(e.target.value)}
                      className="w-1/2 px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl font-medium focus:outline-none focus:border-purple-600 transition"
                    />

                    <input
                      type="text"
                      placeholder="Max (₹)"
                      value={salaryMax}
                      onChange={(e) => setSalaryMax(e.target.value)}
                      className="w-1/2 px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl font-medium focus:outline-none focus:border-purple-600 transition"
                    />

                  </div>

                </div>

              </div>

              {/* Required Skills */}
              <div>

                <label className="block text-[10px] uppercase text-slate-400 mb-1">
                  ATS Required Skills
                </label>

                <div className="flex flex-wrap gap-1.5 mb-2">

                  {requiredSkills.map((skill, index) => (
                    <span
                      key={`${skill}-${index}`}
                      className="text-xs font-bold bg-purple-50 text-purple-700 border border-purple-200 px-3 py-1 rounded-xl flex items-center gap-1.5"
                    >
                      {skill}

                      <button
                        type="button"
                        onClick={() => handleRemoveSkill(skill)}
                        className="text-purple-400 hover:text-purple-900 cursor-pointer"
                      >
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
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') {
                        handleAddSkill(e);
                      }
                    }}
                    className="flex-grow px-3.5 py-2 bg-slate-50 border border-slate-200 rounded-xl font-medium focus:outline-none focus:border-purple-600"
                  />

                  <button
                    type="button"
                    onClick={handleAddSkill}
                    className="px-3.5 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold rounded-xl flex items-center gap-1 cursor-pointer"
                  >
                    <Plus className="w-3.5 h-3.5" />
                    Add
                  </button>

                </div>

              </div>

              {/* Description */}
              <div>

                <label className="block text-[10px] uppercase text-slate-400 mb-1">
                  Job Summary & Responsibilities *
                </label>

                <textarea
                  rows="5"
                  required
                  placeholder="Describe core project responsibilities and requirements..."
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl font-medium text-slate-800 focus:outline-none focus:border-purple-600 transition"
                />

              </div>

              {/* Publish */}
              <button
                type="submit"
                disabled={isPublishing}
                className={`
                  w-full py-3 text-white font-bold text-xs rounded-xl
                  shadow-md shadow-purple-600/20 transition
                  flex items-center justify-center gap-2
                  ${
                    isPublishing
                      ? 'bg-purple-400 cursor-not-allowed'
                      : 'bg-purple-600 hover:bg-purple-700 cursor-pointer'
                  }
                `}
              >

                {isPublishing ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Publishing Job...
                  </>
                ) : (
                  <>
                    <span>Publish Job & Inspect Candidates</span>
                    <ArrowRight className="w-4 h-4" />
                  </>
                )}

              </button>

            </form>
          </div>

          {/* ---------------------------------------------------------------- */}
          {/* RIGHT: LIVE PREVIEW */}
          {/* ---------------------------------------------------------------- */}

          <div className="space-y-4">

            <h3 className="text-xs font-black text-slate-900 uppercase tracking-wider flex items-center gap-1.5">
              <Eye className="w-4 h-4 text-purple-600" />
              Candidate Card Preview
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
                    {jobTitle || 'Job Title Preview'}
                  </h4>

                  <p className="text-xs font-semibold text-slate-500 flex items-center gap-1 mt-0.5">
                    <Building2 className="w-3.5 h-3.5 text-slate-400" />
                    Recruiter Company
                  </p>

                </div>

                <div className="bg-purple-600 text-white text-xs font-black px-2.5 py-1 rounded-xl flex items-center gap-1">
                  <Sparkles className="w-3 h-3" />
                  AI Match
                </div>

              </div>

              <div className="grid grid-cols-2 gap-2 py-2 border-y border-slate-100 text-[11px] text-slate-600 font-medium">

                <div className="flex items-center gap-1 truncate">
                  <MapPin className="w-3.5 h-3.5 text-purple-600" />
                  {location || 'Location'}
                </div>

                <div className="flex items-center gap-1 truncate">
                  <DollarSign className="w-3.5 h-3.5 text-emerald-600" />

                  {salaryMin && salaryMax
                    ? `₹${salaryMin} - ₹${salaryMax}`
                    : 'Salary Range'}
                </div>

              </div>

              <div className="flex flex-wrap gap-1">

                {requiredSkills.map((skill, index) => (
                  <span
                    key={`${skill}-${index}`}
                    className="text-[10px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200 px-2 py-0.5 rounded-md"
                  >
                    {skill}
                  </span>
                ))}

              </div>

              <p className="text-xs text-slate-500 line-clamp-3">
                {description ||
                  'Job description overview will appear here as you type in the form.'}
              </p>

            </div>

            {/* Integration Information */}
            <div className="bg-purple-50 border border-purple-100 rounded-2xl p-4">

              <div className="flex items-start gap-2">

                <Briefcase className="w-4 h-4 text-purple-600 mt-0.5 flex-shrink-0" />

                <div>

                  <p className="text-xs font-black text-purple-900">
                    Integrated Job Pipeline
                  </p>

                  <p className="text-[10px] text-purple-700 font-medium mt-1 leading-relaxed">
                    Publishing sends this job through the Gateway and
                    synchronizes it with the Job Data service for
                    recommendations and ATS processing.
                  </p>

                </div>

              </div>

            </div>

          </div>

        </main>
      </div>
    </div>
  );
}