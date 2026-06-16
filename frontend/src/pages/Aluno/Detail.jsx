import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import gameService from '../../services/game.service';
import { adaptGame } from '../../services/adapters';
import { useAuth } from '../../context/AuthContext';
import Loader from '../../components/Loader';

import '../../style/StylePages/StyleDetail.css';

const Detail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { isAdmin } = useAuth();
  const [game, setGame] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!id) return;
    setLoading(true);

    gameService.getById(id)
      .then((res) => {
        setGame(adaptGame(res));
      })
      .catch((err) => {
        console.error("Erro ao carregar detalhes do jogo:", err);
        setGame(null);
      })
      .finally(() => {
        setLoading(false);
      });
  }, [id]);

  if (loading) return <Loader />;

  if (!game) {
    return (
      <div className="detail-page-wrapper">
        <div className="detail-card-panel" style={{ textAlign: 'center', maxWidth: '450px' }}>
          <h2 style={{ marginBottom: '12px', color: '#090d16' }}>Jogo não encontrado</h2>
          <button className="detail-btn-primary" onClick={() => navigate('/home')}>
            Voltar ao Catálogo
          </button>
        </div>
      </div>
    );
  }

  const isAvailable = game.disponivel;
  const playersCount = game.minJogadores && game.maxJogadores
    ? `${game.minJogadores}-${game.maxJogadores}`
    : 'N/A';
  const quantidade = game.quantidadeDisponivel ?? 0;

  return (
    <div className="detail-page-wrapper">
      <div className="detail-bg-banner" style={{ backgroundImage: `url(${game.imagemUrl})` }} />
      <div className="detail-bg-overlay" />

      <button className="detail-btn-back" onClick={() => navigate(-1)}>←</button>

      <div className="detail-card-panel">
        <header className="detail-main-header">
          <div className="detail-title-group">
            <h1>{game.nome}</h1>
            <div className="detail-badges-row">
              <span className="detail-badge-tag">{game.categoria || 'Estratégia'}</span>
              <span className="detail-badge-tag outline">{game.faixaEtaria || '10+'}</span>
            </div>
          </div>

          <div>
            {isAvailable && quantidade > 0 ? (
              <div className="detail-status-indicator available">
                <span className="detail-status-icon">✓</span>
                <div className="detail-status-info-box">
                  <span className="detail-status-label">Disponíveis</span>
                  <span className="detail-status-qty">{quantidade}</span>
                </div>
              </div>
            ) : (
              <div className="detail-status-indicator unavailable">
                <span className="detail-status-icon">✕</span>
                <div className="detail-status-info-box">
                  <span className="detail-status-label">Status</span>
                  <span className="detail-status-qty">Indisponível</span>
                </div>
              </div>
            )}
          </div>
        </header>

        <section className="detail-attributes-grid">
          <div className="detail-attr-item">
            <div className="detail-attr-icon-box">👥</div>
            <div className="detail-attr-text-box">
              <p className="detail-attr-label">Jogadores</p>
              <p className="detail-attr-value">{playersCount} jog.</p>
            </div>
          </div>

          <div className="detail-attr-item">
            <div className="detail-attr-icon-box">🕒</div>
            <div className="detail-attr-text-box">
              <p className="detail-attr-label">Duração</p>
              <p className="detail-attr-value">{game.duracao || '60 min'}</p>
            </div>
          </div>

          <div className="detail-attr-item">
            <div className="detail-attr-icon-box">📅</div>
            <div className="detail-attr-text-box">
              <p className="detail-attr-label">Idade</p>
              <p className="detail-attr-value">{game.faixaEtaria || '10+'}</p>
            </div>
          </div>
        </section>

        <section className="detail-description-section">
          <h2>Descrição</h2>
          <p>{game.descricao}</p>
        </section>

        <footer className="detail-actions-footer">
          {/* Apenas alunos (USER) podem criar parties — admins gerenciam */}
          {!isAdmin && (
            <button
              className="detail-btn-primary"
              disabled={!isAvailable || quantidade === 0}
              onClick={() => navigate('/parties/create', { state: { gameId: game.id } })}
            >
              Criar Party's
            </button>
          )}
          <button className="detail-btn-secondary" onClick={() => navigate('/parties')}>
            Ver Party's
          </button>
        </footer>
      </div>
    </div>
  );
};

export default Detail;
