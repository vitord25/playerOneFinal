import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import partyService from '../../services/party.service';
import gameService from '../../services/game.service';
import { adaptGames } from '../../services/adapters';
import { useAuth } from '../../context/AuthContext';
import Loader from '../../components/Loader';

import '../../style/StylePages/StyleMyPartys.css';

export default function MyPartys() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('parties');

  const [myCreatedParties, setMyCreatedParties] = useState([]);
  const [joinedParties, setJoinedParties] = useState([]);
  const [pendingRequests, setPendingRequests] = useState([]);

  const statusLabel = (status) => {
    const map = {
      PENDING: 'Pendente',
      APPROVED: 'Aprovada',
      REJECTED: 'Rejeitada',
      CANCELLED: 'Cancelada',
    };
    return map[status] || status;
  };

  const loadData = useCallback(async () => {
    if (!user) return;
    setLoading(true);
    try {
      const [parties, games] = await Promise.all([
        partyService.listMyParties(),
        gameService.listAvailable().catch(() => []),
      ]);

      const adaptedGames = adaptGames(Array.isArray(games) ? games : []);
      const gamesById = {};
      adaptedGames.forEach((g) => { gamesById[g.id] = g; });
      const gameName = (id) => (gamesById[id] ? gamesById[id].nome : `Jogo #${id}`);

      const created = [];
      const joined = [];
      const list = Array.isArray(parties) ? parties : [];

      list.forEach((p) => {
        const base = {
          id: p.id,
          gameName: gameName(p.game_id),
          description: p.description,
          slots: p.max_players,
          date: p.date,
          time: p.time,
          location: p.location,
          status: p.status,
        };
        if (p.organizer_id === user.id) {
          created.push(base);
        } else {
          joined.push(base);
        }
      });

      // Solicitações pendentes recebidas nas parties que EU organizo
      const requests = [];
      await Promise.all(
        created.map(async (p) => {
          try {
            const members = await partyService.listMembers(p.id);
            (members || [])
              .filter((m) => m.status === 'PENDING')
              .forEach((m) => {
                requests.push({
                  id: m.id,
                  partyId: p.id,
                  memberId: m.id,
                  gameName: p.gameName,
                  partyDate: p.date,
                  partyTime: p.time,
                  userName: `Usuário #${m.user_id}`,
                  userId: m.user_id,
                });
              });
          } catch (_) {
            // ignora parties sem permissão de leitura de membros
          }
        })
      );

      setMyCreatedParties(created);
      setJoinedParties(joined);
      setPendingRequests(requests);
    } catch (err) {
      console.error('Erro ao carregar minhas parties:', err);
    } finally {
      setLoading(false);
    }
  }, [user]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleApproveRequest = async (request) => {
    try {
      await partyService.approveMember(request.partyId, request.memberId);
      setPendingRequests((prev) => prev.filter((req) => req.id !== request.id));
    } catch (err) {
      console.error('Erro ao aprovar membro:', err);
      const detail = err?.response?.data?.detail;
      alert(typeof detail === 'string' ? detail : 'Não foi possível aprovar o jogador.');
    }
  };

  const handleRejectRequest = async (request) => {
    try {
      await partyService.rejectMember(request.partyId, request.memberId);
      setPendingRequests((prev) => prev.filter((req) => req.id !== request.id));
    } catch (err) {
      console.error('Erro ao rejeitar membro:', err);
      alert('Não foi possível rejeitar o jogador.');
    }
  };

  const getInitials = (name) => {
    if (!name) return "?";
    return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
  };

  if (loading) {
    return <Loader />;
  }

  const totalPartiesCount = myCreatedParties.length + joinedParties.length;

  return (
    <div className="my-parties-wrapper">
      <header className="my-parties-header">
        <div className="my-parties-header-content">
          <div className="my-header-left">
            <button className="btn-my-back" onClick={() => navigate(-1)}>
              <span className="material-symbols-outlined">arrow_back</span>
            </button>
            <h1 className="my-header-title">Minhas Party's</h1>
          </div>
        </div>
      </header>

      <main className="my-parties-main">
        <div className="my-parties-dashboard-container">

          <section className="my-dashboard-intro">
            <h2>Gerenciar Party's</h2>
            <p className="my-dashboard-subtext">
              {myCreatedParties.length} criada{myCreatedParties.length !== 1 ? 's' : ''} • {joinedParties.length} participando • {pendingRequests.length} solicitaç{pendingRequests.length !== 1 ? 'ões' : 'ão'} pendente{pendingRequests.length !== 1 ? 's' : ''}
            </p>
          </section>

          <div className="my-tabs-list">
            <button
              className={`my-tab-trigger ${activeTab === 'parties' ? 'active' : ''}`}
              onClick={() => setActiveTab('parties')}
            >
              Minhas Party's ({totalPartiesCount})
            </button>
            <button
              className={`my-tab-trigger relative-trigger ${activeTab === 'requests' ? 'active' : ''}`}
              onClick={() => setActiveTab('requests')}
            >
              Solicitações recebidas
              {pendingRequests.length > 0 && (
                <span className="my-requests-badge-count">
                  {pendingRequests.length}
                </span>
              )}
            </button>
          </div>

          {activeTab === 'parties' && (
            <div className="my-tab-content-pane">
              {totalPartiesCount > 0 ? (
                <div className="my-parties-grid-flow">

                  {myCreatedParties.map((party) => (
                    <div key={`created-${party.id}`} className="my-custom-card highlight-host-card">
                      <div className="my-card-header-row">
                        <div>
                          <div className="host-indicator-pill">Você é o Responsável</div>
                          <h3 className="my-card-game-title">{party.gameName}</h3>
                          <p className="my-card-game-desc">{party.description}</p>
                        </div>
                        <span className="my-status-badge badge-approved">{statusLabel(party.status)}</span>
                      </div>
                      <div className="my-card-details-grid">
                        <div className="my-detail-item"><span className="material-symbols-outlined">calendar_month</span> {party.date ? new Date(party.date).toLocaleDateString('pt-BR') : '-'}</div>
                        <div className="my-detail-item"><span className="material-symbols-outlined">schedule</span> {party.time}</div>
                        <div className="my-detail-item"><span className="material-symbols-outlined">location_on</span> {party.location}</div>
                        <div className="my-detail-item"><span className="material-symbols-outlined">groups</span> {party.slots} vagas</div>
                      </div>
                      <button className="btn-my-card-action"
                        onClick={() => navigate(`/parties/${party.id}`, { state: { isMember: true, isHost: true } })} >
                        <span className="material-symbols-outlined">visibility</span> Ver Detalhes da Mesa
                      </button>
                    </div>
                  ))}

                  {joinedParties.map((party) => (
                    <div key={`joined-${party.id}`} className="my-custom-card">
                      <div className="my-card-header-row">
                        <div>
                          <span className="guest-indicator-label">Participando</span>
                          <h3 className="my-card-game-title">{party.gameName}</h3>
                          <p className="my-card-game-desc">{party.description}</p>
                        </div>
                        <span className="my-status-badge badge-joined">{statusLabel(party.status)}</span>
                      </div>
                      <div className="my-card-details-grid">
                        <div className="my-detail-item"><span className="material-symbols-outlined">calendar_month</span> {party.date ? new Date(party.date).toLocaleDateString('pt-BR') : '-'}</div>
                        <div className="my-detail-item"><span className="material-symbols-outlined">schedule</span> {party.time}</div>
                        <div className="my-detail-item"><span className="material-symbols-outlined">location_on</span> {party.location}</div>
                        <div className="my-detail-item"><span className="material-symbols-outlined">groups</span> {party.slots} vagas</div>
                      </div>
                      <button className="btn-my-card-action"
                        onClick={() => navigate(`/parties/${party.id}`, { state: { isMember: true, isHost: false } })} >
                        <span className="material-symbols-outlined">visibility</span> Ver Detalhes da Mesa
                      </button>
                    </div>
                  ))}

                </div>
              ) : (
                <div className="my-parties-empty-state-pane">
                  <p>Você ainda não possui nenhuma movimentação em partidas.</p>
                  <button className="btn-my-empty-action" onClick={() => navigate('/parties')}>
                    Procurar Partys Disponíveis
                  </button>
                </div>
              )}
            </div>
          )}

          {activeTab === 'requests' && (
            <div className="my-tab-content-pane">
              {pendingRequests.length > 0 ? (
                <div className="my-parties-grid-flow">
                  {pendingRequests.map((request) => (
                    <div key={request.id} className="my-custom-card request-card-layout">
                      <div className="request-card-top">
                        <h3 className="request-game-context">Mesa de {request.gameName}</h3>
                        <p className="request-time-context">Agendada para {request.partyDate ? new Date(request.partyDate).toLocaleDateString('pt-BR') : '-'} às {request.partyTime}</p>
                      </div>

                      <div className="request-user-profile-bar">
                        <div className="my-avatar-circle">
                          <span className="my-avatar-fallback">{getInitials(request.userName)}</span>
                        </div>
                        <div className="request-user-info">
                          <p className="request-user-name">{request.userName}</p>
                          <p className="request-user-date-sub">Solicitou ingressar na partida</p>
                        </div>
                      </div>

                      <div className="request-actions-dual-row">
                        <button
                          className="btn-request-decision approve-trigger"
                          onClick={() => handleApproveRequest(request)}
                        >
                          <span className="material-symbols-outlined">check</span> Aprovar Jogador
                        </button>
                        <button
                          className="btn-request-decision reject-trigger"
                          onClick={() => handleRejectRequest(request)}
                        >
                          <span className="material-symbols-outlined">close</span> Rejeitar
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="my-parties-empty-state-pane">
                  <span className="material-symbols-outlined big-empty-icon">notification_important</span>
                  <p>Nenhuma solicitação de entrada pendente no momento.</p>
                </div>
              )}
            </div>
          )}

        </div>
      </main>
    </div>
  );
}
