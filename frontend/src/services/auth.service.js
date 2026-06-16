import api from './api.js';

const authService = {
  // Registrar novo usuário
  register: async (userData) => {
    const response = await api.post('/api/v1/auth/register', userData);
    return response.data;
  },

  // Autenticar e obter JWT (Formato obrigatório do FastAPI)
  login: async (username, password) => {
    const params = new URLSearchParams();
    params.append('username', username);
    params.append('password', password);

    const response = await api.post('/api/v1/auth/login', params, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    
    if (response.data.access_token) {
      localStorage.setItem('access_token', response.data.access_token);
    }
    return response.data;
  },

  // Encerrar sessão
  logout: async () => {
    try {
      await api.post('/api/v1/auth/logout');
    } finally {
      localStorage.removeItem('access_token');
    }
  },

  // Obter usuário autenticado corrente (Contexto do Auth)
  getMe: async () => {
    const response = await api.get('/api/v1/auth/me');
    return response.data;
  },
};

export default authService;