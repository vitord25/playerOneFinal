import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, ShieldCheck, ShieldOff, UserCheck, UserX, Pencil, Save, XCircle } from 'lucide-react';
import userService from '../../services/user.service';
import { useAuth } from '../../context/AuthContext';
import Loader from '../../components/Loader';
import '../../style/Admin/Admin.css';

export default function ManageUsers() {
  const navigate = useNavigate();
  const { user: currentUser } = useAuth();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(null); // usuário em edição
  const [form, setForm] = useState({ name: '', email: '', role: 'USER', active: true });
  const [saving, setSaving] = useState(false);
  const [editError, setEditError] = useState('');

  const load = async () => {
    setLoading(true);
    try {
      const data = await userService.listAll();
      setUsers(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error('Erro ao listar usuários:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const getInitials = (name) =>
    (name || '?').split(' ').map((n) => n[0]).join('').toUpperCase().slice(0, 2);

  const handleToggleRole = async (u) => {
    const newRole = u.role === 'ADMIN' ? 'USER' : 'ADMIN';
    try {
      await userService.changeRole(u.id, { role: newRole });
      await load();
    } catch (err) {
      const detail = err?.response?.data?.detail;
      alert(typeof detail === 'string' ? detail : 'Não foi possível alterar o papel do usuário.');
    }
  };

  const handleToggleActive = async (u) => {
    try {
      if (u.active) {
        await userService.deactivate(u.id);
      } else {
        await userService.reactivate(u.id);
      }
      await load();
    } catch (err) {
      alert('Não foi possível alterar o status do usuário.');
    }
  };

  const openEdit = (u) => {
    setEditError('');
    setEditing(u);
    setForm({
      name: u.name || '',
      email: u.email || '',
      role: u.role || 'USER',
      active: !!u.active,
    });
  };

  const closeEdit = () => {
    setEditing(null);
    setEditError('');
  };

  const handleFormChange = (field, value) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const saveEdit = async () => {
    if (!editing) return;
    if (!form.name.trim() || !form.email.trim()) {
      setEditError('Nome e e-mail são obrigatórios.');
      return;
    }
    setSaving(true);
    setEditError('');
    try {
      await userService.adminUpdateUser(editing.id, {
        name: form.name.trim(),
        email: form.email.trim(),
        role: form.role,
        active: form.active,
      });
      await load();
      closeEdit();
    } catch (err) {
      const detail = err?.response?.data?.detail;
      setEditError(typeof detail === 'string' ? detail : 'Não foi possível salvar as alterações.');
    } finally {
      setSaving(false);
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
            <div><h1>Gerenciar Usuários</h1></div>
          </div>
        </div>
      </header>

      <main className="admin-main">
        <div className="admin-toolbar">
          <span className="admin-count">{users.length} usuários cadastrados</span>
        </div>

        {users.length === 0 ? (
          <div className="admin-empty">Nenhum usuário encontrado.</div>
        ) : (
          <div className="admin-card-list">
            {users.map((u) => (
              <div key={u.id} className="admin-row-card">
                <div className="admin-avatar-mini">
                  {u.profile_image_url ? <img src={u.profile_image_url} alt={u.name} /> : getInitials(u.name)}
                </div>
                <div className="admin-row-main">
                  <div className="admin-row-title">
                    {u.name}
                    <span className={`admin-tag ${u.role === 'ADMIN' ? 'tag-cat' : 'tag-age'}`}>{u.role}</span>
                    <span className={`admin-tag ${u.active ? 'tag-on' : 'tag-off'}`}>{u.active ? 'Ativo' : 'Inativo'}</span>
                  </div>
                  <p className="admin-row-desc">{u.email}</p>
                </div>
                <div className="admin-row-actions">
                  <button
                    className="admin-btn admin-btn-ghost"
                    onClick={() => openEdit(u)}
                    title="Editar dados do usuário"
                  >
                    <Pencil size={15} /> Editar
                  </button>
                  <button
                    className="admin-btn admin-btn-ghost"
                    disabled={currentUser?.id === u.id}
                    onClick={() => handleToggleRole(u)}
                    title={u.role === 'ADMIN' ? 'Rebaixar para usuário' : 'Promover a admin'}
                  >
                    {u.role === 'ADMIN' ? <><ShieldOff size={15} /> Tornar Usuário</> : <><ShieldCheck size={15} /> Tornar Admin</>}
                  </button>
                  <button
                    className={`admin-btn ${u.active ? 'admin-btn-danger' : 'admin-btn-success'}`}
                    disabled={currentUser?.id === u.id}
                    onClick={() => handleToggleActive(u)}
                  >
                    {u.active ? <><UserX size={15} /> Desativar</> : <><UserCheck size={15} /> Reativar</>}
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>

      {editing && (
        <div className="admin-modal-overlay" onClick={closeEdit}>
          <div className="admin-modal" onClick={(e) => e.stopPropagation()}>
            <div className="admin-modal-header">
              <h2>Editar Usuário</h2>
              <button className="admin-btn admin-btn-ghost" onClick={closeEdit}>
                <XCircle size={18} />
              </button>
            </div>

            <div className="admin-modal-body">
              <label className="admin-field">
                <span>Nome</span>
                <input
                  type="text"
                  value={form.name}
                  onChange={(e) => handleFormChange('name', e.target.value)}
                  placeholder="Nome do usuário"
                />
              </label>

              <label className="admin-field">
                <span>E-mail</span>
                <input
                  type="email"
                  value={form.email}
                  onChange={(e) => handleFormChange('email', e.target.value)}
                  placeholder="email@exemplo.com"
                />
              </label>

              <label className="admin-field">
                <span>Papel</span>
                <select
                  value={form.role}
                  onChange={(e) => handleFormChange('role', e.target.value)}
                >
                  <option value="USER">USER</option>
                  <option value="ADMIN">ADMIN</option>
                </select>
              </label>

              <label className="admin-field admin-field-inline">
                <input
                  type="checkbox"
                  checked={form.active}
                  onChange={(e) => handleFormChange('active', e.target.checked)}
                />
                <span>Usuário ativo</span>
              </label>

              {editError && <div className="admin-modal-error">{editError}</div>}
            </div>

            <div className="admin-modal-footer">
              <button className="admin-btn admin-btn-ghost" onClick={closeEdit} disabled={saving}>
                <XCircle size={15} /> Cancelar
              </button>
              <button className="admin-btn admin-btn-success" onClick={saveEdit} disabled={saving}>
                <Save size={15} /> {saving ? 'Salvando...' : 'Salvar'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
