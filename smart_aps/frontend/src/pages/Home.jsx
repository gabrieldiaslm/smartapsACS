import { Link } from 'react-router-dom'
import Layout from '../components/Layout'

function Home() {
  const cardStyle = {
    backgroundColor: '#e65100',
    color: 'white',
    border: 'none',
    minHeight: '150px',
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'center',
    alignItems: 'center',
    textDecoration: 'none',
    // transition: 'transform 0.2s' <--- REMOVI DAQUI E PASSEI PRO CSS ABAIXO
  }

  return (
    <Layout>
        <div className="container mt-4">
        
        {/* Título opcional */}
        <div className="mb-4 text-center">
            <h3 className="fw-bold" style={{color: '#e65100'}}>Painel Principal</h3>
            <p className="text-muted">Bem-vindo ao Sistema SmartAPS</p>
        </div>

        <div className="row g-4">
            
            {/* 1. CONTROLE DE PACIENTES (Lista) */}
            <div className="col-md-6">
                {/* Atualizei o link para /criancas que é a lista que criamos */}
                <Link to="/lista" className="card shadow-sm hover-effect" style={cardStyle}>
                    <i className="fa-solid fa-users fa-3x mb-2"></i>
                    <h4 className="fw-bold">Controle de Pacientes</h4>
                </Link>
            </div>

            {/* 2. GUIA VACINAL */}
            <div className="col-md-6">
                <Link to="/guia-vacinal" className="card shadow-sm hover-effect" style={cardStyle}>
                    <i className="fa-solid fa-book-medical fa-3x mb-2"></i>
                    <h4 className="fw-bold">Guia Vacinal</h4>
                </Link>
            </div>

            {/* 3. CENSO DEMOGRÁFICO */}
            <div className="col-md-6">
                <Link to="/censo" className="card shadow-sm hover-effect" style={cardStyle}>
                    <i className="fa-solid fa-chart-pie fa-3x mb-2"></i>
                    <h4 className="fw-bold">Censo Demográfico</h4>
                </Link>
            </div>

            {/* 4. desativado */}
            <div className="col-md-6">
                <Link to="#" className="card shadow-sm hover-effect" style={{...cardStyle, backgroundColor: '#757575', cursor: 'not-allowed'}}>
                    <i className="fa-solid fa-lock fa-3x mb-2"></i>
                    <h4 className="fw-bold">Desativado (Cadastrar usuário)</h4>
                </Link>
            </div>

        </div>
        </div>

        {/* --- CSS DO EFEITO HOVER --- */}
        <style>{`
            .hover-effect {
                transition: transform 0.3s ease, box-shadow 0.3s ease;
            }
            
            .hover-effect:hover {
                transform: translateY(-8px); /* O botão sobe 8 pixels */
                box-shadow: 0 10px 20px rgba(230, 81, 0, 0.4) !important; /* Sombra laranja suave */
                filter: brightness(1.1); /* Clareia levemente a cor */
            }
        `}</style>

    </Layout>
  )
}

export default Home