import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import gameService from '../../services/game.service';
import partyService from '../../services/party.service';
import { adaptGames } from '../../services/adapters';
import Loader from '../../components/Loader';

import '../../style/StylePages/StyleCreateParty.css';

export default function CreateParty() {
  const navigate = useNavigate();
  const location = useLocation();

  const preselectedGameId = location.state?.gameId;

  const [gamesList, setGamesList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [erro, setErro] = useState('');
  const [enviando, setEnviando] = useState(false);

  const [gameId, setGameId] = useState(preselectedGameId ? String(preselectedGameId) : '');
  const [date, setDate] = useState('');
  const [time, setTime] = useState('');
  const [slots, setSlots] = useState('4');
  const [description, setDescription] = useState('');

  const FIXED_LOCATION = 'Biblioteca da Unifor';

  useEffect(() => {
    gameService.listAvailable()
      .then((res) => {
        setGamesList(adaptGames(Array.isArray(res) ? res : []));
      })
      .catch((err) => {
        console.error("Erro ao buscar jogos:", err);
        setErro('Não foi possível carregar a lista de jogos.');
      })
      .finally(() => setLoading(false));
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErro('');
    setEnviando(true);

    // Garante o formato HH:MM:SS exigido pelo backend
    const horaFormatada = time.length === 5 ? `${time}:00` : time;

    const novaParty = {
      game_id: Number(gameId),
      description: description || 'Party criada via Player One.',
      date,
      time: horaFormatada,
      location: FIXED_LOCATION,
      max_players: Number(slots),
    };

    try {
      await partyService.create(novaParty);
      alert("Party criada com sucesso! Aguarde a aprovação do administrador.");
      navigate('/parties/my');
    } catch (err) {
      console.error("Erro ao criar party:", err);
      const detail = err?.response?.data?.detail;
      setErro(typeof detail === 'string' ? detail : 'Não foi possível criar a party.');
    } finally {
      setEnviando(false);
    }
  };

  if (loading) return <Loader />;

  return (
    <div className="create-party-wrapper">
      <header className="create-party-header">
        <div className="create-party-header-content">
          <button className="btn-icon-back" onClick={() => navigate(-1)}>←</button>
          <h1>Criar Nova Party's</h1>
        </div>
      </header>

      <main className="create-party-main">
        <div className="create-party-card">
          <div className="create-party-info-block">
            <div className="info-block-icon">
              <span className="material-symbols-outlined" style={{ fontSize: '28px', color: '#090d16' }}>
                calendar_month
              </span>
            </div>
            <div className="info-block-text">
              <h2>Organize sua partida</h2>
              <p>Preencha os detalhes abaixo</p>
            </div>
          </div>

          {erro && <div className="auth-error-box" style={{ marginBottom: '16px' }}>{erro}</div>}

          <form onSubmit={handleSubmit} className="form-group-stack">
            <div className="form-field">
              <label htmlFor="game-select">Jogo</label>
              <select
                id="game-select"
                value={gameId}
                onChange={(e) => setGameId(e.target.value)}
                required
              >
                <option value="" disabled>Selecione um jogo</option>
                {gamesList.map((game) => (
                  <option key={game.id} value={String(game.id)}>
                    {game.nome}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-grid-2">
              <div className="form-field">
                <label htmlFor="party-date">Data</label>
                <input id="party-date" type="date" value={date} onChange={(e) => setDate(e.target.value)} required />
              </div>
              <div className="form-field">
                <label htmlFor="party-time">Horário</label>
                <input id="party-time" type="time" value={time} onChange={(e) => setTime(e.target.value)} required />
              </div>
            </div>

            <div className="form-field">
              <label>Local</label>
              <div className="fixed-location-box">
                <span className="fixed-location-icon">📍</span>
                <span className="fixed-location-text">{FIXED_LOCATION}</span>
              </div>
              <p className="fixed-location-sub">Todas as party's acontecem na Biblioteca da Unifor</p>
            </div>

            <div className="form-field">
              <label htmlFor="slots-select">Número de Jogadores</label>
              <select id="slots-select" value={slots} onChange={(e) => setSlots(e.target.value)} required>
                {[2, 3, 4, 5, 6, 7, 8].map(num => (
                  <option key={num} value={num.toString()}>{num} jogadores</option>
                ))}
              </select>
            </div>

            <div className="form-field">
              <label htmlFor="party-description">Descrição</label>
              <textarea id="party-description" placeholder="Adicione informações extras..." value={description} onChange={(e) => setDescription(e.target.value)} rows={4} />
            </div>

            <div className="form-actions-row">
              <button type="button" className="btn-party-cancel" onClick={() => navigate(-1)}>Cancelar</button>
              <button type="submit" className="btn-party-submit" disabled={enviando}>
                {enviando ? 'Criando...' : "Criar Party's"}
              </button>
            </div>
          </form>
        </div>
      </main>
    </div>
  );
}
