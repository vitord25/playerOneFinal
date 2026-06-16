import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import '../../style/StyleRegister/Auth.css';
import { useAuth } from '../../context/AuthContext';
import cadastroImg from '../../imgs/CadastroImage.png';
import iconLogo from '../../imgs/IconeDado.png';

const Register = () => {
  const navigate = useNavigate();
  const { register } = useAuth();

  const [nome, setNome] = useState('');
  const [email, setEmail] = useState('');
  const [senha, setSenha] = useState('');
  const [erro, setErro] = useState('');
  const [sucesso, setSucesso] = useState('');
  const [carregando, setCarregando] = useState(false);

  const handleRegister = async (e) => {
    e.preventDefault();
    setErro('');
    setSucesso('');

    // RGN03: senha forte (mín. 8 caracteres, letra + número/símbolo)
    const senhaForte = senha.length >= 8 && /[A-Za-z]/.test(senha) && /[\d\W_]/.test(senha);
    if (!senhaForte) {
      setErro('A senha deve ter no mínimo 8 caracteres, com letras e ao menos um número ou símbolo.');
      return;
    }

    setCarregando(true);
    try {
      await register({ name: nome, email, password: senha });
      setSucesso('Conta criada com sucesso! Redirecionando para o login...');
      setTimeout(() => navigate('/'), 1200);
    } catch (err) {
      const detail = err?.response?.data?.detail;
      if (err?.response?.status === 400 || err?.response?.status === 409) {
        setErro(typeof detail === 'string' ? detail : 'E-mail já cadastrado.');
      } else if (err?.response?.status === 422) {
        setErro('Dados inválidos. Verifique o e-mail e a senha.');
      } else {
        setErro('Não foi possível concluir o cadastro. Verifique a conexão com o servidor.');
      }
    } finally {
      setCarregando(false);
    }
  };

  return (
    <div className="auth-page-body">
      <div className="auth-left-side">
        <form className="auth-form-wrapper" onSubmit={handleRegister}>
          <div className="auth-logo-box">
            <img src={iconLogo} alt="ÍconeDado" />
          </div>
          <h2>Criar Conta</h2>
          <p>Junte-se à comunidade de jogadores</p>

          {erro && <div className="auth-error-box">{erro}</div>}
          {sucesso && <div className="auth-success-box">{sucesso}</div>}

          <label>Nome</label>
          <input
            type="text"
            placeholder="Digite seu nome"
            value={nome}
            onChange={(e) => setNome(e.target.value)}
            required
          />

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
            placeholder="Mín. 8 caracteres, com letra e número"
            value={senha}
            onChange={(e) => setSenha(e.target.value)}
            required
          />

          <button type="submit" disabled={carregando}>
            {carregando ? 'Cadastrando...' : 'Cadastrar'}
          </button>

          <p className="auth-link-text">
            Já tem uma conta?{' '}
            <Link to="/">
              <span className="auth-link-green">Entrar</span>
            </Link>
          </p>
        </form>
      </div>

      <div className="auth-right-side" style={{ backgroundImage: `url(${cadastroImg})` }}>
        <h1>Bem-vindo ao </h1>
        <h1>Player One</h1>
        <p>Acesse milhares de jogos e encontre pessoas para jogar</p>
      </div>
    </div>
  );
};

export default Register;
