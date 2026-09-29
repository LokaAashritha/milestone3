import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';

// Protected Route Guard
import ProtectedRoute from './components/ProtectedRoute';

// Public Pages
import Landing from './pages/Landing';
import Login from './pages/Login';
import Register from './pages/Register';

// Candidate Pages
import SwipeDiscovery from './pages/SwipeDiscovery';
import JobSearch from './pages/JobSearch';
import CompanyProfile from './pages/CompanyProfile';
import ResumeUpload from './pages/ResumeUpload';
import Dashboard from './pages/Dashboard';
import Analytics from './pages/Analytics';
import Profile from './pages/Profile';
import Notifications from './pages/Notifications';

// Recruiter Pages
import RecruiterDashboard from './pages/RecruiterDashboard';
import PostJob from './pages/PostJob';
import AtsRanker from './pages/AtsRanker';
import CandidateReview from './pages/CandidateReview';

// Admin Pages
import AdminDashboard from './pages/AdminDashboard';
import AdminUsers from './pages/AdminUsers';

export default function App() {
  return (
    <Router>
      <Routes>
        {/* Public Routes */}
        <Route path="/" element={<Landing />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        {/* Candidate Portal Routes (Protected) */}
        <Route path="/discovery" element={<ProtectedRoute allowedRoles={['candidate']}><SwipeDiscovery /></ProtectedRoute>} />
        <Route path="/job-search" element={<ProtectedRoute allowedRoles={['candidate']}><JobSearch /></ProtectedRoute>} />
        <Route path="/companies" element={<ProtectedRoute allowedRoles={['candidate']}><CompanyProfile /></ProtectedRoute>} />
        <Route path="/resume-upload" element={<ProtectedRoute allowedRoles={['candidate']}><ResumeUpload /></ProtectedRoute>} />
        <Route path="/dashboard" element={<ProtectedRoute allowedRoles={['candidate']}><Dashboard /></ProtectedRoute>} />
        <Route path="/analytics" element={<ProtectedRoute allowedRoles={['candidate']}><Analytics /></ProtectedRoute>} />
        <Route path="/profile" element={<ProtectedRoute allowedRoles={['candidate']}><Profile /></ProtectedRoute>} />
        <Route path="/notifications" element={<ProtectedRoute allowedRoles={['candidate']}><Notifications /></ProtectedRoute>} />

        {/* Recruiter Portal Routes (Protected) */}
        <Route path="/recruiter-dashboard" element={<ProtectedRoute allowedRoles={['recruiter']}><RecruiterDashboard /></ProtectedRoute>} />
        <Route path="/post-job" element={<ProtectedRoute allowedRoles={['recruiter']}><PostJob /></ProtectedRoute>} />
        <Route path="/ats-ranker" element={<ProtectedRoute allowedRoles={['recruiter', 'candidate']}><AtsRanker /></ProtectedRoute>} />
        <Route path="/candidate-review" element={<ProtectedRoute allowedRoles={['recruiter']}><CandidateReview /></ProtectedRoute>} />

        {/* Admin Portal Routes (Protected) */}
        <Route path="/admin-dashboard" element={<ProtectedRoute allowedRoles={['admin']}><AdminDashboard /></ProtectedRoute>} />
        <Route path="/admin-users" element={<ProtectedRoute allowedRoles={['admin']}><AdminUsers /></ProtectedRoute>} />

        {/* Catch-All Fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}

// import React from 'react';
// import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';

// // Public Pages
// import Landing from './pages/Landing';
// import Login from './pages/Login';
// import Register from './pages/Register';

// // Candidate Portal Pages
// import SwipeDiscovery from './pages/SwipeDiscovery';
// import JobSearch from './pages/JobSearch';
// import CompanyProfile from './pages/CompanyProfile';
// import ResumeUpload from './pages/ResumeUpload';
// import Dashboard from './pages/Dashboard';
// import Analytics from './pages/Analytics';
// import Profile from './pages/Profile';
// import Notifications from './pages/Notifications';

// // Recruiter Portal Pages
// import RecruiterDashboard from './pages/RecruiterDashboard';
// import PostJob from './pages/PostJob';
// import AtsRanker from './pages/AtsRanker';
// import CandidateReview from './pages/CandidateReview';

// // Admin Portal Pages
// import AdminDashboard from './pages/AdminDashboard';
// import AdminUsers from './pages/AdminUsers';

// export default function App() {
//   return (
//     <Router>
//       <Routes>
//         {/* Public & Auth Routes */}
//         <Route path="/" element={<Landing />} />
//         <Route path="/login" element={<Login />} />
//         <Route path="/register" element={<Register />} />

//         {/* Candidate Portal Routes */}
//         <Route path="/discovery" element={<SwipeDiscovery />} />
//         <Route path="/job-search" element={<JobSearch />} />
//         <Route path="/companies" element={<CompanyProfile />} />
//         <Route path="/resume-upload" element={<ResumeUpload />} />
//         <Route path="/dashboard" element={<Dashboard />} />
//         <Route path="/analytics" element={<Analytics />} />
//         <Route path="/profile" element={<Profile />} />
//         <Route path="/notifications" element={<Notifications />} />

//         {/* Recruiter Portal Routes */}
//         <Route path="/recruiter-dashboard" element={<RecruiterDashboard />} />
//         <Route path="/post-job" element={<PostJob />} />
//         <Route path="/ats-ranker" element={<AtsRanker />} />
//         <Route path="/candidate-review" element={<CandidateReview />} />

//         {/* Admin Portal Routes */}
//         <Route path="/admin-dashboard" element={<AdminDashboard />} />
//         <Route path="/admin-users" element={<AdminUsers />} />
//         {/* Fallback Catch-All Redirect */}
//         <Route path="*" element={<Navigate to="/" replace />} />
//       </Routes>
//     </Router>
//   );
// }