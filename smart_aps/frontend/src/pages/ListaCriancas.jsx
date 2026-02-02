import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import api from '../api'
import Layout from '../components/Layout'

function ListaCriancas() {
  const [criancas, setCriancas] = useState([])
  const [busca, setBusca] = useState('')
  const [loading, setLoading] = useState(false)

  const carregarCriancas = () => {
    setLoading(true)
    api.get('criancas/', {
      params: { search: busca } 
    })
    .then(res => {
      const dados = res.data.results ? res.data.results : res.data
      setCriancas(dados)
      setLoading(false)
    })
    .catch(err => {
      console.error("Erro ao buscar:", err)
      setLoading(false)
    })
  }

  useEffect(() => {
    const timeout = setTimeout(() => {
      carregarCriancas()
    }, 500)
    return () => clearTimeout(timeout)
  }, [busca])

  return (
    <Layout>
      <div className="container mt-4">
        
{/* --- CABEÇALHO (Centralizado com Grid) --- */}
        <div className="row align-items-center mb-4">
            
            {/* Lado Esquerdo: Coluna de 4 partes */}
            <div className="col-4 text-start">
                <Link to="/" className="btn btn-outline-secondary rounded-pill px-4 fw-bold hover-scale">
                    <i className="fa-solid fa-arrow-left me-2"></i> Voltar
                </Link>
            </div>
            
            {/* Centro: Coluna de 4 partes (Título Centralizado) */}
            <div className="col-4 text-center">
                <h3 className="fw-bold text-primary mb-0 text-nowrap">
                    Controle
                </h3>
            </div>     
        </div>

        {/* --- BARRA DE BUSCA --- */}
        <div className="card border-0 shadow-sm mb-4">
            <div className="card-body p-2">
                <div className="input-group input-group-lg">
                    <span className="input-group-text bg-white border-0 text-muted">
                        <i className="fa-solid fa-magnifying-glass"></i>
                    </span>
                    <input 
                        type="text" 
                        className="form-control border-0 bg-transparent" 
                        placeholder="Buscar por nome, mãe ou CNS..." 
                        value={busca}
                        onChange={(e) => setBusca(e.target.value)}
                    />
                </div>
            </div>
        </div>

        {/* --- LISTA DE PACIENTES --- */}
        {loading ? (
            <div className="text-center py-5">
                <div className="spinner-border text-primary" role="status"></div>
                <p className="text-muted mt-2">Carregando lista...</p>
            </div>
        ) : (
            <div className="d-flex flex-column gap-2 pb-5">
                {criancas.map(c => (
                    <Link 
                        key={c.id} 
                        to={`/crianca/${c.id}`}  /* <--- CORRIGIDO AQUI: Removemos o /cartao/ */
                        className="card border-0 shadow-sm text-decoration-none text-dark hover-card"
                    >
                        <div className="card-body py-3 px-4">
                            <div className="d-flex justify-content-between align-items-center">
                                
                                {/* Dados do Paciente */}
                                <div>
                                    <h5 className="fw-bold mb-1 text-dark">
                                        {c.nome}
                                    </h5>
                                    
                                    <div className="text-muted small d-flex gap-3 align-items-center mt-2 flex-wrap">
                                        <span title="Nome da Mãe">
                                            <i className="fa-solid fa-person-breastfeeding me-1 text-secondary"></i> 
                                            Mãe: <strong>{c.nome_mae}</strong>
                                        </span>
                                        
                                        <span className="border-start ps-3" title="Cartão Nacional de Saúde">
                                            <i className="fa-solid fa-id-card me-1 text-secondary"></i> 
                                            CNS: {c.cns}
                                        </span>
                                    </div>
                                </div>

                                {/* Seta */}
                                <div className="text-muted">
                                    <i className="fa-solid fa-chevron-right"></i>
                                </div>
                            </div>
                        </div>
                    </Link>
                ))}

                {criancas.length === 0 && !loading && (
                    <div className="text-center text-muted py-5 bg-light rounded">
                        <i className="fa-solid fa-user-slash fa-2x mb-3 text-secondary"></i>
                        <h5>Nenhum paciente encontrado.</h5>
                    </div>
                )}
            </div>
        )}

      </div>

      <style>{`
        .hover-card {
            transition: transform 0.2s, background-color 0.2s;
        }
        .hover-card:hover {
            transform: translateX(5px);
            background-color: #f8f9fa;
            border-left: 4px solid #ffc107 !important;
        }
        .hover-scale:hover {
            transform: scale(1.05);
            transition: transform 0.2s;
        }
      `}</style>
    </Layout>
  )
}

export default ListaCriancas