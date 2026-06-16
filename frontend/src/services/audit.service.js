import api from './api.js';

const auditService = {
  // Listar logs gerais com filtros avançados (Admin)
  listLogs: async (filters = {}) => {
    // filters pode conter: entity, entity_id, action, user_id, date_from, date_to, skip, limit
    const response = await api.get('/api/v1/audit/', {
      params: filters,
    });
    return response.data;
  },

  // Histórico específico de uma entidade (Admin)
  getEntityHistory: async (entity, entityId) => {
    const response = await api.get(`/api/v1/audit/entity/${entity}/${entityId}`);
    return response.data;
  },
};

export default auditService;