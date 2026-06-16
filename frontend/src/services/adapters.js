// ============================================================================
// Adapters — convertem o formato do backend (FastAPI/Ludoteca) para o formato
// esperado pela UI (que foi originalmente construída com dados mockados em PT).
// Centralizar essa tradução evita espalhar mapeamentos pelo código das telas.
// ============================================================================

// Imagem padrão por categoria (o backend não armazena URL de imagem).
const DEFAULT_GAME_IMAGE =
  'https://images.unsplash.com/photo-1610890716171-6b1bb98ffd09?q=80&w=600&auto=format&fit=crop';

const CATEGORY_IMAGES = {
  'estratégia': 'https://images.unsplash.com/photo-1611371805429-8b5c1b2c34ba?q=80&w=600&auto=format&fit=crop',
  'rpg': 'https://images.unsplash.com/photo-1605870445919-838d190e8e1b?q=80&w=600&auto=format&fit=crop',
  'card game': 'https://images.unsplash.com/photo-1606167668584-78701c57f13d?q=80&w=600&auto=format&fit=crop',
  'cooperativo': 'https://images.unsplash.com/photo-1632501641765-e568d28b0015?q=80&w=600&auto=format&fit=crop',
  'familiar': 'https://images.unsplash.com/photo-1563986768609-322da13575f3?q=80&w=600&auto=format&fit=crop',
};

export function pickGameImage(category) {
  if (!category) return DEFAULT_GAME_IMAGE;
  const key = String(category).toLowerCase();
  return CATEGORY_IMAGES[key] || DEFAULT_GAME_IMAGE;
}

// Backend Game -> UI Game
export function adaptGame(g) {
  if (!g) return null;
  const duracao =
    g.min_duration_minutes && g.max_duration_minutes
      ? `${g.min_duration_minutes} a ${g.max_duration_minutes} min`
      : 'N/A';
  return {
    id: g.id,
    codigoUnico: `JOG-${String(g.id).padStart(3, '0')}`,
    nome: g.name,
    imagemUrl: pickGameImage(g.category),
    statusJogo: g.available ? 'DISPONIVEL' : 'INDISPONIVEL',
    disponivel: g.available,
    indisponivel: !g.available,
    categoria: g.category,
    faixaEtaria: g.minimum_age != null ? `${g.minimum_age}+` : 'N/A',
    minJogadores: g.min_players,
    maxJogadores: g.max_players,
    duracao,
    quantidadeDisponivel: g.quantity ?? 0,
    descricao: g.description || 'Nenhuma descrição fornecida.',
    // mantém os campos crus para telas administrativas
    _raw: g,
  };
}

export function adaptGames(list = []) {
  return list.map(adaptGame);
}

// Backend Party -> UI Party (enriquecida opcionalmente com nome do jogo/organizador)
export function adaptParty(p, { gamesById = {}, usersById = {}, membersCount } = {}) {
  if (!p) return null;
  const game = gamesById[p.game_id];
  const organizer = usersById[p.organizer_id];
  return {
    id: p.id,
    gameId: p.game_id,
    gameName: game ? game.nome || game.name : `Jogo #${p.game_id}`,
    organizerId: p.organizer_id,
    hostName: organizer ? organizer.name : `Usuário #${p.organizer_id}`,
    description: p.description,
    date: p.date,
    time: p.time,
    location: p.location,
    slots: p.max_players,
    currentPlayers: membersCount != null ? membersCount : undefined,
    status: (p.status || '').toLowerCase(),
    statusRaw: p.status,
    _raw: p,
  };
}

export function adaptParties(list = [], opts = {}) {
  return list.map((p) => adaptParty(p, opts));
}
