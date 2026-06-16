import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import '../../style/StyleRegister/Auth.css';
import { useAuth } from '../../context/AuthContext';
import loginImg from '../../imgs/LoginImage.png';
import iconLogo from '../../imgs/IconeDado.png';

const Login = () => {
  const navigate = useNavigate();
  const { login } = useAuth();

  const [email, setEmail] = useState('');
  const [senha, setSenha] = useState('');
  const [erro, setErro] = useState('');
  const [carregando, setCarregando] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    setErro('');
    setCarregando(true);
    try {
      const me = await login(email, senha);
      // Redireciona conforme o papel do usuário
      if (me?.role === 'ADMIN') {
        navigate('/admin/dashboard');
      } else {
        navigate('/home');
      }
    } catch (err) {
      const status = err?.response?.status;
      if (status === 401) {
        setErro('E-mail ou senha inválidos.');
      } else {
        setErro('Não foi possível entrar. Verifique a conexão com o servidor.');
      }
    } finally {
      setCarregando(false);
    }
  };

  return (
    <div className="auth-page-body">
      <div className="auth-left-side">
        <form className="auth-form-wrapper" onSubmit={handleLogin}>
          <div className="auth-logo-box">
            <img src={iconLogo} alt="ÍconeDado" />
          </div>

          <h2>Player One</h2>
          <p>Entre para acessar seu catálogo de jogos</p>

          {erro && <div className="auth-error-box">{erro}</div>}

          <label>E-mail</label>
          <input
            type="email"
            placeholder="Digite seu e-mail"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />

          <label>Senha</label>
          <input
            type="password"
            placeholder="Digite sua senha"
            value={senha}
            onChange={(e) => setSenha(e.target.value)}
            required
          />

          <button type="submit" disabled={carregando}>
            {carregando ? 'Entrando...' : 'Entrar'}
          </button>

          <p className="auth-link-text">
            Não tem uma conta? <Link to="/cadastro">Cadastre-se</Link>
          </p>
        </form>
      </div>

      <div className="auth-right-side" style={{ backgroundImage: `url(${loginImg})` }}>
        <h1>Conecte-se com jogadores</h1>
        <p>Organize partidas, descubra novos jogos e faça parte da comunidade</p>
      </div>
    </div>
  );
};

export default Login;
