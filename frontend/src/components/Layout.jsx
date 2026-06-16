import React from 'react';
import Header from './Header'; 
import '../style/StylePages/StyleGlobal.css'; 

const Layout = ({ children, toggleDarkMode, isDark, searchQuery, setSearchQuery }) => {
  return (
    <div className="app-container">
      
      <Header 
        toggleDarkMode={toggleDarkMode} 
        isDark={isDark} 
        searchQuery={searchQuery} 
        setSearchQuery={setSearchQuery} 
      />

      <main className="main-content">
        {children}
      </main>

      <footer className="main-footer">
        <p>© 2026 PLAYER ONE - Sistema de Gestão de Ludoteca UNIFOR</p>
      </footer>
    </div>
  );
};

export default Layout;