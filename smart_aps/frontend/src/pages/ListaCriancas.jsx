import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import api from '../api'
import Layout from '../components/Layout'
import Pagination from '../components/Pagination'

function ListaCriancas() {
  const [criancas, setCriancas] = useState([])
  const [busca, setBusca] = useState('')
  const [loading, setLoading] = useState(true) // Começa como true para a primeira renderização
  
  // --- ESTADOS DE PAGINAÇÃO ---
  const [page, setPage] = useState(1)
  const [totalItems, setTotalItems] = useState(0)
  const PAGE_SIZE = 10 

  // ==========================================
  // CARREGAMENTO OTIMIZADO (Atraso Zero na abertura)
  // ==========================================
  useEffect(() => {
    setLoading(true)
    const controller = new AbortController()

    // O PULO DO GATO: Se a busca estiver vazia, carrega em 0ms.
    // Só aplica o atraso de 300ms se o usuário estiver digitando para não travar o servidor.
    const delay = busca.trim() !== '' ? 300 : 0

    const timeout = setTimeout(() => {
      api.get('criancas/', {
        params: { 
          search: busca,
          page: page 
        },
        signal: controller.signal // Conecta o cancelamento à requisição
      })
      .then(res => {
        setCriancas(res.data.results)
        setTotalItems(res.data.count)
        setLoading(false)
      })
      .catch(err => {
        // Ignora o erro se ele foi causado pelo AbortController (usuário digitando rápido)
        if (err.name !== 'CanceledError') {
          console.error("Erro ao buscar:", err)
          setLoading(false)
        }
      })
    }, delay)

    return () => {
      clearTimeout(timeout)
      controller.abort() 
    }
  }, [busca, page]) // O React escuta as mudanças de busca e página automaticamente aqui

  // ==========================================
  // HANDLERS
  // ==========================================
  const handleBuscaChange = (e) => {
    setBusca(e.target.value)
    setPage(1) // Volta para a página 1 ao fazer uma nova busca
  }

  const handlePageChange = (newPage) => {
    setPage(newPage)
    window.scrollTo({ top: 0, behavior: 'smooth' })
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
                        value={busca} 
                        onChange={handleBuscaChange}
                    />
                    {busca && (
                        <button className="btn btn-outline-secondary bg-white border-0" onClick={() => { setBusca(''); setPage(1); }}>
                            <i className="fa-solid fa-times"></i>
                        </button>
                    )}
                </div>
            </div>
        </div>

        {/* Lista de Cards */}
        <div className="position-relative">
            {/* Efeito visual suave durante o loading das próximas páginas */}
            {loading && (
                <div className="position-absolute w-100 h-100 d-flex justify-content-center pt-5" style={{backgroundColor: 'rgba(255,255,255,0.6)', zIndex: 10}}>
                    <div className="spinner-border text-primary mt-4"></div>
                </div>
            )}

            <div className="d-flex flex-column gap-2 pb-3">
                {criancas.length === 0 && !loading ? (
                    <div className="text-center text-muted py-5 bg-light rounded">
                        <i className="fa-solid fa-user-slash fa-2x mb-3 text-secondary"></i>
                        <h5>Nenhum paciente encontrado.</h5>
                    </div>
                ) : (
                    criancas.map(c => (
                        <Link key={c.id} to={`/crianca/${c.id}`} className="card border-0 shadow-sm text-decoration-none text-dark hover-card">
                            <div className="card-body py-3 px-4">
                                <div className="d-flex justify-content-between align-items-center">
                                    <div>
                                        <h5 className="fw-bold mb-1 text-dark">{c.nome}</h5>
                                        
                                        {/* NOVAS INFORMAÇÕES: Idade e Status */}
                                        <div className="d-flex gap-2 mb-2 mt-2">
                                            <span className="badge bg-light text-dark border">
                                                <i className="fa-regular fa-calendar me-1 text-secondary"></i>
                                                {c.idade_formatada}
                                            </span>
                                            {c.status_geral === 'EM_DIA' ? (
                                                <span className="badge bg-success-subtle text-success border border-success-subtle">
                                                    <i className="fa-solid fa-check-circle me-1"></i> Em Dia
                                                </span>
                                            ) : (
                                                <span className="badge bg-danger-subtle text-danger border border-danger-subtle">
                                                    <i className="fa-solid fa-triangle-exclamation me-1"></i> Atrasado
                                                </span>
                                            )}
                                        </div>

                                        <div className="text-muted small d-flex gap-3 align-items-center flex-wrap mt-1">
                                            <span title="Nome da Mãe"><i className="fa-solid fa-person-breastfeeding me-1 text-secondary"></i> Mãe: <strong>{c.nome_mae}</strong></span>
                                            <span className="border-start ps-3" title="CNS"><i className="fa-solid fa-id-card me-1 text-secondary"></i> CNS: {c.cns}</span>
                                        </div>
                                    </div>
                                    <div className="text-primary ms-3">
                                        <i className="fa-solid fa-chevron-right fs-4"></i>
                                    </div>
                                </div>
                            </div>
                        </Link>
                    ))
                )}
            </div>
        </div>

        {/* --- PAGINAÇÃO NO RODAPÉ --- */}
        {totalItems > 0 && (
            <Pagination 
                currentPage={page} 
                totalItems={totalItems} 
                pageSize={PAGE_SIZE} 
                onPageChange={handlePageChange} 
            />
        )}
        
        {/* Espaço extra no final para não colar no rodapé do celular */}
        <div className="mb-5"></div>

      </div>
      
      {/* Estilos inline para os efeitos de Hover */}
      <style>{`
        .hover-card { transition: transform 0.2s, background-color 0.2s; border-left: 4px solid transparent; }
        .hover-card:hover { transform: translateX(5px); background-color: #f8f9fa; border-left: 4px solid #0d6efd !important; }
        .hover-scale:hover { transform: scale(1.05); transition: transform 0.2s; }
      `}</style>
    </Layout>
  )
}

export default ListaCriancas