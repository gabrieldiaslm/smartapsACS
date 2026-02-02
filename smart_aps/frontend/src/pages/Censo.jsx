import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import api from '../api'
import Layout from '../components/Layout'
import Pagination from '../components/Pagination'

function Censo() {
  const [criancas, setCriancas] = useState([])
  const [stats, setStats] = useState({ total: 0, meninos: 0, meninas: 0, bebes: 0 })
  const [loading, setLoading] = useState(true)

  // Filtros
  const [busca, setBusca] = useState('')
  const [statusFiltro, setStatusFiltro] = useState('')
  const [sexo, setSexo] = useState('')
  const [ordem, setOrdem] = useState('idade_dec')

  // Paginação
  const [page, setPage] = useState(1)
  const [totalItems, setTotalItems] = useState(0)
  const PAGE_SIZE = 10 

  const carregarDados = (paginaAtual = 1) => {
    setLoading(true)
    
    const params = {
      search: busca,
      status_filtro: statusFiltro,
      sexo: sexo,
      ordem: ordem,
      page: paginaAtual 
    }

    // Busca Lista Paginada
    const reqLista = api.get('criancas/', { params })
    // Busca Stats (Não muda com a página, só com filtros)
    const reqStats = api.get('criancas/estatisticas/', { params })

    Promise.all([reqLista, reqStats])
      .then(([resLista, resStats]) => {
        setCriancas(resLista.data.results) // Pega results
        setTotalItems(resLista.data.count) // Pega count
        setStats(resStats.data)
        setLoading(false)
      })
      .catch(err => {
        console.error("Erro ao carregar censo:", err)
        setLoading(false)
      })
  }

  // Se mudar qualquer filtro, reseta para página 1
  useEffect(() => {
    const timeout = setTimeout(() => {
      setPage(1)
      carregarDados(1)
    }, 300)
    return () => clearTimeout(timeout)
  }, [busca, statusFiltro, sexo, ordem])

  // Troca de página apenas
  const handlePageChange = (newPage) => {
    setPage(newPage)
    carregarDados(newPage)
    window.scrollTo(0, 0)
  }

  const limparFiltros = () => {
    setBusca(''); setStatusFiltro(''); setSexo(''); setOrdem('idade_dec');
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

        {/* Cards Estatísticas */}
        <div className="row g-3 mb-4">
            <div className="col-md-3"><div className="card shadow-sm border-primary text-center py-2"><small className="fw-bold text-muted">Total</small><h2 className="fw-bold text-primary m-0">{stats.total}</h2></div></div>
            <div className="col-md-3"><div className="card shadow-sm border-0 text-center py-2" style={{backgroundColor: '#e3f2fd'}}><small className="fw-bold text-primary">Meninos</small><h2 className="fw-bold text-primary m-0">{stats.meninos}</h2></div></div>
            <div className="col-md-3"><div className="card shadow-sm border-0 text-center py-2" style={{backgroundColor: '#fce4ec'}}><small className="fw-bold text-danger">Meninas</small><h2 className="fw-bold text-danger m-0">{stats.meninas}</h2></div></div>
            <div className="col-md-3"><div className="card shadow-sm border-success text-center py-2"><small className="fw-bold text-success">Bebês (&lt;1 ano)</small><h2 className="fw-bold text-success m-0">{stats.bebes}</h2></div></div>
        </div>

        {/* Filtros */}
        <div className="card shadow-sm p-3 mb-4 bg-light border-0">
            <div className="row g-2">
                <div className="col-md-4">
                    <div className="input-group"><span className="input-group-text bg-white"><i className="fa-solid fa-search"></i></span><input type="text" className="form-control" placeholder="Buscar..." value={busca} onChange={e => setBusca(e.target.value)}/></div>
                </div>
                <div className="col-md-2"><select className="form-select" value={statusFiltro} onChange={e => setStatusFiltro(e.target.value)}><option value="">Todos</option><option value="EM_DIA">✅ Em dia</option><option value="ATRASADO">⚠️ Atrasado</option></select></div>
                <div className="col-md-2"><select className="form-select" value={sexo} onChange={e => setSexo(e.target.value)}><option value="">Ambos</option><option value="M">Masculino</option><option value="F">Feminino</option></select></div>
                <div className="col-md-2"><select className="form-select" value={ordem} onChange={e => setOrdem(e.target.value)}><option value="idade_dec">Mais novos</option><option value="nome">A-Z</option></select></div>
                <div className="col-md-2"><button className="btn btn-outline-secondary w-100" onClick={limparFiltros}>Limpar</button></div>
            </div>
        </div>

        {/* Tabela */}
        {loading ? (
            <div className="text-center py-5"><div className="spinner-border text-primary"></div></div>
        ) : (
            <div className="card shadow-sm">
                <div className="table-responsive">
                    <table className="table table-hover align-middle mb-0">
                        <thead className="table-light">
                            <tr><th>Nome</th><th>Bairro</th><th>Idade</th><th>Sexo</th><th>Status</th><th className="text-end">Ações</th></tr>
                        </thead>
                        <tbody>
                            {criancas.map(c => (
                                <tr key={c.id}>
                                    <td className="fw-bold">{c.nome}</td>
                                    <td>{c.localidade}</td>
                                    <td>{c.idade_formatada}</td>
                                    <td>{c.sexo === 'M' ? <span className="badge bg-primary">Masc</span> : <span className="badge bg-danger">Fem</span>}</td>
                                    <td>{c.status_geral === 'EM_DIA' ? <span className="badge bg-success">Em dia</span> : <span className="badge bg-danger">Atrasado</span>}</td>
                                    <td className="text-end"><Link to={`/crianca/${c.id}`} className="btn btn-primary btn-sm">Abrir</Link></td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        )}

        {/* PAGINAÇÃO */}
        {!loading && totalItems > 0 && (
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