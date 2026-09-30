/**
 * SwipeX Central API Client & Gateway Service
 *
 * Frontend communicates ONLY with the API Gateway.
 *
 * Flow:
 * Frontend :5173
 *     ↓
 * Gateway :8000
 *     ↓
 * ┌───────────────┐
 * │               │
 * ▼               ▼
 * Job Data :8004  AIML :8002
 *
 * IMPORTANT:
 * - No mock/fallback data
 * - No direct frontend calls to AIML or Job Data
 * - Authentication token uses "access_token" consistently
 */

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

/**
 * Get the currently stored authentication token.
 *
 * "access_token" is the canonical key used by axiosClient.js
 * and by the Gateway authentication flow.
 */
const getAuthToken = () => {
  return localStorage.getItem('access_token');
};

/**
 * Common API request helper.
 */
async function request(endpoint, options = {}) {
  const token = getAuthToken();

  const headers = {
    ...(token && { Authorization: `Bearer ${token}` }),
    ...options.headers,
  };

  /**
   * Only add JSON Content-Type when a body is actually JSON.
   * This is important for multipart/form-data uploads because
   * the browser must set the multipart boundary automatically.
   */
  if (
    options.body &&
    typeof options.body === 'string' &&
    !headers['Content-Type']
  ) {
    headers['Content-Type'] = 'application/json';
  }

  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));

      const message =
        errorData?.detail ||
        errorData?.message ||
        `API Error: ${response.status}`;

      throw new Error(message);
    }

    if (response.status === 204) {
      return true;
    }

    const contentType = response.headers.get('content-type') || '';

    if (contentType.includes('application/json')) {
      return await response.json();
    }

    return await response.text();
  } catch (error) {
    console.warn(
      `[SwipeX API Error] ${endpoint}:`,
      error?.message || error
    );

    throw error;
  }
}

/* ==========================================================================
   1. AUTH SERVICE
   ========================================================================== */

export const login = async (email, password) => {
  const params = new URLSearchParams();

  params.append('username', email);
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

    throw new Error(
      errorData?.detail ||
        errorData?.message ||
        `Login failed with status ${response.status}`
    );
  }

  const data = await response.json();

  if (data?.access_token) {
    localStorage.setItem('access_token', data.access_token);
  }

  /**
   * Store user ID only when Gateway provides it.
   * This is useful for UI state but is NOT required for
   * authenticated Gateway requests.
   */
  if (data?.user?.id) {
    localStorage.setItem('swipex_user_id', String(data.user.id));
  } else if (data?.user_id) {
    localStorage.setItem('swipex_user_id', String(data.user_id));
  }

  return data;
};

export const register = async (userData) => {
  const payload = {
    email: userData.email,
    password: userData.password,

    full_name:
      userData.fullName ||
      userData.full_name ||
      userData.name ||
      '',

    role:
      userData.role === 'candidate'
        ? 'job_seeker'
        : userData.role || 'job_seeker',

    skills: Array.isArray(userData.skills)
      ? userData.skills
      : String(userData.skills || '')
          .split(',')
          .map((skill) => skill.trim())
          .filter(Boolean),
  };

  return request('/auth/register', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
};

export const logout = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('swipex_auth_token');
  localStorage.removeItem('swipex_user_id');
};

export const getCurrentUser = () => request('/auth/me');

export const AuthService = {
  login,
  register,
  logout,
  getCurrentUser,
};

/* ==========================================================================
   2. JOB SERVICE
   ========================================================================== */

export const searchJobs = (filters = {}) => {
  const params = new URLSearchParams();

  if (filters.q) {
    params.append('keyword', filters.q);
  }

  if (filters.location) {
    params.append('location', filters.location);
  }

  if (filters.skills) {
    params.append(
      'skills',
      Array.isArray(filters.skills)
        ? filters.skills.join(',')
        : filters.skills
    );
  }

  if (filters.type) {
    params.append('job_type', filters.type);
  }

  const query = params.toString();

  return request(`/jobs/search${query ? `?${query}` : ''}`);
};

export const getJobs = (
  page = 1,
  pageSize = 20,
  filters = {}
) => {
  const params = new URLSearchParams({
    page: String(page),
    page_size: String(pageSize),
  });

  if (filters.type) {
    params.append('job_type', filters.type);
  }

  if (filters.location) {
    params.append('location', filters.location);
  }

  return request(`/jobs?${params.toString()}`);
};

