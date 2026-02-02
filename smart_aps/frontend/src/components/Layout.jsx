import { useState, useEffect } from 'react' // <--- Importe useState e useEffect
import { Link, useNavigate } from 'react-router-dom'
import api from '../api' // <--- Importe sua api

const Layout = ({ children }) => {
  const navigate = useNavigate()
  const [nomeUsuario, setNomeUsuario] = useState('ACS') // Valor padrão enquanto carrega

  // Busca o nome do usuário ao carregar o Layout
  useEffect(() => {
    api.get('usuario/me/')
      .then(response => {
        // Pega o full_name que o backend mandou
        if (response.data.full_name) {
            setNomeUsuario(response.data.full_name)
        }
      })
      .catch(error => {
        console.error("Erro ao buscar usuário:", error)
        // Se der erro de token (401), pode deslogar automaticamente se quiser
      })
  }, [])

  const handleLogout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('refresh_token')
    navigate('/login')
  }

  return (
    <div>
      {/* --- NAVBAR FIXO --- */}
      <nav className="navbar navbar-dark mb-4 shadow-sm" style={{ backgroundColor: '#e65100' }}>
        <div className="container">
          <Link to="/" className="navbar-brand mb-0 h1 text-decoration-none fw-bold">
            <i className="fa-solid fa-user-doctor me-2"></i>
            SmartAPS
          </Link>
          
          <div className="d-flex align-items-center">
             {/* Exibe o nome dinâmico aqui */}
             <span className="text-white me-3 d-none d-md-inline fw-bold">
                <i className="fa-regular fa-circle-user me-2"></i>
                Olá, {nomeUsuario}
             </span>
             
             <button onClick={handleLogout} className="btn btn-sm btn-light text-danger fw-bold">
                <i className="fa-solid fa-right-from-bracket me-1"></i> Sair
             </button>
          </div>
        </div>
      </nav>

      {/* --- CONTEÚDO DA PÁGINA --- */}
      <main>
        {children}
      </main>
    </div>
  )
}

export default Layout