import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import api from '../api'
import Layout from '../components/Layout'
import ModalVacina from '../components/ModalVacina' // <--- IMPORTANTE

function Detalhes() {
  const { id } = useParams()
  const [crianca, setCrianca] = useState(null)
  const [loading, setLoading] = useState(true)
  
  // Estado para controlar qual vacina foi clicada
  const [vacinaSelecionada, setVacinaSelecionada] = useState(null)

  // Função isolada para poder ser chamada no início E depois de salvar
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

  // Carrega na montagem do componente
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

  const getNomeIdade = (meses) => {
    if (meses === 0) return "Ao Nascer"
    if (meses === 1) return "1 Mês"
    return `${meses} Meses`
  }

  if (loading) return <Layout><div className="text-center mt-5">Carregando...</div></Layout>
  if (!crianca) return <Layout><div className="alert alert-danger m-3">Criança não encontrada.</div></Layout>

  const gruposVacinas = agruparPorIdade(crianca.registros)
  const idadesOrdenadas = Object.keys(gruposVacinas).sort((a, b) => a - b)

  return (
    <Layout>
      <div className="container mt-2 pb-5">
        
        {/* --- TOPO DA PÁGINA --- */}
        <div className="d-flex justify-content-between align-items-start mb-4">
            <Link to="/lista" className="btn btn-outline-warning text-dark fw-bold px-4" style={{borderRadius: '20px'}}>
                <i className="fa-solid fa-arrow-left me-2"></i> Voltar
            </Link>

            <div className="text-end">
                <h2 className="fw-bold text-primary mb-0" style={{color: '#2c3e50'}}>{crianca.nome}</h2>
                <span className="badge bg-secondary">{crianca.idade_formatada}</span>
            </div>
        </div>

        {/* --- LOOP DOS GRUPOS DE IDADE --- */}
        {idadesOrdenadas.map((idade) => (
            <div key={idade} className="mb-5">
                
                {/* Cabeçalho do Grupo */}
                <div className="d-flex align-items-center mb-3 p-2 bg-white rounded shadow-sm border-start border-5 border-warning">
                    <i className="fa-regular fa-clock me-2 text-secondary"></i>
                    <h5 className="fw-bold m-0 text-dark">{getNomeIdade(parseInt(idade))}</h5>
                </div>

                {/* Grid de Cards de Vacina */}
                <div className="row g-3">
                    {gruposVacinas[idade].map((reg) => (
                        <div key={reg.id} className="col-12 col-md-6 col-lg-4">
                            
                            {/* O CARD AGORA É CLICÁVEL */}
                            <div 
                                onClick={() => setVacinaSelecionada(reg)} // <--- CLIQUE AQUI ABRE O MODAL
                                className={`card h-100 shadow-sm ${reg.status === 'ATRASADA' ? 'border-danger bg-light-danger' : 'border-light'}`}
                                style={{
                                    cursor: 'pointer', // Mãozinha
                                    backgroundColor: reg.status === 'ATRASADA' ? '#fff5f5' : '',
                                    transition: 'transform 0.2s'
                                }}
                                onMouseEnter={(e) => e.currentTarget.style.transform = 'scale(1.02)'}
                                onMouseLeave={(e) => e.currentTarget.style.transform = 'scale(1)'}
                            >
                                <div className="card-body">
                                    <h6 className="fw-bold text-primary mb-2">{reg.nome_vacina}</h6>
                                    <span className="badge bg-light text-dark border mb-3">
                                        {reg.dose || "Dose Única"}
                                    </span>

                                    <div className="d-flex align-items-center">
                                        {reg.status === 'ATRASADA' && (
                                            <>
                                                <i className="fa-solid fa-triangle-exclamation text-danger me-2"></i>
                                                <span className="fw-bold text-danger">Atrasada</span>
                                            </>
                                        )}
                                        {reg.status === 'PENDENTE' && (
                                            <>
                                                <i className="fa-regular fa-circle text-secondary me-2"></i>
                                                <span className="text-secondary">Pendente</span>
                                            </>
                                        )}
                                        {reg.status === 'APLICADA' && (
                                            <>
                                                <i className="fa-solid fa-check-circle text-success me-2"></i>
                                                <span className="fw-bold text-success">
                                                    {/* TRUQUE: Divide a string "2026-02-01" e remonta como "01/02/2026" */}
                                                    Aplicada em {reg.data_aplicacao.split('-').reverse().join('/')}
                                                </span>
                                            </>
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
                // A KEY É O SEGREDO: Se mudar o ID, o React reinicia o Modal do zero
                key={vacinaSelecionada.id} 
                registro={vacinaSelecionada}
                onClose={() => setVacinaSelecionada(null)}
                onSave={carregarDados} // Recarrega a tela ao salvar
            />
        )}

      </div>
    </Layout>
  )
}

export default Detalhes