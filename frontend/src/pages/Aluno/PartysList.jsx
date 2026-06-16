import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import partyService from '../../services/party.service';
import gameService from '../../services/game.service';
import { adaptGames, adaptParties } from '../../services/adapters';
import Loader from '../../components/Loader';

import '../../style/StylePages/StylePartysList.css';

export default function PartiesList() {
  const navigate = useNavigate();
  const [partiesList, setPartiesList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [erro, setErro] = useState('');

  const [requestedParties, setRequestedParties] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [selectedHost, setSelectedHost] = useState('');

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      try {
        const [openParties, games] = await Promise.all([
          partyService.listOpen(),
          gameService.listAvailable().catch(() => []),
        ]);
        const adaptedGames = adaptGames(Array.isArray(games) ? games : []);
        const gamesById = {};
        adaptedGames.forEach((g) => { gamesById[g.id] = g; });
        const adapted = adaptParties(Array.isArray(openParties) ? openParties : [], { gamesById });
        setPartiesList(adapted);
      } catch (err) {
        console.error("Erro ao carregar parties abertas:", err);
        setErro('Não foi possível carregar as parties disponíveis.');
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const handleJoinParty = async (partyId, hostName) => {
    if (requestedParties.includes(partyId)) return;
    try {
      await partyService.requestMembership(partyId);
      setRequestedParties((prev) => [...prev, partyId]);
      setSelectedHost(hostName);
      setShowModal(true);
    } catch (err) {
      console.error("Erro ao solicitar entrada:", err);
      const detail = err?.response?.data?.detail;
      alert(typeof detail === 'string' ? detail : 'Não foi possível solicitar entrada nesta party.');
    }
  };

  if (loading) {
    return <Loader />;
  }

  return (
    <div className="parties-list-wrapper">
      <header className="parties-list-header">
        <div className="parties-list-header-content">
          <div className="header-left-group">
            <button className="btn-icon-back" onClick={() => navigate(-1)}>
              <span className="material-symbols-outlined">arrow_back</span>
            </button>
            <div className="header-title-text">
              <h1>Party's Disponíveis</h1>
              <p className="sub-header-text">Encontre jogadores e organize suas partidas</p>
            </div>
          </div>

          <button className="btn-parties-create-new" onClick={() => navigate('/parties/create')}>
            <span className="material-symbols-outlined btn-icon-inner">add</span>
            Criar Party's
          </button>
        </div>
      </header>

      <main className="parties-list-main">
        {erro && <div className="auth-error-box" style={{ margin: '0 auto 16px', maxWidth: '600px' }}>{erro}</div>}
        <div className="parties-grid-container">
          {partiesList.map((party) => {
            const isRequested = requestedParties.includes(party.id);

            return (
              <div
                key={party.id}
                className={`party-glass-card ${isRequested ? 'party-card-disabled' : ''}`}
              >
                <div className="party-card-top-row">
                  <div className="party-title-block">
                    <h3>{party.gameName}</h3>
                    <span className="party-host-label">Organizado por {party.hostName}</span>
                  </div>
                  <div className="party-slots-badge">
                    <span className="material-symbols-outlined badge-icon">groups</span>
                    <span>{party.slots} vagas</span>
                  </div>
                </div>

                <p className="party-card-description">{party.description}</p>

                <div className="party-info-subgrid">
                  <div className="party-info-meta-item">
                    <span className="material-symbols-outlined meta-icon">calendar_month</span>
                    <span>{party.date ? new Date(party.date).toLocaleDateString('pt-BR') : '-'}</span>
                  </div>

                  <div className="party-info-meta-item">
                    <span className="material-symbols-outlined meta-icon">schedule</span>
                    <span>{party.time}</span>
                  </div>

                  <div className="party-info-meta-item col-span-2">
                    <span className="material-symbols-outlined meta-icon">location_on</span>
                    <span>{party.location}</span>
                  </div>
                </div>

                <button
                  className={`btn-party-action-detail ${isRequested ? 'btn-requested' : ''}`}
                  onClick={() => handleJoinParty(party.id, party.hostName)}
                  disabled={isRequested}
                >
                  {isRequested ? (
                    <>
                      <span className="material-symbols-outlined btn-inline-icon">hourglass_empty</span>
                      Aguardando Autorização...
                    </>
                  ) : (
                    'Participar'
                  )}
                </button>
              </div>
            );
          })}
        </div>

        {partiesList.length === 0 && !erro && (
          <div className="parties-empty-state">
            <span className="material-symbols-outlined empty-icon">inbox</span>
            <p>Nenhuma party's disponível no momento</p>
            <button className="btn-parties-create-new" onClick={() => navigate('/parties/create')}>
              Criar a primeira party's
            </button>
          </div>
        )}
      </main>

      {showModal && (
        <div className="party-modal-overlay" onClick={() => setShowModal(false)}>
          <div className="party-modal-card" onClick={(e) => e.stopPropagation()}>
            <div className="party-modal-icon-wrapper">
              <span className="material-symbols-outlined party-modal-success-icon">mark_email_read</span>
            </div>
            <h2>Solicitação Enviada!</h2>
            <p>
              Sua intenção de entrar na partida foi enviada diretamente para o responsável <strong>{selectedHost}</strong>.
            </p>
            <p className="party-modal-subtext">
              Por favor, aguarde a autorização dele para ter acesso completo aos dados de comunicação.
            </p>
            <button className="btn-party-modal-close" onClick={() => setShowModal(false)}>
              Entendido
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
