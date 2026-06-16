import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Settings, LogOut, Users, Dices, Calendar, Clock } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import userService from '../../services/user.service';
import gameService from '../../services/game.service';
import partyService from '../../services/party.service';
import Loader from '../../components/Loader';
import '../../style/Admin/Admin.css';

export default function AdminDashboard() {
  const navigate = useNavigate();
  const { logout, user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    usersActive: 0,
    gamesRegistered: 0,
    totalParties: 0,
    pendingApproval: 0,
  });

  useEffect(() => {
    const load = async () => {
      try {
        const [users, games, parties] = await Promise.all([
          userService.listActive().catch(() => []),
          gameService.listAll().catch(() => []),
          partyService.listAll().catch(() => []),
        ]);
        const partyList = Array.isArray(parties) ? parties : [];
        setStats({
          usersActive: Array.isArray(users) ? users.length : 0,
          gamesRegistered: Array.isArray(games) ? games.length : 0,
          totalParties: partyList.length,
          pendingApproval: partyList.filter((p) => p.status === 'PENDING').length,
        });
      } catch (err) {
        console.error('Erro ao carregar dashboard:', err);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const handleLogout = async () => {
    await logout();
    navigate('/');
  };

  if (loading) return <Loader />;

  return (
    <div className="admin-layout">
      <header className="admin-navbar">
        <div className="admin-navbar-inner">
          <div className="admin-brand">
            <div className="admin-gear"><Settings size={20} /></div>
            <div>
              <h1>Painel Administrativo</h1>
              <p>Bem-vindo, {user?.name || 'Administrador'}</p>
            </div>
          </div>
          <div className="admin-actions">
            <button className="admin-btn admin-btn-ghost" onClick={() => navigate('/home')}>Ver catálogo</button>
            <button className="admin-btn admin-btn-danger" onClick={handleLogout}>
              <LogOut size={16} /> Sair
            </button>
          </div>
        </div>
      </header>

      <main className="admin-main">
        <h2 className="admin-page-title">Dashboard</h2>
        <p className="admin-page-sub">Visão geral do sistema Player One</p>

        <section className="metrics-grid">
          <div className="metric-card">
            <div className="metric-top"><Users size={18} className="text-blue" /> Usuários</div>
            <div className="metric-number">{stats.usersActive}</div>
            <div className="metric-desc">Usuários ativos</div>
          </div>
          <div className="metric-card">
            <div className="metric-top"><Dices size={18} className="text-green" /> Jogos</div>
            <div className="metric-number">{stats.gamesRegistered}</div>
            <div className="metric-desc">Jogos cadastrados</div>
          </div>
          <div className="metric-card">
            <div className="metric-top"><Calendar size={18} className="text-purple" /> Party's</div>
            <div className="metric-number">{stats.totalParties}</div>
            <div className="metric-desc">Total de party's</div>
          </div>
          <div className="metric-card pending">
            <div className="metric-top"><Clock size={18} className="text-orange" /> Pendentes</div>
            <div className="metric-number">{stats.pendingApproval}</div>
            <div className="metric-desc">Party's aguardando aprovação</div>
          </div>
        </section>

        <section className="quick-panel">
          <h3>Ações Rápidas</h3>
          <p>Gerenciar o sistema Player One</p>
          <div className="quick-grid">
            <button className="quick-tile" onClick={() => navigate('/admin/games')}>
              <Dices size={28} className="text-green" />
              <span>Gerenciar Jogos</span>
            </button>
            <button className="quick-tile" onClick={() => navigate('/admin/users')}>
              <Users size={28} className="text-blue" />
              <span>Gerenciar Usuários</span>
            </button>
            <button className="quick-tile" onClick={() => navigate('/admin/parties')}>
              <Calendar size={28} className="text-purple" />
              <span>Gerenciar Party's</span>
              {stats.pendingApproval > 0 && <div className="tile-badge">{stats.pendingApproval}</div>}
            </button>
          </div>
        </section>
      </main>
    </div>
  );
}
