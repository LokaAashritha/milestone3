import React from 'react';
import { Navigate } from 'react-router-dom';

export default function ProtectedRoute({ children, allowedRoles }) {
  const token = localStorage.getItem('swipex_auth_token');
  const userRole = localStorage.getItem('swipex_role') || 'candidate';

  // 1. If unauthenticated, send user to login
  if (!token) {
    return <Navigate to="/login" replace />;
  }

  // 2. If user role is not permitted for this page, send to their default portal
  if (allowedRoles && !allowedRoles.includes(userRole)) {
    if (userRole === 'recruiter') return <Navigate to="/recruiter-dashboard" replace />;
    if (userRole === 'admin') return <Navigate to="/admin-dashboard" replace />;
    return <Navigate to="/discovery" replace />;
  }

  // 3. Otherwise, render the requested page
  return children;
}