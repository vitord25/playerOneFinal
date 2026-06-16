import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import partyService from '../../services/party.service';
import gameService from '../../services/game.service';
import { useAuth } from '../../context/AuthContext';
import Loader from '../../components/Loader';

import '../../style/StylePages/StylePartyDetails.css';

export default function PartyDetails() {
  const navigate = useNavigate();
  const { id } = useParams();
  const { user } = useAuth();
  const chatScrollRef = useRef(null);

  const [loading, setLoading] = useState(true);
  const [erro, setErro] = useState('');
  const [party, setParty] = useState(null);
  const [members, setMembers] = useState([]);
  const [requests, setRequests] = useState([]);
  const [messages, setMessages] = useState([]);
  const [typedMessage, setTypedMessage] = useState('');

  const isHost = party && user && party.organizer_id === user.id;
  const isApprovedMember =
    isHost ||
    members.some((m) => m.user_id === user?.id && m.status === 'APPROVED');

  const loadAll = useCallback(async () => {
    setLoading(true);
    setErro('');
    try {
      const p = await partyService.getById(id);
      setParty(p);

      // Nome do jogo (best-effort)
      try {
        const g = await gameService.getById(p.game_id);
        p.gameName = g?.name;
        setParty({ ...p });
      } catch (_) { /* ignore */ }

      // Membros (organizador/admin conseguem listar)
      try {
        const mem = await partyService.listMembers(id);
        const list = Array.isArray(mem) ? mem : [];
        setMembers(list.filter((m) => m.status === 'APPROVED'));
        setRequests(list.filter((m) => m.status === 'PENDING'));
      } catch (_) {
        setMembers([]);
        setRequests([]);
      }

      // Mensagens (apenas membros aprovados/admin)
      try {
        const msgs = await partyService.listMessages(id);
        setMessages(Array.isArray(msgs) ? msgs : []);
      } catch (_) {
        setMessages([]);
      }
    } catch (err) {
      console.error('Erro ao carregar party:', err);
      setErro('Mesa não encontrada ou indisponível.');
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    loadAll();
  }, [loadAll]);

  useEffect(() => {
    if (chatScrollRef.current) {
      chatScrollRef.current.scrollTop = chatScrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!typedMessage.trim()) return;
    const content = typedMessage.trim();
    setTypedMessage('');
    try {
      const created = await partyService.sendMessage(id, { content });
      setMessages((prev) => [...prev, created]);
    } catch (err) {
      console.error('Erro ao enviar mensagem:', err);
      const detail = err?.response?.data?.detail;
      alert(typeof detail === 'string' ? detail : 'Não foi possível enviar a mensagem.');
      setTypedMessage(content);
    }
  };

  const handleApproveRequest = async (member) => {
    try {
      await partyService.approveMember(id, member.id);
      await loadAll();
    } catch (err) {
      console.error('Erro ao aprovar:', err);
      const detail = err?.response?.data?.detail;
      alert(typeof detail === 'string' ? detail : 'Não foi possível aprovar o jogador.');
    }
  };

  const handleRejectRequest = async (member) => {
    try {
      await partyService.rejectMember(id, member.id);
      setRequests((prev) => prev.filter((r) => r.id !== member.id));
    } catch (err) {
      console.error('Erro ao rejeitar:', err);
      alert('Não foi possível rejeitar o jogador.');
    }
  };

  const handleRemoveMember = async (member) => {
    try {
      await partyService.removeMember(id, member.id);
      setMembers((prev) => prev.filter((m) => m.id !== member.id));
    } catch (err) {
      console.error('Erro ao remover membro:', err);
      alert('Não foi possível remover o jogador.');
    }
  };

  const handleLeaveOrCancel = async () => {
    if (isHost) {
      if (!window.confirm('Tem certeza que deseja cancelar esta mesa permanentemente?')) return;
      try {
        await partyService.cancelParty(id);
        navigate('/parties/my');
      } catch (err) {
        alert('Não foi possível cancelar a mesa.');
      }
    } else {
      if (!window.confirm('Deseja mesmo sair desta mesa?')) return;
      try {
        await partyService.leaveParty(id);
        navigate('/parties/my');
      } catch (err) {
        alert('Não foi possível sair da mesa.');
      }
    }
  };

  const getInitials = (name) => {
    if (!name) return "?";
    return String(name).split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
  };

  const memberLabel = (m) => (m.user_id === user?.id ? 'Você' : `Usuário #${m.user_id}`);
  const senderLabel = (msg) => (msg.user_id === user?.id ? 'Você' : `Usuário #${msg.user_id}`);
  const formatTime = (iso) => {
    if (!iso) return '';
    try {
      return new Date(iso).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
    } catch (_) { return ''; }
  };
  const formatStringDate = (dateStr) => {
    if (!dateStr) return '';
    try { return new Date(dateStr).toLocaleDateString('pt-BR'); } catch (_) { return dateStr; }
  };

  if (loading) return <Loader />;

  if (erro || !party) {
    return (
      <div className="party-details-empty-screen">
        <span className="material-symbols-outlined" style={{ fontSize: '48px', color: '#ff4757' }}>error</span>
        <h2>Mesa não encontrada</h2>
        <p>{erro || 'A mesa solicitada não existe ou foi encerrada pelo organizador.'}</p>
        <button className="btn-details-back-fallback" onClick={() => navigate('/parties/my')}>
          Voltar para minhas reservas
        </button>
      </div>
    );
  }

  const emptySlotsCount = Math.max(0, (party.max_players || 0) - members.length);

  return (
    <div className="party-details-page-wrapper">

      <header className="party-details-sticky-header">
        <div className="party-details-header-container">
          <button className="btn-details-header-back" onClick={() => navigate(-1)} title="Voltar">
            <span className="material-symbols-outlined">arrow_back</span>
          </button>
          <div className="party-details-header-titles">
            <h1>{party.gameName || `Jogo #${party.game_id}`}</h1>
            <p>{isHost ? "Você é o organizador desta mesa" : `Mesa #${party.id}`}</p>
          </div>
        </div>
      </header>

      <main className="party-details-main-layout">
        <div className="party-details-grid-container">

          <div className="details-sidebar-column">

            <div className="details-custom-card">
              <div className="details-card-header">
                <h3>Informações da Partida</h3>
                <span className="card-sub-label">Detalhes da reserva na biblioteca</span>
              </div>

              <div className="spacing-rows">
                <div className="info-meta-row">
                  <span className="material-symbols-outlined icon-muted">calendar_month</span>
                  <div><label>Data</label><p>{formatStringDate(party.date)}</p></div>
                </div>
                <div className="info-meta-row">
                  <span className="material-symbols-outlined icon-muted">schedule</span>
                  <div><label>Horário</label><p>{party.time}</p></div>
                </div>
                <div className="info-meta-row">
                  <span className="material-symbols-outlined icon-muted">location_on</span>
                  <div><label>Localização</label><p>{party.location}</p></div>
                </div>
                <div className="info-meta-row">
                  <span className="material-symbols-outlined icon-muted">groups</span>
                  <div>
                    <label>Vagas</label>
                    <p className="slots-sub-badge">{members.length} / {party.max_players} Jogadores</p>
                  </div>
                </div>
              </div>

              <hr className="details-divider" />

              <div className="info-description-block">
                <label>Descrição da Mesa</label>
                <p>{party.description}</p>
              </div>

              <div style={{ marginTop: '20px' }}>
                {isHost ? (
                  <button className="btn-details-action-trigger leave-mode" onClick={handleLeaveOrCancel}>
                    <span className="material-symbols-outlined">delete_forever</span> Cancelar Mesa
                  </button>
                ) : isApprovedMember ? (
                  <button className="btn-details-action-trigger leave-mode" onClick={handleLeaveOrCancel}>
                    <span className="material-symbols-outlined">logout</span> Sair da Mesa
                  </button>
                ) : null}
              </div>
            </div>

            {isHost && requests.length > 0 && (
              <div className="details-custom-card panel-requests-alert">
                <div className="details-card-header">
                  <h3>Solicitações de Entrada</h3>
                  <span className="card-sub-label">Aprove ou rejeite novos jogadores</span>
                </div>

                <div className="requests-approval-stack">
                  {requests.map((req) => (
                    <div key={req.id} className="request-approval-item">
                      <div className="details-avatar-circle" style={{ width: '32px', height: '32px', fontSize: '11px' }}>
                        {getInitials(memberLabel(req))}
                      </div>
                      <div className="request-approval-info">
                        <p className="req-name">{memberLabel(req)}</p>
                      </div>
                      <div className="request-approval-actions">
                        <button className="btn-req-approve" title="Aprovar" onClick={() => handleApproveRequest(req)}>
                          <span className="material-symbols-outlined" style={{ fontSize: '18px' }}>check</span>
                        </button>
                        <button className="btn-req-reject" title="Recusar" onClick={() => handleRejectRequest(req)}>
                          <span className="material-symbols-outlined" style={{ fontSize: '18px' }}>close</span>
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="details-custom-card">
              <div className="details-card-header">
                <h3>Participantes Confirmados</h3>
                <span className="card-sub-label">Jogadores na mesa atualmente</span>
              </div>

              <div className="participants-list-stack">
                {members.map((member) => {
                  const isOrganizer = member.user_id === party.organizer_id;
                  return (
                    <div key={member.id} className="participant-member-item">
                      <div className="details-avatar-circle">{getInitials(memberLabel(member))}</div>
                      <div className="participant-member-meta">
                        <p className="member-name">{memberLabel(member)}</p>
                        {isOrganizer && <span className="host-indicator-badge">Organizador</span>}
                      </div>
                      {isHost && !isOrganizer && (
                        <button className="btn-remove-member" title="Remover" onClick={() => handleRemoveMember(member)}>
                          <span className="material-symbols-outlined" style={{ fontSize: '18px' }}>person_remove</span>
                        </button>
                      )}
                    </div>
                  );
                })}

                {Array.from({ length: emptySlotsCount }).map((_, idx) => (
                  <div key={`empty-${idx}`} className="participant-member-item slot-empty-row">
                    <div className="details-avatar-circle empty-avatar">
                      <span className="material-symbols-outlined" style={{ fontSize: '16px', color: '#9ca3af' }}>add</span>
                    </div>
                    <div className="participant-member-meta">
                      <p className="slot-empty-text">Vaga disponível</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

          </div>

          <div className="details-custom-card chat-card-layout">
            <div className="details-card-header">
              <h3>Bate-papo da Mesa</h3>
              <span className="card-sub-label">Comunicação com o grupo</span>
            </div>

            <div className="chat-messages-container-scroll" ref={chatScrollRef}>
              {messages.length === 0 ? (
                <div className="chat-empty-state">
                  <p>Nenhuma mensagem por aqui. Envie um oi para iniciar!</p>
                </div>
              ) : (
                <div className="chat-messages-inner-stack">
                  {messages.map((msg) => {
                    const isOwn = msg.user_id === user?.id;
                    return (
                      <div key={msg.id} className={`chat-message-row ${isOwn ? 'own-msg-row' : ''}`}>
                        <div className="details-avatar-circle chat-avatar">{getInitials(senderLabel(msg))}</div>
                        <div>
                          <div className="chat-message-meta-info">
                            <span className="chat-sender-name">{senderLabel(msg)}</span>
                            <span className="chat-msg-time">{formatTime(msg.created_at)}</span>
                          </div>
                          <div className="chat-message-bubble">
                            <p>{msg.content}</p>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>

            <div className="chat-footer-form-box">
              {isApprovedMember ? (
                <form onSubmit={handleSendMessage} className="chat-native-form">
                  <input
                    type="text"
                    className="chat-native-input"
                    placeholder="Digite uma mensagem na mesa..."
                    value={typedMessage}
                    onChange={(e) => setTypedMessage(e.target.value)}
                  />
                  <button type="submit" className="btn-chat-send" disabled={!typedMessage.trim()}>
                    <span className="material-symbols-outlined">send</span>
                  </button>
                </form>
              ) : (
                <div className="chat-locked-warning">
                  <span className="material-symbols-outlined" style={{ fontSize: '18px', verticalAlign: 'middle', marginRight: '6px' }}>lock</span>
                  Você precisa ser um participante aprovado para interagir no chat.
                </div>
              )}
            </div>

          </div>

        </div>
      </main>
    </div>
  );
}
