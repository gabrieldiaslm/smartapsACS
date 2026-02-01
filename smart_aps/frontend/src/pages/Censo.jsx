import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import api from '../api'
import Layout from '../components/Layout'

function Censo() {
  // Dados
  const [criancas, setCriancas] = useState([])
  const [stats, setStats] = useState({ total: 0, meninos: 0, meninas: 0, bebes: 0 })
  const [loading, setLoading] = useState(true)

  // Filtros
  const [busca, setBusca] = useState('')
  const [statusFiltro, setStatusFiltro] = useState('') // '' | EM_DIA | ATRASADO
  const [sexo, setSexo] = useState('')
  const [ordem, setOrdem] = useState('idade_dec') // Padrão: Mais novos

  // Função que carrega tudo
  const carregarDados = () => {
    setLoading(true)
    
    // Monta a URL com os filtros
    const params = {
      search: busca,
      status_filtro: statusFiltro,
      sexo: sexo,
      ordem: ordem
    }

    // 1. Busca a Lista
    const reqLista = api.get('criancas/', { params })
    // 2. Busca as Estatísticas (Cards) baseadas nos mesmos filtros
    const reqStats = api.get('criancas/estatisticas/', { params })

    Promise.all([reqLista, reqStats])
      .then(([resLista, resStats]) => {
        setCriancas(resLista.data)
        setStats(resStats.data)
        setLoading(false)
      })
      .catch(err => {
        console.error("Erro ao carregar censo:", err)
        setLoading(false)
      })
  }

  // Recarrega sempre que um filtro mudar
  useEffect(() => {
    // Debounce na busca (espera parar de digitar)
    const timeout = setTimeout(() => {
      carregarDados()
    }, 300)
    return () => clearTimeout(timeout)
  }, [busca, statusFiltro, sexo, ordem])

  // Limpar filtros
  const limparFiltros = () => {
    setBusca('')
    setStatusFiltro('')
    setSexo('')
    setOrdem('idade_dec')
  }

  return (
    <Layout>
      <div className="container mt-2 pb-5">
        
        {/* --- HEADER --- */}
        <div className="d-flex justify-content-between align-items-center mb-4">
            <div>
                <Link to="/" className="btn btn-outline-warning text-dark fw-bold me-3" style={{borderRadius: '20px'}}>
                    <i className="fa-solid fa-arrow-left me-2"></i> Voltar
                </Link>
            </div>
            <h3 className="fw-bold text-primary mb-0"><i className="fa-solid fa-users-viewfinder me-2"></i> Censo Demográfico</h3>
            <button className="btn btn-outline-secondary" onClick={() => window.print()}>
                <i className="fa-solid fa-print me-2"></i> Imprimir
            </button>
        </div>

        {/* --- CARDS DE ESTATÍSTICA (Igual ao Print) --- */}
        <div className="row g-3 mb-4">
            <div className="col-md-3">
                <div className="card shadow-sm border-primary text-center py-2">
                    <small className="fw-bold text-uppercase text-muted">Total</small>
                    <h2 className="fw-bold text-primary m-0">{stats.total}</h2>
                </div>
            </div>
            <div className="col-md-3">
                <div className="card shadow-sm border-0 text-center py-2" style={{backgroundColor: '#e3f2fd'}}>
                    <small className="fw-bold text-uppercase text-primary">Meninos</small>
                    <h2 className="fw-bold text-primary m-0">{stats.meninos}</h2>
                </div>
            </div>
            <div className="col-md-3">
                <div className="card shadow-sm border-0 text-center py-2" style={{backgroundColor: '#fce4ec'}}>
                    <small className="fw-bold text-uppercase text-danger">Meninas</small>
                    <h2 className="fw-bold text-danger m-0">{stats.meninas}</h2>
                </div>
            </div>
            <div className="col-md-3">
                <div className="card shadow-sm border-success text-center py-2">
                    <small className="fw-bold text-uppercase text-success">Bebês (&lt;1 ano)</small>
                    <h2 className="fw-bold text-success m-0">{stats.bebes}</h2>
                </div>
            </div>
        </div>

        {/* --- BARRA DE FILTROS --- */}
        <div className="card shadow-sm p-3 mb-4 bg-light border-0">
            <div className="row g-2">
                <div className="col-md-4">
                    <div className="input-group">
                        <span className="input-group-text bg-white"><i className="fa-solid fa-search"></i></span>
                        <input 
                            type="text" className="form-control" placeholder="Buscar nome..." 
                            value={busca} onChange={e => setBusca(e.target.value)}
                        />
                    </div>
                </div>
                <div className="col-md-2">
                    <select className="form-select" value={statusFiltro} onChange={e => setStatusFiltro(e.target.value)}>
                        <option value="">Status: Todos</option>
                        <option value="EM_DIA">✅ Em dia</option>
                        <option value="ATRASADO">⚠️ Atrasado</option>
                    </select>
                </div>
                <div className="col-md-2">
                    <select className="form-select" value={sexo} onChange={e => setSexo(e.target.value)}>
                        <option value="">Sexo: Ambos</option>
                        <option value="M">Masculino</option>
                        <option value="F">Feminino</option>
                    </select>
                </div>
                <div className="col-md-2">
                    <select className="form-select" value={ordem} onChange={e => setOrdem(e.target.value)}>
                        <option value="nome">A-Z</option>
                        <option value="idade_dec">Mais novos</option>
                        <option value="idade_cresc">Mais velhos</option>
                    </select>
                </div>
                <div className="col-md-2">
                    <button className="btn btn-outline-secondary w-100" onClick={limparFiltros}>
                        <i className="fa-solid fa-filter-circle-xmark me-2"></i> Limpar
                    </button>
                </div>
            </div>
        </div>

        {/* --- TABELA --- */}
        {loading ? (
            <div className="text-center py-5"><div className="spinner-border text-primary"></div></div>
        ) : (
            <div className="card shadow-sm">
                <div className="table-responsive">
                    <table className="table table-hover align-middle mb-0">
                        <thead className="table-light">
                            <tr>
                                <th>Nome da Criança</th>
                                <th>Bairro / Localidade</th>
                                <th>Idade</th>
                                <th>Sexo</th>
                                <th>Status</th>
                                <th className="text-end">Ações</th>
                            </tr>
                        </thead>
                        <tbody>
                            {criancas.map(c => (
                                <tr key={c.id}>
                                    <td className="fw-bold">{c.nome}</td>
                                    <td>{c.localidade}</td>
                                    <td>{c.idade_formatada}</td>
                                    <td>
                                        {c.sexo === 'M' ? 
                                            <span className="badge bg-primary"><i className="fa-solid fa-mars"></i> Masc</span> : 
                                            <span className="badge bg-danger"><i className="fa-solid fa-venus"></i> Fem</span>
                                        }
                                    </td>
                                    <td>
                                        {c.status_geral === 'EM_DIA' ? (
                                            <span className="badge bg-success rounded-pill px-3"><i className="fa-solid fa-check-circle me-1"></i> Em dia</span>
                                        ) : (
                                            <span className="badge bg-danger rounded-pill px-3"><i className="fa-solid fa-triangle-exclamation me-1"></i> Atrasado</span>
                                        )}
                                    </td>
                                    <td className="text-end">
                                        <Link to={`/crianca/${c.id}`} className="btn btn-primary btn-sm fw-bold">
                                            <i className="fa-solid fa-address-card me-2"></i> Abrir Cartão
                                        </Link>
                                    </td>
                                </tr>
                            ))}
                            {criancas.length === 0 && (
                                <tr>
                                    <td colSpan="6" className="text-center py-4 text-muted">Nenhum registro encontrado.</td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
                <div className="card-footer bg-white d-flex justify-content-between align-items-center">
                    <small className="text-muted">Total de registros: {criancas.length}</small>
                    {/* Paginação simples pode ser adicionada aqui se o backend suportar */}
                </div>
            </div>
        )}

      </div>
    </Layout>
  )
}

export default Censo