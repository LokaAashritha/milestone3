import React, { useState, useEffect } from 'react';
import Navbar from '../components/Navbar';
import Sidebar from '../components/Sidebar';
import { 
  User, Mail, Briefcase, GraduationCap, MapPin, 
  Save, RefreshCw, CheckCircle2, Shield, Lock
} from 'lucide-react';
import { AuthService } from '../services/api';

export default function Profile() {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [successMessage, setSuccessMessage] = useState(null);

  const [formData, setFormData] = useState({
    full_name: 'Asha Candidate',
    email: 'asha@swipex.ai',
    title: 'Software Development Engineer (B.Tech CSM)',
    location: 'Bengaluru, India',
    bio: 'Passionate computer science engineer specializing in AI/ML solutions, Python backend architecture, and dynamic web applications.',
    preferred_role: 'Full Stack & Backend Developer',
    experience_level: 'Entry Level (Fresher / 2027 Grad)',
    github_url: 'https://github.com/ashacandidate',
    linkedin_url: 'https://linkedin.com/in/ashacandidate'
  });

  useEffect(() => {
    loadUserProfile();
  }, []);

  const loadUserProfile = async () => {
    setLoading(true);
    try {
      const user = await AuthService.getCurrentUser();
      if (user) {
        setFormData(prev => ({
          ...prev,
          full_name: user.full_name || user.name || prev.full_name,
          email: user.email || prev.email,
          title: user.title || prev.title,
          location: user.location || prev.location
        }));
      }
    } catch (err) {
      console.warn("Backend offline, using local profile state:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSaveProfile = async (e) => {
    e.preventDefault();
    setSaving(true);
    setSuccessMessage(null);

    try {
      // API call placeholder for profile update
      await new Promise(resolve => setTimeout(resolve, 600));
      setSuccessMessage("Profile preferences updated successfully!");
    } catch (err) {
      console.warn("Save profile notice:", err);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col font-sans">
      <Navbar />

      <div className="flex flex-1">
        <Sidebar />

        <main className="flex-1 p-8 max-w-5xl space-y-8">
          {/* Header */}
          <div>
            <h1 className="text-2xl font-black text-slate-900 tracking-tight">Profile & Preferences</h1>
            <p className="text-xs text-slate-500 font-medium">Manage your personal information, career target roles, and profile settings</p>
          </div>

          {/* Alert Message */}
          {successMessage && (
            <div className="p-4 bg-purple-50 border border-purple-200 rounded-2xl flex items-center gap-3 text-xs font-bold text-purple-700">
              <CheckCircle2 className="w-5 h-5 flex-shrink-0 text-purple-600" />
              <span>{successMessage}</span>
            </div>
          )}

          {loading ? (
            <div className="text-center py-20 space-y-3">
              <RefreshCw className="w-8 h-8 text-purple-600 animate-spin mx-auto" />
              <p className="text-xs font-bold text-slate-400">Loading profile data...</p>
            </div>
          ) : (
            <form onSubmit={handleSaveProfile} className="space-y-6">
              
              {/* Account Identity Card */}
              <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm space-y-6">
                <div className="flex items-center gap-4">
                  <div className="w-16 h-16 rounded-2xl bg-purple-600 text-white font-black text-xl flex items-center justify-center shadow-md">
                    {formData.full_name.charAt(0)}
                  </div>
                  <div>
                    <h2 className="text-lg font-black text-slate-900">{formData.full_name}</h2>
                    <p className="text-xs font-bold text-purple-600">{formData.title}</p>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
                  <div className="space-y-1.5">
                    <label className="text-xs font-black text-slate-700 uppercase tracking-wider flex items-center gap-1.5">
                      <User className="w-3.5 h-3.5 text-purple-600" /> Full Name
                    </label>
                    <input 
                      type="text"
                      name="full_name"
                      value={formData.full_name}
                      onChange={handleInputChange}
                      className="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-2.5 text-xs font-bold text-slate-800 focus:outline-hidden focus:border-purple-600 transition"
                    />
                  </div>

                  <div className="space-y-1.5">
                    <label className="text-xs font-black text-slate-700 uppercase tracking-wider flex items-center gap-1.5">
                      <Mail className="w-3.5 h-3.5 text-purple-600" /> Email Address
                    </label>
                    <input 
                      type="email"
                      name="email"
                      value={formData.email}
                      onChange={handleInputChange}
                      className="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-2.5 text-xs font-bold text-slate-800 focus:outline-hidden focus:border-purple-600 transition"
                    />
                  </div>
                </div>
              </div>

              {/* Career Preferences */}
              <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm space-y-4">
                <h3 className="text-xs font-black text-slate-900 uppercase tracking-wider flex items-center gap-2">
                  <Briefcase className="w-4 h-4 text-purple-600" /> Career & Role Objectives
                </h3>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-1.5">
                    <label className="text-xs font-black text-slate-700 uppercase tracking-wider">Target Position Title</label>
                    <input 
                      type="text"
                      name="preferred_role"
                      value={formData.preferred_role}
                      onChange={handleInputChange}
                      className="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-2.5 text-xs font-bold text-slate-800 focus:outline-hidden focus:border-purple-600 transition"
                    />
                  </div>

                  <div className="space-y-1.5">
                    <label className="text-xs font-black text-slate-700 uppercase tracking-wider">Experience Level</label>
                    <input 
                      type="text"
                      name="experience_level"
                      value={formData.experience_level}
                      onChange={handleInputChange}
                      className="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-2.5 text-xs font-bold text-slate-800 focus:outline-hidden focus:border-purple-600 transition"
                    />
                  </div>

                  <div className="md:col-span-2 space-y-1.5">
                    <label className="text-xs font-black text-slate-700 uppercase tracking-wider">Professional Summary / Bio</label>
                    <textarea 
                      name="bio"
                      rows={3}
                      value={formData.bio}
                      onChange={handleInputChange}
                      className="w-full bg-slate-50 border border-slate-200 rounded-2xl p-4 text-xs font-bold text-slate-800 focus:outline-hidden focus:border-purple-600 transition"
                    />
                  </div>
                </div>
              </div>

              {/* Action Button */}
              <div className="flex justify-end">
                <button
                  type="submit"
                  disabled={saving}
                  className="px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-2xl text-xs font-bold flex items-center gap-2 shadow-sm transition cursor-pointer disabled:opacity-50"
                >
                  {saving ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
                  <span>Save Profile Preferences</span>
                </button>
              </div>

            </form>
          )}
        </main>
      </div>
    </div>
  );
}