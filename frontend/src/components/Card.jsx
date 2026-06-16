import React from 'react';
import { Link } from 'react-router-dom';
import '../style/StyleComponents/Card.css';

// ❌ REMOVIDO: import Detail de páginas para não dar conflito

const Card = ({ game }) => {
  const isUnavailable = game.statusJogo === 'INDISPONIVEL' || game.indisponivel;

  return (
    // ✨ CORRIGIDO: Agora aponta para "/jogo/id", batendo exatamente com a rota configurada!
    // Usamos game.id para casar perfeitamente com a busca por ID (g.id === Number(id)) no jogoService mockado.
    <Link to={`/jogo/${game.id}`} className="game-card">
      {isUnavailable && (
        <span className="badge-unavailable">Indisponível</span>
      )}
      
      <img 
        src={game.imagemUrl || 'https://via.placeholder.com/300x400'} 
        alt={game.nome} 
        className="game-card-img" 
      />
      
      <div className="game-card-overlay">
        <h3 className="game-card-title">{game.nome.toUpperCase()}</h3>
      </div>
    </Link>
  );
};

export default Card;