import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Plus, Pencil, Trash2, Users, Clock, CheckCircle2, XCircle } from 'lucide-react';
import gameService from '../../services/game.service';
import Loader from '../../components/Loader';
import '../../style/Admin/Admin.css';

const EMPTY_FORM = {
  name: '', description: '', category: '', minimum_age: 10,
  quantity: 1, min_players: 2, max_players: 4,
  min_duration_minutes: 30, max_duration_minutes: 60,
};

export default function ManageGames() {
  const navigate = useNavigate();
  const [games, setGames] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [showDelete, setShowDelete] = useState(false);
  const [mode, setMode] = useState('create');
  const [selected, setSelected] = useState(null);
  const [form, setForm] = useState(EMPTY_FORM);
  const [erro, setErro] = useState('');

  const load = async () => {
    setLoading(true);
    try {
      const data = await gameService.listAll();
      setGames(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error('Erro ao listar jogos:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const openCreate = () => {
    setMode('create');
    setForm(EMPTY_FORM);
    setErro('');
    setShowForm(true);
  };

  const openEdit = (game) => {
    setMode('edit');
    setSelected(game);
    setForm({
      name: game.name || '',
      description: game.description || '',
      category: game.category || '',
      minimum_age: game.minimum_age ?? 10,
      quantity: game.quantity ?? 1,
      min_players: game.min_players ?? 2,
      max_players: game.max_players ?? 4,
      min_duration_minutes: game.min_duration_minutes ?? 30,
      max_duration_minutes: game.max_duration_minutes ?? 60,
    });
    setErro('');
    setShowForm(true);
  };

  const handleChange = (field) => (e) => {
    const val = e.target.value;
    const numeric = ['minimum_age', 'quantity', 'min_players', 'max_players', 'min_duration_minutes', 'max_duration_minutes'];
    setForm((prev) => ({ ...prev, [field]: numeric.includes(field) ? Number(val) : val }));
  };

  const handleSave = async (e) => {
    e.preventDefault();
    setErro('');
    try {
      if (mode === 'create') {
        await gameService.create(form);
      } else {
        // GameUpdate aceita: name, description, quantity, available
        await gameService.update(selected.id, {
          name: form.name,
          description: form.description,
          quantity: form.quantity,
        });
      }
      setShowForm(false);
      await load();
    } catch (err) {
      console.error('Erro ao salvar jogo:', err);
      const detail = err?.response?.data?.detail;
      setErro(typeof detail === 'string' ? detail : 'Não foi possível salvar o jogo. Verifique os campos.');
    }
  };

  const handleToggle = async (game) => {
    try {
      await gameService.toggleAvailability(game.id);
      await load();
    } catch (err) {
      alert('Não foi possível alterar a disponibilidade.');
    }
  };

  const confirmDelete = (game) => {
    setSelected(game);
    setShowDelete(true);
  };

  const handleDelete = async () => {
    try {
      await gameService.delete(selected.id);
      setShowDelete(false);
      setSelected(null);
      await load();
    } catch (err) {
      alert('Não foi possível excluir o jogo.');
    }
  };

  if (loading) return <Loader />;

  return (
    <div className="admin-layout">
      <header className="admin-navbar">
        <div className="admin-navbar-inner">
          <div className="admin-brand">
            <button className="admin-btn admin-btn-ghost" onClick={() => navigate('/admin/dashboard')}>
              <ArrowLeft size={16} />
            </button>
            <div><h1>Gerenciar Jogos</h1></div>
          </div>
          <button className="admin-btn admin-btn-primary" onClick={openCreate}>
            <Plus size={16} /> Adicionar Jogo
          </button>
        </div>
      </header>

      <main className="admin-main">
        <div className="admin-toolbar">
          <span className="admin-count">{games.length} jogos cadastrados</span>
        </div>

        {games.length === 0 ? (
          <div className="admin-empty">Nenhum jogo cadastrado ainda.</div>
        ) : (
          <div className="admin-card-list">
            {games.map((game) => (
              <div key={game.id} className="admin-row-card">
                <div className="admin-row-main">
                  <div className="admin-row-title">
                    {game.name}
                    <span className="admin-tag tag-cat">{game.category}</span>
                    <span className="admin-tag tag-age">{game.minimum_age}+</span>
                    <span className={`admin-tag ${game.available ? 'tag-on' : 'tag-off'}`}>
                      {game.available ? <><CheckCircle2 size={12} /> Disponível</> : <><XCircle size={12} /> Indisponível</>}
                    </span>
                  </div>
                  <p className="admin-row-desc">{game.description}</p>
                  <div className="admin-row-meta">
                    <span><Users size={14} /> {game.min_players}-{game.max_players} jog.</span>
                    <span><Clock size={14} /> {game.min_duration_minutes}-{game.max_duration_minutes} min</span>
                    <span>Qtd: {game.quantity}</span>
                  </div>
                </div>
                <div className="admin-row-actions">
                  <button
                    className={`admin-btn ${game.available ? 'admin-btn-warning' : 'admin-btn-success'}`}
                    onClick={() => handleToggle(game)}
                  >
                    {game.available ? 'Marcar Indisponível' : 'Marcar Disponível'}
                  </button>
                  <button className="icon-btn edit" onClick={() => openEdit(game)}><Pencil size={16} /></button>
                  <button className="icon-btn delete" onClick={() => confirmDelete(game)}><Trash2 size={16} /></button>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>

      {showForm && (
        <div className="admin-modal-overlay" onClick={() => setShowForm(false)}>
          <form className="admin-modal" onClick={(e) => e.stopPropagation()} onSubmit={handleSave}>
            <h2>{mode === 'create' ? 'Adicionar Jogo' : 'Editar Jogo'}</h2>
            {erro && <div className="admin-error">{erro}</div>}

            <div className="admin-field">
              <label>Nome</label>
              <input value={form.name} onChange={handleChange('name')} required />
            </div>
            <div className="admin-field">
              <label>Descrição</label>
              <textarea rows={3} value={form.description} onChange={handleChange('description')} />
            </div>

            {mode === 'create' && (
              <>
                <div className="admin-grid-2">
                  <div className="admin-field">
                    <label>Categoria</label>
                    <input value={form.category} onChange={handleChange('category')} required />
                  </div>
                  <div className="admin-field">
                    <label>Idade mínima</label>
                    <input type="number" min="0" value={form.minimum_age} onChange={handleChange('minimum_age')} required />
                  </div>
                </div>
                <div className="admin-grid-2">
                  <div className="admin-field">
                    <label>Mín. jogadores</label>
                    <input type="number" min="1" value={form.min_players} onChange={handleChange('min_players')} required />
                  </div>
                  <div className="admin-field">
                    <label>Máx. jogadores</label>
                    <input type="number" min="1" value={form.max_players} onChange={handleChange('max_players')} required />
                  </div>
                </div>
                <div className="admin-grid-2">
                  <div className="admin-field">
                    <label>Duração mín. (min)</label>
                    <input type="number" min="1" value={form.min_duration_minutes} onChange={handleChange('min_duration_minutes')} required />
                  </div>
                  <div className="admin-field">
                    <label>Duração máx. (min)</label>
                    <input type="number" min="1" value={form.max_duration_minutes} onChange={handleChange('max_duration_minutes')} required />
                  </div>
                </div>
              </>
            )}

            <div className="admin-field">
              <label>Quantidade de cópias</label>
              <input type="number" min="1" value={form.quantity} onChange={handleChange('quantity')} required />
            </div>

            <div className="admin-modal-actions">
              <button type="button" className="admin-btn admin-btn-ghost" onClick={() => setShowForm(false)}>Cancelar</button>
              <button type="submit" className="admin-btn admin-btn-primary">Salvar</button>
            </div>
          </form>
        </div>
      )}

      {showDelete && (
        <div className="admin-modal-overlay" onClick={() => setShowDelete(false)}>
          <div className="admin-modal" onClick={(e) => e.stopPropagation()}>
            <h2>Excluir jogo</h2>
            <p style={{ color: '#b9c0d4' }}>
              Tem certeza que deseja excluir <strong>{selected?.name}</strong>? Esta ação removerá também as party's associadas.
            </p>
            <div className="admin-modal-actions">
              <button className="admin-btn admin-btn-ghost" onClick={() => setShowDelete(false)}>Cancelar</button>
              <button className="admin-btn admin-btn-danger" onClick={handleDelete}>Excluir</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
