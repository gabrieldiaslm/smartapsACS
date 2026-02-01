import { useState } from 'react'
import api from '../api'
import { useNavigate } from 'react-router-dom'

function Login() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const navigate = useNavigate()

  const handleLogin = async (e) => {
    e.preventDefault()
    setError('')

    try {
      // 1. Envia usuário e senha para o Django
      const response = await api.post('http://127.0.0.1:8000/api/token/', {
        username: username,
        password: password
      })

      // 2. Se der certo, guarda o Token no navegador
      // 'access' é o token de acesso que dura alguns minutos
      // 'refresh' é o token para renovar o acesso
      localStorage.setItem('token', response.data.access)
      localStorage.setItem('refresh_token', response.data.refresh)

      // 3. Redireciona para a Home (Dashboard)
      navigate('/')
      
    } catch (err) {
      setError('Usuário ou senha incorretos.')
      console.error(err)
    }
  }

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f8f9fa' }}>
      
      {/* Header Laranja (Igual ao Django) */}
      <nav className="navbar navbar-dark mb-5" style={{ backgroundColor: '#e65100' }}>
        <div className="container">
          <span className="navbar-brand mb-0 h1">
            <i className="fa-solid fa-user-doctor me-2"></i>
            SmartAPS
          </span>
          <i className="fa-solid fa-bell text-white"></i>
        </div>
      </nav>

      {/* Card de Login Centralizado */}
      <div className="container d-flex justify-content-center">
        <div className="card shadow-sm" style={{ width: '400px' }}>
          
          {/* Cabeçalho Azul do Card */}
          <div className="card-header text-center text-white py-3" style={{ backgroundColor: '#0d6efd' }}>
            <h5 className="m-0">Acesso SMART APS</h5>
          </div>

          <div className="card-body p-4">
            <form onSubmit={handleLogin}>
              
              {error && <div className="alert alert-danger text-center">{error}</div>}

              <div className="mb-3">
                <label className="form-label">Usuário</label>
                <input 
                  type="text" 
                  className="form-control" 
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  required
                />
              </div>

              <div className="mb-4">
                <label className="form-label">Senha</label>
                <input 
                  type="password" 
                  className="form-control" 
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
              </div>

              <button type="submit" className="btn btn-primary w-100" style={{ backgroundColor: '#0d6efd' }}>
                Entrar
              </button>
            </form>
          </div>
          
          <div className="card-footer text-muted text-center py-3" style={{ fontSize: '0.8rem' }}>
            Acesso restrito a Agentes Comunitários.
          </div>

        </div>
      </div>
    </div>
  )
}

export default Login