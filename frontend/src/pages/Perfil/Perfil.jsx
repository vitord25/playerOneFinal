import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import userService from '../../services/user.service';

import '../../style/StylePages/StylePerfil.css';

export default function Profile() {
  const navigate = useNavigate();
  const fileInputRef = useRef(null);
  const { user, setUser, logout, isAdmin } = useAuth();

  const [name, setName] = useState('');
  const [bio, setBio] = useState('');
  const [editing, setEditing] = useState(false);
  const [avatarPreview, setAvatarPreview] = useState('');
  const [salvando, setSalvando] = useState(false);

  useEffect(() => {
    if (user) {
      setName(user.name || '');
      setBio(user.description || '');
      setAvatarPreview(user.profile_image_url || '');
    }
  }, [user]);

  if (!user) {
    return null;
  }

  const handleSave = async () => {
    setSalvando(true);
    try {
      const updated = await userService.updateProfile({
        name,
        description: bio,
        profile_image_url: avatarPreview || null,
      });
      setUser(updated);
      setEditing(false);
    } catch (err) {
      console.error('Erro ao salvar perfil:', err);
      alert('Não foi possível salvar as alterações.');
    } finally {
      setSalvando(false);
    }
  };

  const handleLogout = async () => {
    await logout();
    navigate('/');
  };

  const handleAvatarClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => setAvatarPreview(reader.result);
      reader.readAsDataURL(file);
    }
  };

  const userNameFallback = name || user?.name || 'Jogador';
  const initials = userNameFallback
    .split(' ')
    .filter(Boolean)
    .map(n => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);

  return (
    <div className="profile-page-wrapper">
      <header className="profile-sticky-header">
        <div className="profile-header-container">
          <div className="profile-header-left">
            <button type="button" className="btn-profile-icon-back" onClick={() => navigate(-1)}>
              <span className="material-symbols-outlined">arrow_back</span>
            </button>
            <h1 className="profile-main-title">Perfil</h1>
          </div>

          <button type="button" className="btn-profile-logout" onClick={handleLogout}>
            <span className="material-symbols-outlined">logout</span> Sair
          </button>
        </div>
      </header>

      <main className="profile-main-content">
        <div className="profile-card-box">

          <div className="profile-avatar-center-section">
            <div className="profile-avatar-interactive-group">
              {avatarPreview ? (
                <img src={avatarPreview} alt={userNameFallback} className="profile-img-avatar" />
              ) : (
                <div className="profile-avatar-fallback-box">{initials}</div>
              )}

              <button type="button" onClick={handleAvatarClick} className="btn-profile-camera-overlay" title="Alterar foto de perfil">
                <span className="material-symbols-outlined">photo_camera</span>
              </button>
            </div>

            <input ref={fileInputRef} type="file" accept="image/*" onChange={handleFileChange} className="profile-hidden-file-input" />

            {!editing && (
              <div className="profile-text-identity-summary">
                <h2 className="profile-user-display-name">{userNameFallback}</h2>
                <p className="profile-user-display-email">
                  <span className="material-symbols-outlined">alternate_email</span>
                  {user.email || 'usuario@unifor.br'}
                </p>
                {isAdmin && <span className="host-indicator-badge" style={{ marginTop: 8 }}>Administrador</span>}
                {bio && <p className="profile-user-display-bio">{bio}</p>}
              </div>
            )}
          </div>

          {editing ? (
            <div className="profile-inputs-form-stack">
              <div className="profile-form-field">
                <label htmlFor="form-profile-name">Nome</label>
                <input id="form-profile-name" type="text" value={name} onChange={(e) => setName(e.target.value)} placeholder="Seu nome completo" className="profile-native-input" />
              </div>

              <div className="profile-form-field">
                <label htmlFor="form-profile-bio">Biografia</label>
                <textarea id="form-profile-bio" value={bio} onChange={(e) => setBio(e.target.value)} placeholder="Conte um pouco sobre você..." rows={4} className="profile-native-textarea" />
              </div>

              <div className="profile-form-actions-row">
                <button
                  type="button"
                  className="btn-profile-form-action variant-cancel"
                  onClick={() => {
                    setName(user.name || '');
                    setBio(user.description || '');
                    setAvatarPreview(user.profile_image_url || '');
                    setEditing(false);
                  }}
                >
                  Cancelar
                </button>
                <button type="button" className="btn-profile-form-action variant-save" onClick={handleSave} disabled={salvando}>
                  <span className="material-symbols-outlined">save</span> {salvando ? 'Salvando...' : 'Salvar'}
                </button>
              </div>
            </div>
          ) : (
            <div className="profile-static-details-stack">
              <button type="button" className="btn-profile-trigger-edit" onClick={() => setEditing(true)}>
                <span className="material-symbols-outlined">edit</span> Editar Perfil
              </button>

              {isAdmin && (
                <button type="button" className="btn-profile-trigger-edit" style={{ marginTop: 12 }} onClick={() => navigate('/admin/dashboard')}>
                  <span className="material-symbols-outlined">admin_panel_settings</span> Painel Administrativo
                </button>
              )}
            </div>
          )}

        </div>
      </main>
    </div>
  );
}
