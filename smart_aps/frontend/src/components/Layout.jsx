import { Link, useNavigate } from 'react-router-dom'

const Layout = ({ children }) => {
  const navigate = useNavigate()

  const handleLogout = () => {
    // Remove os tokens para "deslogar"
    localStorage.removeItem('token')
    localStorage.removeItem('refresh_token')
    navigate('/login')
  }

  return (
    <div>
      {/* --- NAVBAR FIXO (O Laranja) --- */}
      <nav className="navbar navbar-dark mb-4" style={{ backgroundColor: '#e65100' }}>
        <div className="container">
          <Link to="/" className="navbar-brand mb-0 h1 text-decoration-none">
            <i className="fa-solid fa-user-doctor me-2"></i>
            SmartAPS
          </Link>
          
          <div className="d-flex align-items-center">
             <span className="text-white me-3 d-none d-md-inline">Olá, ACS</span>
             <button onClick={handleLogout} className="btn btn-sm btn-outline-light">
                <i className="fa-solid fa-right-from-bracket"></i> Sair
             </button>
          </div>
        </div>
      </nav>

      {/* --- CONTEÚDO DA PÁGINA --- */}
      {/* Aqui é onde o React vai "colar" o conteúdo da Home, Lista, etc */}
      <main>
        {children}
      </main>
    </div>
  )
}

export default Layout