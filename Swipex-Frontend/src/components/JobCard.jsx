import React from 'react';
import { MapPin, Briefcase, IndianRupee, Sparkles, Building } from 'lucide-react';

const JobCard = ({ job }) => {
  return (
    <div className="w-full max-w-sm h-[520px] bg-white rounded-3xl shadow-xl border border-gray-100 p-6 flex flex-col justify-between select-none relative overflow-hidden pointer-events-none">
      {/* Top Banner Badges */}
      <div className="flex flex-wrap gap-2 mb-3">
        {job.fresher_friendly && (
          <span className="bg-emerald-50 text-emerald-700 border border-emerald-200 text-xs font-semibold px-2.5 py-1 rounded-full flex items-center gap-1">
            <Sparkles className="w-3 h-3" /> Fresher Friendly
          </span>
        )}
        {job.low_competition && (
          <span className="bg-amber-50 text-amber-700 border border-amber-200 text-xs font-semibold px-2.5 py-1 rounded-full">
            🔥 Low Competition ({job.applicant_count || 0} applicants)
          </span>
        )}
      </div>

      {/* Main Details */}
      <div>
        <div className="flex items-center gap-4 mb-4">
          {job.logo_url ? (
            <img src={job.logo_url} alt={job.company_name} className="w-14 h-14 rounded-2xl object-cover border" />
          ) : (
            <div className="w-14 h-14 rounded-2xl bg-indigo-50 text-indigo-600 flex items-center justify-center font-bold text-xl border border-indigo-100">
              <Building className="w-7 h-7" />
            </div>
          )}
          <div>
            <h3 className="font-bold text-xl text-gray-900 leading-tight">{job.title}</h3>
            <p className="text-gray-500 font-medium text-sm">{job.company_name}</p>
          </div>
        </div>

        {/* Info Grid */}
        <div className="grid grid-cols-2 gap-2 mb-4 text-xs font-medium text-gray-600">
          <div className="flex items-center gap-1.5 bg-gray-50 p-2.5 rounded-xl">
            <MapPin className="w-4 h-4 text-gray-400" />
            <span className="truncate">{job.location || 'Remote'}</span>
          </div>
          <div className="flex items-center gap-1.5 bg-gray-50 p-2.5 rounded-xl">
            <Briefcase className="w-4 h-4 text-gray-400" />
            <span className="capitalize">{job.job_type || 'Full Time'}</span>
          </div>
          <div className="col-span-2 flex items-center gap-1.5 bg-indigo-50/50 text-indigo-900 p-2.5 rounded-xl font-semibold">
            <IndianRupee className="w-4 h-4 text-indigo-600" />
            <span>₹{job.salary_min} - ₹{job.salary_max} PA</span>
          </div>
        </div>

        {/* Description */}
        <p className="text-gray-600 text-sm line-clamp-3 mb-4 leading-relaxed">
          {job.description}
        </p>
      </div>

      {/* Required Skills Chips */}
      <div className="mt-auto">
        <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Required Skills</p>
        <div className="flex flex-wrap gap-1.5">
          {job.skills_required?.map((skill, idx) => (
            <span key={idx} className="bg-gray-100 text-gray-700 text-xs px-2.5 py-1 rounded-lg font-medium">
              {skill}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
};

export default JobCard;