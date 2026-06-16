import React from 'react';
import '../style/StyleComponents/Loader.css'; // Importando o CSS específico para o Loader

const Loader = () => {
  return (
    <div className="loader-container">
      <span className="loader"></span>
      
      <p className="loader-text">Embaralhando as cartas...</p>
    </div>
  );
};

export default Loader;