import { Link } from 'react-router-dom'
import Layout from '../components/Layout' // <--- Importe o Layout

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
    transition: 'transform 0.2s'
  }

  return (
    // Embrulhe tudo com <Layout>
    <Layout>
        <div className="container">
        {/* Título opcional se quiser abaixo do navbar */}
        {/* <h3 className="mb-4 text-secondary">Painel Principal</h3> */}

        <div className="row g-4">
            {/* ... Seus cards continuam iguais aqui ... */}
            <div className="col-md-6">
            <Link to="#" className="card shadow-sm hover-effect" style={cardStyle}>
                <i className="fa-solid fa-plus-circle fa-3x mb-2"></i>
                <h4 className="fw-bold">Cadastrar Criança</h4>
            </Link>
            </div>

            <div className="col-md-6">
            <Link to="#" className="card shadow-sm hover-effect" style={cardStyle}>
                <i className="fa-solid fa-syringe fa-3x mb-2"></i>
                <h4 className="fw-bold">Calendário Vacinal</h4>
            </Link>
            </div>

            <div className="col-md-6">
            <Link to="/lista" className="card shadow-sm hover-effect" style={cardStyle}>
                <i className="fa-solid fa-id-card fa-3x mb-2"></i>
                <h4 className="fw-bold">Cartão de Vacina</h4>
            </Link>
            </div>

            <div className="col-md-6">
            <Link to="/lista" className="card shadow-sm hover-effect" style={cardStyle}>
                <i className="fa-solid fa-users fa-3x mb-2"></i>
                <h4 className="fw-bold">Crianças</h4>
            </Link>
            </div>
        </div>
        </div>
    </Layout>
  )
}

export default Home