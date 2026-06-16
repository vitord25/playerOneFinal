import React, { useEffect, useState } from 'react';
import gameService from '../services/game.service';
import { adaptGames } from '../services/adapters';
import GameGrid from '../components/GameGrid';
import Loader from '../components/Loader';

import "../style/StylePages/StyleGlobal.css";
import "../style/StylePages/StyleHome.css";
import "../style/StyleComponents/Header.css";
import "../style/StyleComponents/Card.css";
import "../style/StyleComponents/GameGrid.css";

const Home = ({ searchQuery = '' }) => {
  const [games, setGames] = useState([]);
  const [loading, setLoading] = useState(true);
  const [erro, setErro] = useState('');

  useEffect(() => {
    const fetchGames = async () => {
      try {
        // Catálogo público: jogos disponíveis na ludoteca
        const response = await gameService.listAvailable();
        const adaptados = adaptGames(Array.isArray(response) ? response : []);
        const sorted = adaptados.sort((a, b) => a.nome.localeCompare(b.nome));
        setGames(sorted);
      } catch (error) {
        console.error("Erro ao buscar jogos da Ludoteca:", error);
        setErro('Não foi possível carregar o catálogo de jogos.');
      } finally {
        setLoading(false);
      }
    };
    fetchGames();
  }, []);

  const gamesToDisplay = games.filter(game =>
    game.nome.toLowerCase().includes(searchQuery.trim().toLowerCase())
  );

  return (
    <div className="home-page-container">
      <section className="hero-catalog">
        <h1>Catálogo de Jogos</h1>
        <p>Bem-vindo! Aproveite e reserve um jogo!</p>
      </section>

      {loading ? (
        <Loader />
      ) : erro ? (
        <p className="no-games-message">{erro}</p>
      ) : (
        <GameGrid games={gamesToDisplay} />
      )}
    </div>
  );
};

export default Home;