export const getJobById = (jobId) => {
  if (!jobId) {
    throw new Error('Job ID is required.');
  }

  return request(`/jobs/${encodeURIComponent(jobId)}`);
};

export const JobService = {
  getJobs,
  searchJobs,
  getJobById,
};

/* ==========================================================================
   3. RESUME SERVICE
   ========================================================================== */

export const getResumes = async () => {
  const response = await request('/resumes');

  return response?.resumes || response || [];
};

export const uploadResume = async (formData) => {
  if (!(formData instanceof FormData)) {
    throw new Error('uploadResume requires a FormData object.');
  }

  const token = getAuthToken();

  const headers = {
    ...(token && {
      Authorization: `Bearer ${token}`,
    }),
  };

  /**
   * DO NOT manually set Content-Type here.
   * Browser fetch automatically adds:
   * multipart/form-data; boundary=...
   */
  const response = await fetch(
    `${API_BASE_URL}/resumes/upload`,
    {
      method: 'POST',
      headers,
      body: formData,
    }
  );

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));

    throw new Error(
      errorData?.detail ||
        errorData?.message ||
        `Upload failed with status ${response.status}`
    );
  }

  const data = await response.json();

  return data?.resume || data;
};

export const setActiveVersion = (resumeId) => {
  if (!resumeId) {
    throw new Error('Resume ID is required.');
  }

  return request(
    `/resumes/${encodeURIComponent(resumeId)}/activate`,
    {
      method: 'PATCH',
    }
  );
};

export const deleteResume = (resumeId) => {
  if (!resumeId) {
    throw new Error('Resume ID is required.');
  }

  return request(
    `/resumes/${encodeURIComponent(resumeId)}`,
    {
      method: 'DELETE',
    }
  );
};

export const ResumeService = {
  getResumes,
  uploadResume,
  setActiveVersion,
  deleteResume,
};

/* ==========================================================================
   4. ATS SERVICE
   ========================================================================== */

export const getAtsScore = (resumeId, jobId) => {
  if (!resumeId || !jobId) {
    throw new Error('Both resume ID and job ID are required.');
  }

  return request('/ats/score', {
    method: 'POST',
    body: JSON.stringify({
      resume_id: String(resumeId),
      job_id: String(jobId),
    }),
  });
};

export const getAtsSuggestions = (resumeId, jobId) => {
  if (!resumeId || !jobId) {
    throw new Error('Both resume ID and job ID are required.');
  }

  return request('/ats/suggestions', {
    method: 'POST',
    body: JSON.stringify({
      resume_id: String(resumeId),
      job_id: String(jobId),
    }),
  });
};

export const AtsService = {
  getAtsScore,
  getAtsSuggestions,
};

/* ==========================================================================
   5. RECOMMENDATION SERVICE
   ========================================================================== */

/**
 * Main recommendation endpoint.
 *
 * IMPORTANT:
 * The Gateway gets the authenticated user from the JWT.
 * Therefore the frontend does NOT need to send user_id here.
 *
 * Gateway:
 *   GET /recommendations
 *
 * Gateway internally calls:
 *   AIML :8002
 *
 * AIML internally uses:
 *   Job Data :8004
 */
export const getUpgradedRecommendations = async (limit = 10) => {
  const safeLimit = Math.max(1, Number(limit) || 10);

  const response = await request(
    `/recommendations?limit=${safeLimit}`
  );

  const recommendations = Array.isArray(
    response?.recommendations
  )
    ? response.recommendations
    : [];

  return {
    ...response,

    recommendations: recommendations.map((item) => {
      const job = item?.job || item;

      return {
        ...job,

        /**
         * Preserve recommendation-level AI information.
         */
        match_score: item?.match_score ?? null,
        semantic_match_score:
          item?.semantic_match_score ?? null,
        recommendation_tags:
          item?.recommendation_tags || [],
        match_reasons:
          item?.match_reasons || [],
      };
    }),
  };
};

/**
 * Backward-compatible personalized recommendation function.
 *
 * The authenticated Gateway should be the source of user identity.
 * userId is therefore optional and is only sent when explicitly
 * supplied by an existing frontend caller.
 */
export const getPersonalizedRecommendations = (
  userId,
  limit = 50,
  filters = {}
) => {
  const params = new URLSearchParams();

  params.append('limit', String(limit));

  if (userId) {
    params.append('user_id', String(userId));
  }

  if (filters.workplaceType) {
    params.append(
      'workplace_type',
      filters.workplaceType
    );
  }

  if (filters.hybrid) {
    params.append('hybrid', 'true');
  }

  return request(`/recommendations?${params.toString()}`);
};

