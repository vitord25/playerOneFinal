import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Loader from './Loader';

// ============================================================================
// Rota protegida — garante que o usuário esteja autenticado. Quando
// `adminOnly` é true, exige também o papel ADMIN. Quando `userOnly` é true,
// bloqueia administradores (ex.: criação de party é exclusiva de usuários).
// ============================================================================
export default function ProtectedRoute({ children, adminOnly = false, userOnly = false }) {
  const { isAuthenticated, isAdmin, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return <Loader />;
  }

  if (!isAuthenticated) {
    return <Navigate to="/" replace state={{ from: location }} />;
  }

  if (adminOnly && !isAdmin) {
    return <Navigate to="/home" replace />;
  }

  if (userOnly && isAdmin) {
    return <Navigate to="/admin/dashboard" replace />;
  }

  return children;
}
