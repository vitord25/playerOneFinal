import api from './api.js';

const userService = {
  // Listar todos os usuários (Admin)
  listAll: async () => {
    const response = await api.get('/api/v1/users/');
    return response.data;
  },

  // Listar usuários ativos (Admin)
  listActive: async () => {
    const response = await api.get('/api/v1/users/active');
    return response.data;
  },

  // Obter perfil do usuário autenticado
  getProfile: async () => {
    const response = await api.get('/api/v1/users/me');
    return response.data;
  },

  // Atualizar próprio perfil
  updateProfile: async (profileData) => {
    const response = await api.patch('/api/v1/users/me', profileData);
    return response.data;
  },

  // Buscar usuário por ID (Admin)
  getById: async (userId) => {
    const response = await api.get(`/api/v1/users/${userId}`);
    return response.data;
  },

  // Desativar usuário (Soft Delete - Admin)
  deactivate: async (userId) => {
    const response = await api.delete(`/api/v1/users/${userId}`);
    return response.data;
  },

  // Alterar própria senha
  changePassword: async (passwordData) => {
    await api.patch('/api/v1/users/me/password', passwordData);
  },

  // Alterar role de usuário (Admin)
  changeRole: async (userId, roleData) => {
    const response = await api.patch(`/api/v1/users/${userId}/role`, roleData);
    return response.data;
  },

  // UC09 - Admin edita dados de um usuário (nome, e-mail, role, status, etc.)
  adminUpdateUser: async (userId, userData) => {
    const response = await api.patch(`/api/v1/users/${userId}`, userData);
    return response.data;
  },

  // Reativar usuário (Admin)
  reactivate: async (userId) => {
    const response = await api.patch(`/api/v1/users/${userId}/reactivate`);
    return response.data;
  },
};

export default userService;