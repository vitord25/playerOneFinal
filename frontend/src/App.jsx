import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import Header from './components/Header';
import AppRoutes from './routes/PlayerOneAppRoutes';

// Componente auxiliar global que monta a estrutura da página
function MainLayout({ isDark, toggleDarkMode, searchQuery, setSearchQuery }) {
  const location = useLocation();

  // Rotas onde o Header/Footer NÃO devem aparecer (telas de auth e área admin)
  const noHeaderRoutes = ['/', '/cadastro'];
  const isAdminArea = location.pathname.startsWith('/admin');
  const showHeader = !noHeaderRoutes.includes(location.pathname) && !isAdminArea;

  return (
    <div className="app-container">
      {showHeader && (
        <Header
          toggleDarkMode={toggleDarkMode}
          isDark={isDark}
          searchQuery={searchQuery}
          setSearchQuery={setSearchQuery}
          showSearch={location.pathname === '/home'}
        />
      )}

      <main className="main-content">
        <AppRoutes searchQuery={searchQuery} />
      </main>

      {showHeader && (
        <footer className="main-footer" style={{ textAlign: 'center', padding: '20px 0', opacity: 0.7 }}>
          <p>© 2026 PLAYER ONE - Sistema de Gestão de Ludoteca UNIFOR</p>
        </footer>
      )}
    </div>
  );
}

function App() {
  const [searchQuery, setSearchQuery] = useState('');
  const [isDark, setIsDark] = useState(() => {
    const savedTheme = localStorage.getItem('theme');
    return savedTheme === 'dark';
  });

  const toggleDarkMode = () => {
    setIsDark((prev) => !prev);
  };

  useEffect(() => {
    const rootElement = document.documentElement;
    if (isDark) {
      rootElement.classList.add('dark');
      localStorage.setItem('theme', 'dark');
    } else {
      rootElement.classList.remove('dark');
      localStorage.setItem('theme', 'light');
    }
  }, [isDark]);

  return (
    <MainLayout
      isDark={isDark}
      toggleDarkMode={toggleDarkMode}
      searchQuery={searchQuery}
      setSearchQuery={setSearchQuery}
    />
  );
}

export default App;
