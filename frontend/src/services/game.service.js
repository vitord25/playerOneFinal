import api from './api.js';

const gameService = {
  // Listar todos os jogos (Admin)
  listAll: async () => {
    const response = await api.get('/api/v1/games/');
    return response.data;
  },

  // Cadastrar novo jogo (Admin)
  create: async (gameData) => {
    const response = await api.post('/api/v1/games/', gameData);
    return response.data;
  },

  // Listar jogos disponíveis para o público/membros
  listAvailable: async () => {
    const response = await api.get('/api/v1/games/available');
    return response.data;
  },

  // Buscar jogo por ID
  getById: async (gameId) => {
    const response = await api.get(`/api/v1/games/${gameId}`);
    return response.data;
  },

  // Atualizar dados do jogo (Admin)
  update: async (gameId, gameData) => {
    const response = await api.patch(`/api/v1/games/${gameId}`, gameData);
    return response.data;
  },

  // Deletar jogo (Admin)
  delete: async (gameId) => {
    await api.delete(`/api/v1/games/${gameId}`);
  },

  // Bloquear / desbloquear jogo (Admin)
  toggleAvailability: async (gameId) => {
    const response = await api.patch(`/api/v1/games/${gameId}/availability`);
    return response.data;
  },
};

export default gameService;