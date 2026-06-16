import React, { useEffect } from 'react';
import { Link } from 'react-router-dom';
import '../style/StylePages/StyleGlobal.css';
import SearchBar from './SearchBar';
import '../style/StyleComponents/Header.css';
import iconLogo from '../imgs/IconeDado.png';

const Header = ({ toggleDarkMode, isDark, searchQuery, setSearchQuery, showSearch = true }) => {
  
  // Efeito colateral sênior que escuta o estado 'isDark' e altera o nó raiz da árvore do DOM (<html>)
  useEffect(() => {
    const rootElement = document.documentElement;
    if (isDark) {
      rootElement.classList.add('dark');
    } else {
      rootElement.classList.remove('dark');
    }
  }, [isDark]);

  return (
    <header className="main-header">
      <div className="header-content">

        {/* SEÇÃO ESQUERDA: LOGO */}
        <div className="header-section left">
          <Link to="/home" className="logo-link" title="Ir para a Home">
            <div className="logo-icon-box">
              <img src={iconLogo} alt="Player One Logo" className="logo-img" />
            </div>
            <span className="logo-text">Player One</span>
          </Link>
        </div>

        {/* SEÇÃO CENTRAL: BARRA DE PESQUISA */}
        <div className="header-section center">
          {showSearch && (
            <SearchBar searchQuery={searchQuery} setSearchQuery={setSearchQuery} />
          )}
        </div>

        {/* SEÇÃO DIREITA: BOTÕES DE AÇÃO */}
        <div className="header-section right">
          
          {/* 🌟 ÍCONE DE FESTA/CONFITE (MINHAS RESERVAS) DIRECIONANDO PARA MY PARTIES */}
          <Link to="/parties/my" className="header-icon-btn" title="Minhas Reservas">
            <div className="icon-wrapper">
              {/* Ícone de Festa Nativo do Material Symbols alinhado com o seu Design System */}
              <span className="material-symbols-outlined svg-icon" style={{ fontSize: '24px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                celebration
              </span>
              {/* Mantém o ponto vermelho indicador de solicitações pendentes */}
              <span className="notification-dot"></span>
            </div>
          </Link>
          
          {/* ÍCONE DE PERFIL */}
          <Link to="/perfil" className="header-icon-btn" title="Meu Perfil">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth="1.6" stroke="currentColor" className="svg-icon">
              <path strokeLinecap="round" strokeLinejoin="round" d="M17.982 18.725A7.488 7.488 0 0 0 12 15.75a7.488 7.488 0 0 0-5.982 2.975m11.963 0a9 9 0 1 0-11.963 0m11.963 0A8.966 8.966 0 0 1 12 21a8.966 8.966 0 0 1-5.982-2.275M15 9.75a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" />
            </svg>
          </Link>

          {/* ALTERNADOR DE TEMA ESCURO/CLARO */}
          <button onClick={toggleDarkMode} className="theme-toggle-btn" title="Alternar Tema">
            {isDark ? '☀️' : '🌙'}
          </button>
        </div>

      </div>
    </header>
  );
};

export default Header;