export const getMatchBreakdown = (jobId, userId = null) => {
  if (!jobId) {
    throw new Error('Job ID is required.');
  }

  const params = new URLSearchParams();

  params.append('job_id', String(jobId));

  if (userId) {
    params.append('user_id', String(userId));
  }

  return request(
    `/recommendations/breakdown?${params.toString()}`
  );
};

export const RecommendationService = {
  getUpgradedRecommendations,
  getPersonalizedRecommendations,
  getMatchBreakdown,
};

/* ==========================================================================
   6. SWIPE SERVICE
   ========================================================================== */

/**
 * Record a candidate swipe through the Gateway.
 *
 * IMPORTANT:
 * jobId must be the Gateway Job UUID.
 *
 * Do NOT convert the Gateway UUID to an integer.
 * Gateway handles the UUID → Job Data integer mapping internally.
 */
export const recordCandidateSwipe = (
  userId,
  jobId,
  action = 'like'
) => {
  if (!jobId) {
    throw new Error('Job ID is required to record a swipe.');
  }

  let normalizedAction = action;

  /**
   * Existing frontend terminology:
   *   like → apply
   *
   * Job Data/Gateway interaction terminology:
   *   apply
   *   save
   *   skip
   */
  if (action === 'like') {
    normalizedAction = 'apply';
  }

  return request('/swipes', {
    method: 'POST',
    body: JSON.stringify({
      job_id: String(jobId),
      action: normalizedAction,
    }),
  });
};

export const recordSwipe = (
  jobId,
  direction,
  actionType = 'apply',
  notes = ''
) => {
  return recordCandidateSwipe(
    null,
    jobId,
    actionType
  );
};

export const getSwipeHistory = () =>
  request('/swipes/history');

export const undoSwipe = (jobId) => {
  if (!jobId) {
    throw new Error('Job ID is required.');
  }

  return request(
    `/swipes/${encodeURIComponent(jobId)}`,
    {
      method: 'DELETE',
    }
  );
};

export const SwipeService = {
  recordCandidateSwipe,
  recordSwipe,
  getSwipeHistory,
  undoSwipe,
};

/* ==========================================================================
   7. COMPANY SERVICE
   ========================================================================== */

export const getCompanies = (params = {}) => {
  const query = new URLSearchParams(params).toString();

  return request(
    `/companies${query ? `?${query}` : ''}`
  );
};

export const getCompanyById = (id) => {
  if (!id) {
    throw new Error('Company ID is required.');
  }

  return request(
    `/companies/${encodeURIComponent(id)}`
  );
};

export const CompanyService = {
  getCompanies,
  getCompanyById,
};

/* ==========================================================================
   8. SAVED JOB SERVICE
   ========================================================================== */

export const saveJob = (jobId, notes = '') => {
  if (!jobId) {
    throw new Error('Job ID is required.');
  }

  return request('/saved-jobs', {
    method: 'POST',
    body: JSON.stringify({
      job_id: String(jobId),
      notes,
    }),
  });
};

export const getSavedJobs = () =>
  request('/saved-jobs');

export const unsaveJob = (jobId) => {
  if (!jobId) {
    throw new Error('Job ID is required.');
  }

  return request(
    `/saved-jobs/${encodeURIComponent(jobId)}`,
    {
      method: 'DELETE',
    }
  );
};

export const removeSavedJob = unsaveJob;

export const SavedJobService = {
  saveJob,
  getSavedJobs,
  unsaveJob,
  removeSavedJob,
};

/* ==========================================================================
   DEFAULT EXPORT
   ========================================================================== */

export default {
  AuthService,
  JobService,
  ResumeService,
  AtsService,
  RecommendationService,
  SwipeService,
  CompanyService,
  SavedJobService,

  login,
  register,
  logout,
  getCurrentUser,

  searchJobs,
  getJobs,
  getJobById,

  getResumes,
  uploadResume,
  setActiveVersion,
  deleteResume,

  getAtsScore,
  getAtsSuggestions,

  getUpgradedRecommendations,
  getPersonalizedRecommendations,
  getMatchBreakdown,

  recordCandidateSwipe,
  recordSwipe,
  getSwipeHistory,
  undoSwipe,

  getCompanies,
  getCompanyById,

  saveJob,
  getSavedJobs,
  unsaveJob,
  removeSavedJob,
};      