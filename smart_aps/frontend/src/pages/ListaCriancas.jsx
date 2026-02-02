import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import api from '../api'
import Layout from '../components/Layout'
import Pagination from '../components/Pagination' // <--- IMPORT NOVO

function ListaCriancas() {
  const [criancas, setCriancas] = useState([])
  const [busca, setBusca] = useState('')
  const [loading, setLoading] = useState(false)
  
  // --- ESTADOS DE PAGINAÇÃO ---
  const [page, setPage] = useState(1)
  const [totalItems, setTotalItems] = useState(0)
  const PAGE_SIZE = 10 // Tem que ser igual ao do Django

  const carregarCriancas = (paginaAtual) => {
    setLoading(true)
    api.get('criancas/', {
      params: { 
        search: busca,
        page: paginaAtual // Envia a página para o Django
      } 
    })
    .then(res => {
      // O Django paginado retorna: { count: 50, results: [...] }
      setCriancas(res.data.results)
      setTotalItems(res.data.count)
      setLoading(false)
    })
    .catch(err => {
      console.error("Erro ao buscar:", err)
      setLoading(false)
    })
  }

  // Se mudar a busca, volta para a página 1
  useEffect(() => {
    const timeout = setTimeout(() => {
      setPage(1) // Reseta página
      carregarCriancas(1)
    }, 500)
    return () => clearTimeout(timeout)
  }, [busca])

  // Se mudar a página (clicando no botão), carrega a nova página
  const handlePageChange = (newPage) => {
    setPage(newPage)
    carregarCriancas(newPage)
    window.scrollTo(0, 0) // Sobe a tela
  }

  return (
    <Layout>
      <div className="container mt-4">
        
        {/* Cabeçalho */}
        <div className="row align-items-center mb-4">
            <div className="col-4 text-start">
                <Link to="/" className="btn btn-outline-secondary rounded-pill px-4 fw-bold hover-scale">
                    <i className="fa-solid fa-arrow-left me-2"></i> Voltar
                </Link>
            </div>
            <div className="col-4 text-center">
                <h3 className="fw-bold text-primary mb-0 text-nowrap">Controle de Pacientes</h3>
            </div>
        </div>

        {/* Busca */}
        <div className="card border-0 shadow-sm mb-4">
            <div className="card-body p-2">
                <div className="input-group input-group-lg">
                    <span className="input-group-text bg-white border-0 text-muted">
                        <i className="fa-solid fa-magnifying-glass"></i>
                    </span>
                    <input 
                        type="text" className="form-control border-0 bg-transparent" 
                        placeholder="Buscar por nome, mãe ou CNS..." 
                        value={busca} onChange={(e) => setBusca(e.target.value)}
                    />
                </div>
            </div>
        </div>

        {/* Lista */}
        {loading ? (
            <div className="text-center py-5">
                <div className="spinner-border text-primary"></div>
                <p className="text-muted mt-2">Carregando...</p>
            </div>
        ) : (
            <div className="d-flex flex-column gap-2 pb-3">
                {criancas.map(c => (
                    <Link key={c.id} to={`/crianca/${c.id}`} className="card border-0 shadow-sm text-decoration-none text-dark hover-card">
                        <div className="card-body py-3 px-4">
                            <div className="d-flex justify-content-between align-items-center">
                                <div>
                                    <h5 className="fw-bold mb-1 text-dark">{c.nome}</h5>
                                    <div className="text-muted small d-flex gap-3 align-items-center mt-2 flex-wrap">
                                        <span title="Nome da Mãe"><i className="fa-solid fa-person-breastfeeding me-1 text-secondary"></i> Mãe: <strong>{c.nome_mae}</strong></span>
                                        <span className="border-start ps-3" title="CNS"><i className="fa-solid fa-id-card me-1 text-secondary"></i> CNS: {c.cns}</span>
                                    </div>
                                </div>
                                <div className="text-muted"><i className="fa-solid fa-chevron-right"></i></div>
                            </div>
                        </div>
                    </Link>
                ))}

                {criancas.length === 0 && (
                    <div className="text-center text-muted py-5 bg-light rounded">
                        <i className="fa-solid fa-user-slash fa-2x mb-3 text-secondary"></i>
                        <h5>Nenhum paciente encontrado.</h5>
                    </div>
                )}
            </div>
        )}

        {/* --- PAGINAÇÃO NO RODAPÉ --- */}
        {!loading && totalItems > 0 && (
            <Pagination 
                currentPage={page} 
                totalItems={totalItems} 
                pageSize={PAGE_SIZE} 
                onPageChange={handlePageChange} 
            />
        )}
        
        {/* Espaço extra no final */}
        <div className="mb-5"></div>

      </div>
      <style>{`
        .hover-card { transition: transform 0.2s, background-color 0.2s; }
        .hover-card:hover { transform: translateX(5px); background-color: #f8f9fa; border-left: 4px solid #ffc107 !important; }
        .hover-scale:hover { transform: scale(1.05); transition: transform 0.2s; }
      `}</style>
    </Layout>
  )
}

export default ListaCriancas