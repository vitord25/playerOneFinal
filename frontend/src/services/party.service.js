import api from './api.js';

const partyService = {
  // ==========================================
  // PARTIES
  // ==========================================
  listAll: async () => {
    const response = await api.get('/api/v1/parties/');
    return response.data;
  },

  create: async (partyData) => {
    const response = await api.post('/api/v1/parties/', partyData);
    return response.data;
  },

  listOpen: async () => {
    const response = await api.get('/api/v1/parties/open');
    return response.data;
  },

  listMyParties: async () => {
    const response = await api.get('/api/v1/parties/my');
    return response.data;
  },

  getById: async (partyId) => {
    const response = await api.get(`/api/v1/parties/${partyId}`);
    return response.data;
  },

  update: async (partyId, partyData) => {
    const response = await api.patch(`/api/v1/parties/${partyId}`, partyData);
    return response.data;
  },

  delete: async (partyId) => {
    await api.delete(`/api/v1/parties/${partyId}`);
  },

  approveParty: async (partyId) => {
    const response = await api.patch(`/api/v1/parties/${partyId}/approve`);
    return response.data;
  },

  rejectParty: async (partyId) => {
    const response = await api.patch(`/api/v1/parties/${partyId}/reject`);
    return response.data;
  },

  cancelParty: async (partyId) => {
    const response = await api.patch(`/api/v1/parties/${partyId}/cancel`);
    return response.data;
  },

  // ==========================================
  // PARTY MEMBERS (Membros da Party)
  // ==========================================
  requestMembership: async (partyId) => {
    const response = await api.post(`/api/v1/parties/${partyId}/members`);
    return response.data;
  },

  listMembers: async (partyId) => {
    const response = await api.get(`/api/v1/parties/${partyId}/members`);
    return response.data;
  },

  approveMember: async (partyId, memberId) => {
    const response = await api.patch(`/api/v1/parties/${partyId}/members/${memberId}/approve`);
    return response.data;
  },

  rejectMember: async (partyId, memberId) => {
    const response = await api.patch(`/api/v1/parties/${partyId}/members/${memberId}/reject`);
    return response.data;
  },

  leaveParty: async (partyId) => {
    await api.delete(`/api/v1/parties/${partyId}/members/me`);
  },

  removeMember: async (partyId, memberId) => {
    await api.delete(`/api/v1/parties/${partyId}/members/${memberId}`);
  },

  // ==========================================
  // MESSAGES (Chat da Party)
  // ==========================================
  sendMessage: async (partyId, messageData) => {
    const response = await api.post(`/api/v1/parties/${partyId}/messages`, messageData);
    return response.data;
  },

  listMessages: async (partyId, skip = 0, limit = 100) => {
    const response = await api.get(`/api/v1/parties/${partyId}/messages`, {
      params: { skip, limit },
    });
    return response.data;
  },

  deleteMessage: async (partyId, messageId) => {
    await api.delete(`/api/v1/parties/${partyId}/messages/${messageId}`);
  },
};

export default partyService;