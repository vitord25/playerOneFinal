import React from 'react';
import Card from './Card';
import '../style/StyleComponents/GameGrid.css';

const GameGrid = ({ games }) => {
  if (games.length === 0) {
    return <p className="no-games-message">Nenhum jogo encontrado no catálogo.</p>;
  }

  return (
    <div className="games-grid">
      {games.map((game) => (
        // Usando o código único vindo do seu MER do Banco de Dados (CódigoÚnico)
        <Card key={game.codigoUnico || game.id} game={game} /> 
      ))}
    </div>
  );
};

export default GameGrid;