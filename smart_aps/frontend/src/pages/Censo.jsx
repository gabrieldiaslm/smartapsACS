import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import api from '../api'
import Layout from '../components/Layout'
import Pagination from '../components/Pagination'

function Censo() {
  const [criancas, setCriancas] = useState([])
  const [stats, setStats] = useState({ total: 0, meninos: 0, meninas: 0, bebes: 0 })
  
  // Separamos os loadings para não piscar a tela inteira
  const [loadingStats, setLoadingStats] = useState(true)
  const [loadingLista, setLoadingLista] = useState(true)

  // Filtros
  const [busca, setBusca] = useState('')
  const [statusFiltro, setStatusFiltro] = useState('')
  const [sexo, setSexo] = useState('')
  const [ordem, setOrdem] = useState('idade_dec')

  // Paginação
  const [page, setPage] = useState(1)
  const [totalItems, setTotalItems] = useState(0)
  const PAGE_SIZE = 10 

  // 1. CARREGA ESTATÍSTICAS (Roda APENAS 1 VEZ quando a tela abre)
  useEffect(() => {
    api.get('criancas/estatisticas/')
      .then(res => {
        setStats(res.data)
        setLoadingStats(false)
      })
      .catch(err => console.error("Erro nas estatísticas:", err))
  }, [])

  // 2. CARREGA A LISTA (Otimizado: Sem atraso na abertura da tela)
  useEffect(() => {
    setLoadingLista(true)
    
    // AbortController cancela a requisição anterior se o usuário digitar muito rápido
    const controller = new AbortController()

    // O PULO DO GATO: Se o campo de busca estiver vazio, carrega na hora (0ms). 
    // Só aplica o atraso de 300ms se o usuário estiver ativamente digitando um nome.
    const delay = busca.trim() !== '' ? 300 : 0

    const timeout = setTimeout(() => {
      const params = {
        search: busca,
        status_filtro: statusFiltro,
        sexo: sexo,
        ordem: ordem,
        page: page 
      }

      api.get('criancas/', { params, signal: controller.signal })
        .then(res => {
          setCriancas(res.data.results)
          setTotalItems(res.data.count)
          setLoadingLista(false)
        })
        .catch(err => {
          if (err.name !== 'CanceledError') {
            console.error("Erro na lista:", err)
            setLoadingLista(false)
          }
        })
    }, delay)

    // Limpeza do useEffect
    return () => {
      clearTimeout(timeout)
      controller.abort() 
    }
  }, [busca, statusFiltro, sexo, ordem, page]) // Dependências corretas

  // 3. HANDLERS
  const handleFiltroChange = (setter) => (e) => {
    setter(e.target.value)
    setPage(1) // Volta para página 1 sempre que mexer num filtro
  }

  const handlePageChange = (newPage) => {
    setPage(newPage)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  const limparFiltros = () => {
    setBusca(''); setStatusFiltro(''); setSexo(''); setOrdem('idade_dec'); setPage(1);
  }

  return (
    <Layout>
      <div className="container mt-2 pb-5">
        
        {/* Header */}
        <div className="d-flex justify-content-between align-items-center mb-4">
            <div>
                <Link to="/" className="btn btn-outline-warning text-dark fw-bold me-3" style={{borderRadius: '20px'}}>
                    <i className="fa-solid fa-arrow-left me-2"></i> Voltar
                </Link>
            </div>
            <h3 className="fw-bold text-primary mb-0">Censo Demográfico</h3>
            <button className="btn btn-outline-secondary" onClick={() => window.print()}>
                <i className="fa-solid fa-print me-2"></i> Imprimir
            </button>
        </div>

        {/* Cards Estatísticas (Mostra skeleton ou spinner se loadingStats for true) */}
        <div className="row g-3 mb-4">
            <div className="col-md-3"><div className="card shadow-sm border-primary text-center py-2"><small className="fw-bold text-muted">Total (até 9 anos)</small><h2 className="fw-bold text-primary m-0">{loadingStats ? '...' : stats.total}</h2></div></div>
            <div className="col-md-3"><div className="card shadow-sm border-0 text-center py-2" style={{backgroundColor: '#e3f2fd'}}><small className="fw-bold text-primary">Meninos</small><h2 className="fw-bold text-primary m-0">{loadingStats ? '...' : stats.meninos}</h2></div></div>
            <div className="col-md-3"><div className="card shadow-sm border-0 text-center py-2" style={{backgroundColor: '#fce4ec'}}><small className="fw-bold text-danger">Meninas</small><h2 className="fw-bold text-danger m-0">{loadingStats ? '...' : stats.meninas}</h2></div></div>
            <div className="col-md-3"><div className="card shadow-sm border-success text-center py-2"><small className="fw-bold text-success">Bebês (&lt;1 ano)</small><h2 className="fw-bold text-success m-0">{loadingStats ? '...' : stats.bebes}</h2></div></div>
        </div>

        {/* Filtros */}
        <div className="card shadow-sm p-3 mb-4 bg-light border-0">
            <div className="row g-2">
                <div className="col-md-4">
                    <div className="input-group"><span className="input-group-text bg-white"><i className="fa-solid fa-search"></i></span><input type="text" className="form-control" placeholder="Buscar..." value={busca} onChange={handleFiltroChange(setBusca)}/></div>
                </div>
                <div className="col-md-2"><select className="form-select" value={statusFiltro} onChange={handleFiltroChange(setStatusFiltro)}><option value="">Todos</option><option value="EM_DIA">Em dia</option><option value="ATRASADO">Atrasado</option></select></div>
                <div className="col-md-2"><select className="form-select" value={sexo} onChange={handleFiltroChange(setSexo)}><option value="">Ambos</option><option value="M">Masculino</option><option value="F">Feminino</option></select></div>
                <div className="col-md-2"><select className="form-select" value={ordem} onChange={handleFiltroChange(setOrdem)}><option value="idade_dec">Mais velhos</option><option value="idade_inc">Mais novos</option><option value="nome">A-Z</option></select></div>
                <div className="col-md-2"><button className="btn btn-outline-secondary w-100" onClick={limparFiltros}>Limpar</button></div>
            </div>
        </div>

        {/* Tabela com efeito visual suave no Loading */}
        <div className="card shadow-sm position-relative">
            {/* Efeito de carregamento por cima da tabela */}
            {loadingLista && (
                <div className="position-absolute w-100 h-100 d-flex justify-content-center align-items-center" style={{backgroundColor: 'rgba(255,255,255,0.6)', zIndex: 10}}>
                    <div className="spinner-border text-primary"></div>
                </div>
            )}
            
            <div className="table-responsive">
                <table className="table table-hover align-middle mb-0">
                    <thead className="table-light">
                        <tr><th>Nome</th><th>Bairro</th><th>Idade</th><th>Sexo</th><th>Status</th><th className="text-end">Ações</th></tr>
                    </thead>
                    <tbody>
                        {criancas.length === 0 && !loadingLista ? (
                            <tr><td colSpan="6" className="text-center py-4 text-muted">Nenhuma criança encontrada.</td></tr>
                        ) : (
                            criancas.map(c => (
                                <tr key={c.id}>
                                    <td className="fw-bold">{c.nome}</td>
                                    <td>{c.localidade}</td>
                                    <td>{c.idade_formatada}</td>
                                    <td>{c.sexo === 'M' ? <span className="badge bg-primary">Masc</span> : <span className="badge bg-danger">Fem</span>}</td>
                                    <td>{c.status_geral === 'EM_DIA' ? <span className="badge bg-success">Em dia</span> : <span className="badge bg-danger">Atrasado</span>}</td>
                                    <td className="text-end"><Link to={`/crianca/${c.id}`} className="btn btn-primary btn-sm">Abrir</Link></td>
                                </tr>
                            ))
                        )}
                    </tbody>
                </table>
            </div>
        </div>

        {/* PAGINAÇÃO */}
        {totalItems > 0 && (
            <Pagination 
                currentPage={page} 
                totalItems={totalItems} 
                pageSize={PAGE_SIZE} 
                onPageChange={handlePageChange} 
            />
        )}

      </div>
    </Layout>
  )
}

export default Censo