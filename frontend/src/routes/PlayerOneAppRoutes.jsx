import { Routes, Route, Navigate } from 'react-router-dom';
import React from 'react';

import Login from '../pages/Register/Login';
import Register from '../pages/Register/Register';
import ProtectedRoute from '../components/ProtectedRoute';

// Páginas do Aluno
import Home from '../pages/Home';
import Profile from '../pages/Perfil/Perfil';
import Detail from '../pages/Aluno/Detail';
import CreateParty from '../pages/Aluno/CreateParty';
import PartiesList from '../pages/Aluno/PartysList';
import MyPartys from '../pages/Aluno/MyPartys';
import PartyDetails from '../pages/Aluno/PartyDetails';

// Páginas do Admin
import AdminDashboard from '../pages/Admin/Dashboard';
import ManageGames from '../pages/Admin/ManageGames';
import ManageUsers from '../pages/Admin/ManageUsers';
import ManageParties from '../pages/Admin/ManageParties';

function AppRoutes({ searchQuery }) {
  return (
    <Routes>
      {/* Rotas Públicas */}
      <Route path="/" element={<Login />} />
      <Route path="/cadastro" element={<Register />} />

      {/* Rotas do Aluno (protegidas: exigem login) */}
      <Route
        path="/home"
        element={
          <ProtectedRoute>
            <Home searchQuery={searchQuery} />
          </ProtectedRoute>
        }
      />
      <Route
        path="/perfil"
        element={
          <ProtectedRoute>
            <Profile />
          </ProtectedRoute>
        }
      />
      <Route
        path="/jogo/:id"
        element={
          <ProtectedRoute>
            <Detail />
          </ProtectedRoute>
        }
      />
      <Route
        path="/parties/create"
        element={
          <ProtectedRoute userOnly>
            <CreateParty />
          </ProtectedRoute>
        }
      />
      <Route
        path="/parties/my"
        element={
          <ProtectedRoute>
            <MyPartys />
          </ProtectedRoute>
        }
      />
      <Route
        path="/parties/:id"
        element={
          <ProtectedRoute>
            <PartyDetails />
          </ProtectedRoute>
        }
      />
      <Route
        path="/parties"
        element={
          <ProtectedRoute>
            <PartiesList />
          </ProtectedRoute>
        }
      />

      {/* Rotas do Admin (protegidas: exigem login + papel ADMIN) */}
      <Route
        path="/admin/dashboard"
        element={
          <ProtectedRoute adminOnly>
            <AdminDashboard />
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin/games"
        element={
          <ProtectedRoute adminOnly>
            <ManageGames />
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin/users"
        element={
          <ProtectedRoute adminOnly>
            <ManageUsers />
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin/parties"
        element={
          <ProtectedRoute adminOnly>
            <ManageParties />
          </ProtectedRoute>
        }
      />

      {/* Fallback de Segurança */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default AppRoutes;
