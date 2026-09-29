/**
 * SwipeX Central API Client & Gateway Service
 * Aligned with Live API Gateway Specs & Intern 4 AI Scoring Models
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

async function request(endpoint, options = {}) {
  const token = localStorage.getItem('swipex_auth_token');
  
  // Do not override Content-Type if headers explicitly set it (e.g. form-urlencoded)
  const headers = {
    'Content-Type': 'application/json',
    ...(token && { Authorization: `Bearer ${token}` }),
    ...options.headers,
  };

  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `API Error: ${response.status}`);
    }

    if (response.status === 204) return true;

    return await response.json();
  } catch (error) {
    console.warn(`[API Gateway Network Notice] ${endpoint}:`, error.message);
    throw error;
  }
}

// 1. AUTH SERVICE EXPORTS
export const login = async (email, password) => {
  const params = new URLSearchParams();
  params.append('username', email); // FastAPI OAuth2 Password flow expects 'username'
  params.append('password', password);

  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: params.toString(),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Login failed with status ${response.status}`);
  }

  const data = await response.json();
  if (data.access_token) {
    localStorage.setItem('swipex_auth_token', data.access_token);
  }
  return data;
};

export const register = async (userData) => {
  // Map frontend payload fields to backend Pydantic schema
  const payload = {
    email: userData.email,
    password: userData.password,
    full_name: userData.fullName || userData.full_name || userData.name || '',
    role: userData.role === 'candidate' ? 'job_seeker' : (userData.role || 'job_seeker'),
    skills: Array.isArray(userData.skills)
      ? userData.skills
      : (userData.skills || '').split(',').map((s) => s.trim()).filter(Boolean),
  };

  return request('/auth/register', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
};

export const logout = () => {
  localStorage.removeItem('swipex_auth_token');
};

export const getCurrentUser = () => request('/auth/me');

export const AuthService = { 
  login,
  register,
  logout,
  getCurrentUser 
};

// 2. JOB SERVICE EXPORTS
export const searchJobs = (filters = {}) => {
  const params = new URLSearchParams();
  if (filters.q) params.append('keyword', filters.q);
  if (filters.location) params.append('location', filters.location);
  if (filters.skills) params.append('skills', filters.skills);
  if (filters.type) params.append('job_type', filters.type);
  return request(`/jobs/search?${params.toString()}`);
};

export const getJobs = (page = 1, pageSize = 20, filters = {}) => {
  const params = new URLSearchParams({ page, page_size: pageSize });
  if (filters.type) params.append('job_type', filters.type);
  if (filters.location) params.append('location', filters.location);
  return request(`/jobs?${params.toString()}`);
};

export const getJobById = (jobId) => request(`/jobs/${jobId}`);

export const JobService = {
  getJobs,
  searchJobs,
  getJobById,
};

// 3. RESUME & ATS SCORING SERVICE EXPORTS
export const getResumes = async () => {
  const response = await request('/resumes');
  return response?.resumes || response || [];
};

export const uploadResume = async (formData) => {
  const token = localStorage.getItem('swipex_auth_token');
  const response = await fetch(`${API_BASE_URL}/resumes/upload`, {
    method: 'POST',
    headers: { ...(token && { Authorization: `Bearer ${token}` }) },
    body: formData,
  });
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Upload failed with status ${response.status}`);
  }
  const data = await response.json();
  return data?.resume || data;
};

export const setActiveVersion = (resumeId) => 
  request(`/resumes/${resumeId}/activate`, { method: 'PATCH' });

export const deleteResume = (resumeId) => 
  request(`/resumes/${resumeId}`, { method: 'DELETE' });

export const ResumeService = {
  getResumes,
  uploadResume,
  setActiveVersion,
  deleteResume,
};

export const getAtsScore = (resumeId, jobId) =>
  request('/ats/score', {
    method: 'POST',
    body: JSON.stringify({
      resume_id: String(resumeId),
      job_id: String(jobId),
    }),
  });

export const getAtsSuggestions = (resumeId, jobId) =>
  request('/ats/suggestions', {
    method: 'POST',
    body: JSON.stringify({
      resume_id: String(resumeId),
      job_id: String(jobId),
    }),
  });

export const AtsService = {
  getAtsScore,
  getAtsSuggestions,
};

// 4. RECOMMENDATION SERVICE EXPORTS
export const getUpgradedRecommendations = async (limit = 10) => {
  const response = await request(`/recommendations?limit=${limit}`);
  const recommendations = response?.recommendations || [];
  return {
    ...response,
    recommendations: recommendations.map((item) => ({
      ...(item.job || item),
      match_score: item.match_score,
      semantic_match_score: item.semantic_match_score,
      recommendation_tags: item.recommendation_tags,
    })),
  };
};

export const getPersonalizedRecommendations = (userId, limit = 50, filters = {}) => {
  const params = new URLSearchParams({ user_id: userId, limit });
  if (filters.workplaceType) params.append('workplace_type', filters.workplaceType);
  if (filters.hybrid) params.append('hybrid', 'true');
  return request(`/recommendations?${params.toString()}`);
};

export const getMatchBreakdown = (jobId, userId) => 
  request(`/recommendations/breakdown?job_id=${jobId}&user_id=${userId}`);

export const RecommendationService = {
  getUpgradedRecommendations,
  getPersonalizedRecommendations,
  getMatchBreakdown,
};

// 5. SWIPE SERVICE EXPORTS
export const recordCandidateSwipe = (userId, jobId, action = 'like') => 
  request('/swipes', {
    method: 'POST',
    body: JSON.stringify({
      job_id: String(jobId),
      action: action === 'like' ? 'apply' : action,
    }),
  });

export const recordSwipe = (jobId, direction, actionType = 'apply', notes = '') => 
  recordCandidateSwipe(null, jobId, actionType);

export const getSwipeHistory = () => request('/swipes');

export const undoSwipe = (jobId) => request(`/swipes/${jobId}`, { method: 'DELETE' });

export const SwipeService = {
  recordCandidateSwipe,
  recordSwipe,
  getSwipeHistory,
  undoSwipe,
};

// 6. COMPANY SERVICE EXPORTS
export const getCompanies = (params = {}) => {
  const query = new URLSearchParams(params).toString();
  return request(`/companies${query ? `?${query}` : ''}`);
};

export const getCompanyById = (id) => request(`/companies/${id}`);

export const CompanyService = {
  getCompanies,
  getCompanyById,
};

// 7. SAVED JOBS SERVICE EXPORTS
export const saveJob = (jobId, notes = '') =>
  request('/saved-jobs', {
    method: 'POST',
    body: JSON.stringify({ job_id: jobId, notes }),
  });

export const getSavedJobs = () => request('/saved-jobs');

export const unsaveJob = (jobId) => request(`/saved-jobs/${jobId}`, { method: 'DELETE' });
export const removeSavedJob = unsaveJob;

export const SavedJobService = {
  saveJob,
  getSavedJobs,
  unsaveJob,
  removeSavedJob,
};

// DEFAULT EXPORT
export default {
  AuthService,
  JobService,
  searchJobs,
  getJobs,
  getJobById,
  ResumeService,
  AtsService,
  RecommendationService,
  SwipeService,
  CompanyService,
  getCompanies,
  getCompanyById,
  SavedJobService,
};