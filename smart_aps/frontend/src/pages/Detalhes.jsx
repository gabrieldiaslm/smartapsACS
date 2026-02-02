import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import api from '../api'
import Layout from '../components/Layout'
import ModalVacina from '../components/ModalVacina'

function Detalhes() {
  const { id } = useParams()
  const [crianca, setCrianca] = useState(null)
  const [loading, setLoading] = useState(true)
  
  // Estado para controlar qual vacina foi clicada
  const [vacinaSelecionada, setVacinaSelecionada] = useState(null)

  const carregarDados = () => {
    api.get(`criancas/${id}/`)
      .then(response => {
        setCrianca(response.data)
        setLoading(false)
      })
      .catch(error => {
        console.error("Erro:", error)
        setLoading(false)
      })
  }

  useEffect(() => {
    carregarDados()
  }, [id])

  // --- LÓGICA DE AGRUPAMENTO ---
  const agruparPorIdade = (registros) => {
    if (!registros) return {}
    return registros.reduce((grupos, reg) => {
      const idade = reg.idade_alvo
      if (!grupos[idade]) grupos[idade] = []
      grupos[idade].push(reg)
      return grupos
    }, {})
  }

  // --- NOVA FUNÇÃO DE FORMATAÇÃO DE IDADE ---
  const getNomeIdade = (valor) => {
    const meses = parseInt(valor)
    
    if (meses === 0) return "Ao Nascer"
    if (meses === 1) return "1 Mês"
    if (meses < 12) return `${meses} Meses`

    // Cálculo de Anos
    const anos = Math.floor(meses / 12)
    const resto = meses % 12

    let texto = anos === 1 ? "1 Ano" : `${anos} Anos`

    // Adiciona os meses restantes se houver (ex: 1 Ano e 2 Meses)
    if (resto > 0) {
      texto += ` e ${resto} ${resto === 1 ? "Mês" : "Meses"}`
    }
    
    return texto
  }

  if (loading) return <Layout><div className="text-center mt-5"><div className="spinner-border text-primary"></div></div></Layout>
  if (!crianca) return <Layout><div className="alert alert-danger m-3">Criança não encontrada.</div></Layout>

  const gruposVacinas = agruparPorIdade(crianca.registros)
  const idadesOrdenadas = Object.keys(gruposVacinas).sort((a, b) => a - b)

  return (
    <Layout>
      <div className="container mt-2 pb-5">
        
        {/* --- TOPO DA PÁGINA --- */}
        <div className="d-flex justify-content-between align-items-start mb-4">
            <Link to="/lista" className="btn btn-outline-secondary rounded-pill px-4 fw-bold">
                <i className="fa-solid fa-arrow-left me-2"></i> Voltar
            </Link>

            <div className="text-end">
                <h2 className="fw-bold text-primary mb-0" style={{color: '#2c3e50'}}>{crianca.nome}</h2>
                <div className="text-muted">
                    <i className="fa-solid fa-cake-candles me-2"></i> {crianca.idade_formatada}
                </div>
            </div>
        </div>

        {/* --- LOOP DOS GRUPOS DE IDADE --- */}
        {idadesOrdenadas.map((idade) => (
            <div key={idade} className="mb-4">
                
                {/* Cabeçalho do Grupo (Agora usa a nova formatação) */}
                <div className="d-flex align-items-center mb-3 p-2 bg-white rounded shadow-sm border-start border-5 border-warning">
                    <i className="fa-regular fa-clock me-2 text-secondary ms-2"></i>
                    <h5 className="fw-bold m-0 text-dark">
                        {getNomeIdade(idade)}
                    </h5>
                </div>

                {/* Grid de Cards de Vacina */}
                <div className="row g-3">
                    {gruposVacinas[idade].map((reg) => (
                        <div key={reg.id} className="col-12 col-md-6 col-lg-4">
                            
                            <div 
                                onClick={() => setVacinaSelecionada(reg)} 
                                className={`card h-100 shadow-sm border-0`}
                                style={{
                                    cursor: 'pointer',
                                    transition: 'transform 0.2s',
                                    // Borda colorida na esquerda baseada no status
                                    borderLeft: reg.status === 'APLICADA' ? '5px solid #198754' : 
                                                reg.status === 'ATRASADA' ? '5px solid #dc3545' : 
                                                '5px solid #6c757d'
                                }}
                                onMouseEnter={(e) => {
                                    e.currentTarget.style.transform = 'translateY(-3px)'
                                    e.currentTarget.className = e.currentTarget.className.replace('shadow-sm', 'shadow')
                                }}
                                onMouseLeave={(e) => {
                                    e.currentTarget.style.transform = 'translateY(0)'
                                    e.currentTarget.className = e.currentTarget.className.replace('shadow', 'shadow-sm')
                                }}
                            >
                                <div className="card-body">
                                    <div className="d-flex justify-content-between align-items-start mb-2">
                                        <h6 className="fw-bold text-dark mb-0">{reg.nome_vacina}</h6>
                                        {/* Status Icon no canto */}
                                        {reg.status === 'APLICADA' && <i className="fa-solid fa-circle-check text-success fs-5"></i>}
                                        {reg.status === 'ATRASADA' && <i className="fa-solid fa-triangle-exclamation text-danger fs-5"></i>}
                                    </div>
                                    
                                    <span className="badge bg-light text-secondary border mb-3">
                                        {reg.dose || "Dose Única"}
                                    </span>

                                    <div className="d-flex align-items-center small">
                                        {reg.status === 'ATRASADA' && (
                                            <span className="fw-bold text-danger">Atrasada</span>
                                        )}
                                        {reg.status === 'PENDENTE' && (
                                            <span className="text-secondary">Pendente</span>
                                        )}
                                        {reg.status === 'APLICADA' && (
                                            <span className="fw-bold text-success">
                                                Aplicada em {reg.data_aplicacao ? reg.data_aplicacao.split('-').reverse().join('/') : ''}
                                            </span>
                                        )}
                                    </div>
                                </div>
                            </div>

                        </div>
                    ))}
                </div>
            </div>
        ))}

        {crianca.registros.length === 0 && (
            <div className="text-center text-muted mt-5">Nenhuma vacina encontrada.</div>
        )}

        {/* --- MODAL DE EDIÇÃO --- */}
        {vacinaSelecionada && (
            <ModalVacina 
                key={vacinaSelecionada.id} 
                registro={vacinaSelecionada}
                onClose={() => setVacinaSelecionada(null)}
                onSave={carregarDados}
            />
        )}

      </div>
    </Layout>
  )
}

export default Detalhes