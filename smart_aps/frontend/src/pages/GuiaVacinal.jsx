import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import api from '../api'
import Layout from '../components/Layout'

function GuiaVacinal() {
  const [vacinas, setVacinas] = useState([])
  const [loading, setLoading] = useState(true)
  
  // Estado para controlar quais sanfonas estão abertas. 
  // Ex: { "0": true, "2": false }
  const [secoesAbertas, setSecoesAbertas] = useState({})

  useEffect(() => {
    api.get('vacinas-guia/')
      .then(res => {
        setVacinas(res.data)
        setLoading(false)
        // Opcional: Abrir a primeira seção (Ao Nascer) automaticamente
        if (res.data.length > 0) {
            setSecoesAbertas({ 0: true })
        }
      })
      .catch(err => {
        console.error("Erro ao carregar guia:", err)
        setLoading(false)
      })
  }, [])

  // --- LÓGICA DE AGRUPAMENTO ---
  const agruparPorIdade = (lista) => {
    return lista.reduce((grupos, vacina) => {
      const idade = vacina.idade_alvo_meses
      if (!grupos[idade]) grupos[idade] = []
      grupos[idade].push(vacina)
      return grupos
    }, {})
  }

  // --- FORMATAÇÃO DE TEXTO ---
  const getNomeIdade = (valor) => {
    const meses = parseInt(valor)
    if (meses === 0) return "Ao Nascer"
    if (meses === 1) return "1 Mês"
    if (meses < 12) return `${meses} Meses`
    
    const anos = Math.floor(meses / 12)
    const resto = meses % 12
    let texto = anos === 1 ? "1 Ano" : `${anos} Anos`
    if (resto > 0) texto += ` e ${resto} ${resto === 1 ? "Mês" : "Meses"}`
    return texto
  }

  // --- CONTROLE DA SANFONA ---
  const toggleSecao = (idade) => {
    setSecoesAbertas(prev => ({
        ...prev,
        [idade]: !prev[idade] // Inverte o estado (se ta aberto fecha, se ta fechado abre)
    }))
  }

  if (loading) return <Layout><div className="text-center mt-5"><div className="spinner-border text-primary"></div></div></Layout>

  const grupos = agruparPorIdade(vacinas)
  const idadesOrdenadas = Object.keys(grupos).sort((a, b) => a - b)

  return (
    <Layout>
      <div className="container mt-4 pb-5">
        
        {/* --- HEADER --- */}
        <div className="d-flex justify-content-between align-items-center mb-4">
            <Link to="/" className="btn btn-outline-warning text-dark fw-bold rounded-pill px-4 hover-scale">
                <i className="fa-solid fa-arrow-left me-2"></i> Início
            </Link>
            
            <h3 className="fw-bold text-primary mb-0">Calendário Vacinal</h3>
        </div>

        <div className="card shadow-sm border-0">
            <div className="card-body p-0">
                
                {/* --- LOOP DAS IDADES (ACCORDION) --- */}
                {idadesOrdenadas.map((idade, index) => {
                    const isOpen = secoesAbertas[idade]
                    const listaVacinas = grupos[idade]
                    
                    return (
                        <div key={idade} className="border-bottom">
                            
                            {/* TÍTULO CLICÁVEL (HEADER DA SANFONA) */}
                            <div 
                                onClick={() => toggleSecao(idade)}
                                className="d-flex justify-content-between align-items-center p-3 cursor-pointer hover-bg"
                                style={{ 
                                    backgroundColor: isOpen ? '#e3f2fd' : '#fff', // Azulzinho se aberto
                                    cursor: 'pointer',
                                    transition: 'background-color 0.2s'
                                }}
                            >
                                <div className="d-flex align-items-center gap-3">
                                    <h5 className="fw-bold mb-0 text-dark">
                                        {getNomeIdade(idade)}
                                    </h5>
                                    <span className="badge bg-secondary rounded-pill">
                                        {listaVacinas.length} vacina(s)
                                    </span>
                                </div>
                                
                                <i className={`fa-solid fa-chevron-${isOpen ? 'up' : 'down'} text-muted`}></i>
                            </div>

                            {/* CONTEÚDO (TABELA) - SÓ MOSTRA SE 'isOpen' FOR TRUE */}
                            {isOpen && (
                                <div className="bg-white p-0 animate-fade-in">
                                    <table className="table table-striped mb-0">
                                        <thead className="table-light small text-muted">
                                            <tr>
                                                <th className="ps-4">Vacina</th>
                                                <th>Dose</th>
                                                <th>Proteção (Doença)</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {listaVacinas.map(v => (
                                                <tr key={v.id}>
                                                    <td className="ps-4 fw-bold text-primary">{v.nome}</td>
                                                    <td><span className="badge bg-light text-dark border">{v.dose_padrao}</span></td>
                                                    <td className="text-muted">{v.descricao_doenca}</td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            )}
                        </div>
                    )
                })}

            </div>
        </div>
      </div>

      <style>{`
        .hover-scale:hover { transform: scale(1.05); transition: transform 0.2s; }
        .hover-bg:hover { background-color: #f8f9fa !important; }
        .animate-fade-in { animation: fadeIn 0.3s ease-in-out; }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-5px); }
            to { opacity: 1; transform: translateY(0); }
        }
      `}</style>
    </Layout>
  )
}

export default GuiaVacinal