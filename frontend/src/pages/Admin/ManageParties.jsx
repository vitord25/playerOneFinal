import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Check, X, Ban, Trash2, Calendar, Clock, MapPin, Users, MessageSquare, XCircle } from 'lucide-react';
import partyService from '../../services/party.service';
import gameService from '../../services/game.service';
import Loader from '../../components/Loader';
import '../../style/Admin/Admin.css';

const STATUS_LABEL = {
  PENDING: 'Pendente',
  APPROVED: 'Aprovada',
  REJECTED: 'Rejeitada',
  CANCELLED: 'Cancelada',
};
const STATUS_CLASS = {
  PENDING: 'tag-pending',
  APPROVED: 'tag-approved',
  REJECTED: 'tag-rejected',
  CANCELLED: 'tag-cancelled',
};

export default function ManageParties() {
  const navigate = useNavigate();
  const [parties, setParties] = useState([]);
  const [gamesById, setGamesById] = useState({});
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('ALL');
  const [chatParty, setChatParty] = useState(null); // party cujo chat está aberto
  const [messages, setMessages] = useState([]);
  const [chatLoading, setChatLoading] = useState(false);
  const [chatError, setChatError] = useState('');

  const load = async () => {
    setLoading(true);
    try {
      const [partyList, games] = await Promise.all([
        partyService.listAll(),
        gameService.listAll().catch(() => []),
      ]);
      const map = {};
      (Array.isArray(games) ? games : []).forEach((g) => { map[g.id] = g; });
      setGamesById(map);
      setParties(Array.isArray(partyList) ? partyList : []);
    } catch (err) {
      console.error('Erro ao listar parties:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const act = async (fn, errMsg) => {
    try {
      await fn();
      await load();
    } catch (err) {
      const detail = err?.response?.data?.detail;
      alert(typeof detail === 'string' ? detail : errMsg);
    }
  };

  const gameName = (id) => (gamesById[id] ? gamesById[id].name : `Jogo #${id}`);

  const openChat = async (p) => {
    setChatParty(p);
    setChatError('');
    setMessages([]);
    setChatLoading(true);
    try {
      const data = await partyService.listMessages(p.id);
      setMessages(Array.isArray(data) ? data : []);
    } catch (err) {
      const detail = err?.response?.data?.detail;
      setChatError(typeof detail === 'string' ? detail : 'Não foi possível carregar as mensagens.');
    } finally {
      setChatLoading(false);
    }
  };

  const closeChat = () => {
    setChatParty(null);
    setMessages([]);
    setChatError('');
  };

  const removeMessage = async (messageId) => {
    if (!chatParty) return;
    try {
      await partyService.deleteMessage(chatParty.id, messageId);
      setMessages((prev) => prev.filter((m) => m.id !== messageId));
    } catch (err) {
      const detail = err?.response?.data?.detail;
      alert(typeof detail === 'string' ? detail : 'Não foi possível excluir a mensagem.');
    }
  };

  const filtered = filter === 'ALL' ? parties : parties.filter((p) => p.status === filter);

  if (loading) return <Loader />;

  return (
    <div className="admin-layout">
      <header className="admin-navbar">
        <div className="admin-navbar-inner">
          <div className="admin-brand">
            <button className="admin-btn admin-btn-ghost" onClick={() => navigate('/admin/dashboard')}>
              <ArrowLeft size={16} />
            </button>
            <div><h1>Gerenciar Party's</h1></div>
          </div>
        </div>
      </header>

      <main className="admin-main">
        <div className="admin-toolbar">
          <span className="admin-count">{filtered.length} party's</span>
          <div className="admin-actions">
            {['ALL', 'PENDING', 'APPROVED', 'REJECTED', 'CANCELLED'].map((s) => (
              <button
                key={s}
                className={`admin-btn ${filter === s ? 'admin-btn-primary' : 'admin-btn-ghost'}`}
                onClick={() => setFilter(s)}
              >
                {s === 'ALL' ? 'Todas' : STATUS_LABEL[s]}
              </button>
            ))}
          </div>
        </div>

        {filtered.length === 0 ? (
          <div className="admin-empty">Nenhuma party's nesta categoria.</div>
        ) : (
          <div className="admin-card-list">
            {filtered.map((p) => (
              <div key={p.id} className="admin-row-card">
                <div className="admin-row-main">
                  <div className="admin-row-title">
                    {gameName(p.game_id)}
                    <span className={`admin-tag ${STATUS_CLASS[p.status] || ''}`}>{STATUS_LABEL[p.status] || p.status}</span>
                  </div>
                  <p className="admin-row-desc">{p.description}</p>
                  <div className="admin-row-meta">
                    <span><Calendar size={14} /> {p.date ? new Date(p.date).toLocaleDateString('pt-BR') : '-'}</span>
                    <span><Clock size={14} /> {p.time}</span>
                    <span><MapPin size={14} /> {p.location}</span>
                    <span><Users size={14} /> {p.max_players} vagas</span>
                  </div>
                </div>
                <div className="admin-row-actions">
                  {p.status === 'PENDING' && (
                    <>
                      <button className="admin-btn admin-btn-success" onClick={() => act(() => partyService.approveParty(p.id), 'Não foi possível aprovar.')}>
                        <Check size={15} /> Aprovar
                      </button>
                      <button className="admin-btn admin-btn-warning" onClick={() => act(() => partyService.rejectParty(p.id), 'Não foi possível rejeitar.')}>
                        <X size={15} /> Rejeitar
                      </button>
                    </>
                  )}
                  {(p.status === 'PENDING' || p.status === 'APPROVED') && (
                    <button className="admin-btn admin-btn-ghost" onClick={() => act(() => partyService.cancelParty(p.id), 'Não foi possível cancelar.')}>
                      <Ban size={15} /> Cancelar
                    </button>
                  )}
                  <button className="admin-btn admin-btn-ghost" onClick={() => openChat(p)} title="Ver chat da party (moderação)">
                    <MessageSquare size={15} /> Ver Chat
                  </button>
                  <button className="icon-btn delete" onClick={() => act(() => partyService.delete(p.id), 'Não foi possível excluir.')}>
                    <Trash2 size={16} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>

      {chatParty && (
        <div className="admin-modal-overlay" onClick={closeChat}>
          <div className="admin-modal" onClick={(e) => e.stopPropagation()}>
            <div className="admin-modal-header">
              <h2>Chat — {gameName(chatParty.game_id)}</h2>
              <button className="admin-btn admin-btn-ghost" onClick={closeChat}>
                <XCircle size={18} />
              </button>
            </div>

            <div className="admin-modal-body">
              {chatLoading ? (
                <div className="admin-empty">Carregando mensagens...</div>
              ) : chatError ? (
                <div className="admin-modal-error">{chatError}</div>
              ) : messages.length === 0 ? (
                <div className="admin-empty">Nenhuma mensagem neste chat.</div>
              ) : (
                <div className="admin-chat-list">
                  {messages.map((m) => (
                    <div key={m.id} className="admin-chat-msg">
                      <div className="admin-chat-msg-main">
                        <div className="admin-chat-msg-head">
                          <strong>{m.user?.name || `Usuário #${m.user_id}`}</strong>
                          <span className="admin-chat-msg-time">
                            {m.created_at ? new Date(m.created_at).toLocaleString('pt-BR') : ''}
                          </span>
                        </div>
                        <p className="admin-chat-msg-content">{m.content}</p>
                      </div>
                      <button
                        className="icon-btn delete"
                        title="Excluir mensagem (moderação)"
                        onClick={() => removeMessage(m.id)}
                      >
                        <Trash2 size={15} />
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="admin-modal-footer">
              <button className="admin-btn admin-btn-ghost" onClick={closeChat}>
                Fechar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
