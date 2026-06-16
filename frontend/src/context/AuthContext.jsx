import React, { createContext, useContext, useEffect, useState } from 'react';
import authService from '../services/auth.service';

// ============================================================================
// Contexto de Autenticação — centraliza o estado do usuário logado, o token
// JWT e as funções de login/logout/registro consumindo o backend real.
// ============================================================================
const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Ao montar, se houver token salvo, recupera o usuário corrente
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      setLoading(false);
      return;
    }
    authService
      .getMe()
      .then((me) => setUser(me))
      .catch(() => {
        localStorage.removeItem('access_token');
        setUser(null);
      })
      .finally(() => setLoading(false));
  }, []);

  // Login: autentica (email/senha), salva token e carrega o usuário
  const login = async (email, password) => {
    await authService.login(email, password);
    const me = await authService.getMe();
    setUser(me);
    return me;
  };

  // Registro de novo usuário (sempre nasce como USER no backend)
  const register = async (payload) => {
    return authService.register(payload);
  };

  const logout = async () => {
    try {
      await authService.logout();
    } catch (_) {
      // ignora erros de logout (token pode já ter expirado)
    } finally {
      localStorage.removeItem('access_token');
      setUser(null);
    }
  };

  const refreshUser = async () => {
    const me = await authService.getMe();
    setUser(me);
    return me;
  };

  const isAuthenticated = !!user;
  const isAdmin = user?.role === 'ADMIN';

  return (
    <AuthContext.Provider
      value={{
        user,
        setUser,
        loading,
        login,
        register,
        logout,
        refreshUser,
        isAuthenticated,
        isAdmin,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error('useAuth deve ser usado dentro de <AuthProvider>');
  }
  return ctx;
}

export default AuthContext;
