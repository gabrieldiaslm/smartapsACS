//--- MODELO COM A INDICAÇÃO DE VACINAÇÃO NO MÊS ATUAL ---

import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import api from '../api'
import Layout from '../components/Layout'
import ModalVacina from '../components/ModalVacina'

function Detalhes() {
  const { id } = useParams()
  const [crianca, setCrianca] = useState(null)
  const [loading, setLoading] = useState(true)
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

  // --- FORMATAÇÃO DE IDADE ---
  const getNomeIdade = (valor) => {
    const meses = parseInt(valor)
    if (meses === 0) return "Ao Nascer"
    if (meses === 1) return "1 Mês"
    if (meses < 12) return `${meses} Meses`

    const anos = Math.floor(meses / 12)
    const resto = meses % 12
    let texto = anos === 1 ? "1 Ano" : `${anos} Anos`

    if (resto > 0) {
      texto += ` e ${resto} ${resto === 1 ? "Mês" : "Meses"}`
    }
    return texto
  }

  // --- LÓGICA: DOSE DESTE MÊS ---
  const verificarDoseDoMes = (dataNascimento, idadeAlvoMeses) => {
    if (!dataNascimento) return false;
    
    // Corrige problema de fuso horário dividindo a string 'YYYY-MM-DD'
    const [anoNasc, mesNasc, diaNasc] = dataNascimento.split('-');
    const dataIdeal = new Date(anoNasc, mesNasc - 1, diaNasc);
    
    // Soma a idade alvo em meses à data de nascimento
    dataIdeal.setMonth(dataIdeal.getMonth() + parseInt(idadeAlvoMeses));

    const hoje = new Date();
    // Verifica se o mês e o ano da data ideal batem com o mês e ano atuais
    return dataIdeal.getMonth() === hoje.getMonth() && dataIdeal.getFullYear() === hoje.getFullYear();
  }

  if (loading) return <Layout><div className="text-center mt-5"><div className="spinner-border text-primary"></div></div></Layout>
  if (!crianca) return <Layout><div className="alert alert-danger m-3">Paciente não encontrado.</div></Layout>

  const gruposVacinas = agruparPorIdade(crianca.registros)
  const idadesOrdenadas = Object.keys(gruposVacinas).sort((a, b) => a - b)

  return (
    <Layout>
      <div className="container mt-2 pb-5 print-container">
        
        {/* --- TOPO DA PÁGINA (Some na Impressão) --- */}
        <div className="d-flex justify-content-between align-items-center mb-4 d-print-none">
            <Link to="/lista" className="btn btn-outline-secondary rounded-pill px-4 fw-bold">
                <i className="fa-solid fa-arrow-left me-2"></i> Voltar
            </Link>
            
            <button className="btn btn-secondary rounded-pill px-4 fw-bold shadow-sm" onClick={() => window.print()}>
                <i className="fa-solid fa-print me-2"></i> Imprimir
            </button>
        </div>

        {/* --- CABEÇALHO DO PACIENTE --- */}
        <div className="card border-0 shadow-sm mb-4 print-header">
            <div className="card-body p-4 d-flex justify-content-between align-items-center flex-wrap gap-3">
                <div>
                    <h2 className="fw-bold text-primary mb-1">{crianca.nome}</h2>
                    <div className="d-flex gap-3 text-muted flex-wrap">
                        <span><i className="fa-regular fa-calendar me-1"></i> Nasc: {crianca.data_nascimento.split('-').reverse().join('/')} ({crianca.idade_formatada})</span>
                        <span><i className="fa-regular fa-id-card me-1"></i> CNS: {crianca.cns}</span>
                        <span><i className="fa-solid fa-person-breastfeeding me-1"></i> Mãe: {crianca.nome_mae}</span>
                    </div>
                </div>
                <div className="text-end d-print-none">
                    {crianca.status_geral === 'EM_DIA' ? (
                        <span className="badge bg-success fs-6 px-3 py-2 rounded-pill"><i className="fa-solid fa-check-circle me-1"></i> Em Dia</span>
                    ) : (
                        <span className="badge bg-danger fs-6 px-3 py-2 rounded-pill"><i className="fa-solid fa-triangle-exclamation me-1"></i> Atrasado</span>
                    )}
                </div>
            </div>
        </div>
        {/* ========================================================= */}
        {/* MODO TELA (Interativo, Cards, Visível apenas no Navegador) */}
        {/* ========================================================= */}
        <div className="d-print-none">
            {idadesOrdenadas.map((idade) => (
                <div key={idade} className="mb-4">
                    
                    <div className="d-flex align-items-center mb-3 p-2 bg-light rounded shadow-sm border-start border-5 border-warning">
                        <i className="fa-regular fa-clock me-2 text-secondary ms-2"></i>
                        <h5 className="fw-bold m-0 text-dark">
                            {getNomeIdade(idade)}
                        </h5>
                    </div>

                    <div className="row g-3">
                        {gruposVacinas[idade].map((reg) => {
                            // Verifica se é a dose do mês atual e está pendente
                            const isDoseMes = reg.status === 'PENDENTE' && verificarDoseDoMes(crianca.data_nascimento, reg.idade_alvo);

                            return (
                                <div key={reg.id} className="col-12 col-md-6 col-lg-4">
                                    <div 
                                        onClick={() => setVacinaSelecionada(reg)} 
                                        className={`card h-100 shadow-sm position-relative ${isDoseMes ? 'border-info bg-info-subtle' : 'border-0'}`}
                                        style={{
                                            cursor: 'pointer',
                                            transition: 'transform 0.2s',
                                            borderLeft: reg.status === 'APLICADA' ? '5px solid #198754' : 
                                                        reg.status === 'ATRASADA' ? '5px solid #dc3545' : 
                                                        isDoseMes ? '5px solid #0dcaf0' : '5px solid #ced4da'
                                        }}
                                        onMouseEnter={(e) => { e.currentTarget.style.transform = 'translateY(-3px)' }}
                                        onMouseLeave={(e) => { e.currentTarget.style.transform = 'translateY(0)' }}
                                    >
                                        <div className="card-body d-flex flex-column">
                                            
                                            {/* Badge Dinâmico de Dose do Mês */}
                                            {isDoseMes && (
                                                <span className="position-absolute top-0 end-0 badge bg-info text-dark mt-2 me-2">
                                                    <i className="fa-solid fa-star me-1"></i> Próxima Dose (Este Mês)
                                                </span>
                                            )}

                                            <div className="d-flex justify-content-between align-items-start mb-2 mt-2">
                                                <h6 className="fw-bold text-dark mb-0">{reg.vacina_nome || reg.nome_vacina}</h6>
                                                {reg.status === 'APLICADA' && <i className="fa-solid fa-circle-check text-success fs-5"></i>}
                                                {reg.status === 'ATRASADA' && <i className="fa-solid fa-circle-exclamation text-danger fs-5"></i>}
                                            </div>
                                            
                                            <span className="badge bg-light text-secondary border mb-3 align-self-start">
                                                {reg.dose || "Dose Única"}
                                            </span>

                                            <div className="mt-auto">
                                                {reg.status === 'ATRASADA' && <span className="fw-bold text-danger d-block mb-1">Atrasada</span>}
                                                {reg.status === 'PENDENTE' && !isDoseMes && <span className="text-muted d-block mb-1">Pendente</span>}
                                                {reg.status === 'PENDENTE' && isDoseMes && <span className="fw-bold text-info-emphasis d-block mb-1">Aguardando aplicação</span>}
                                                
                                                {reg.status === 'APLICADA' && (
                                                    <span className="fw-bold text-success d-block mb-2">
                                                        Aplicada em {reg.data_aplicacao ? reg.data_aplicacao.split('-').reverse().join('/') : ''}
                                                    </span>
                                                )}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            )
                        })}
                    </div>
                </div>
            ))}
            
            {crianca.registros.length === 0 && (
                <div className="text-center text-muted mt-5 py-5 bg-white rounded shadow-sm">
                    <i className="fa-solid fa-syringe fa-3x mb-3 opacity-25"></i>
                    <h5>Nenhuma vacina cadastrada no calendário.</h5>
                </div>
            )}
        </div>

        {/* ========================================================= */}
        {/* MODO IMPRESSÃO (Tabela de Extrato, Visível apenas no Ctrl+P) */}
        {/* ========================================================= */}
        <div className="d-none d-print-block mt-4">
            <h4 className="text-center fw-bold mb-4 text-uppercase">Extrato de Vacinação</h4>
            
            <table className="table table-bordered border-dark table-sm align-middle">
                <thead className="table-light">
                    <tr className="text-center">
                        <th style={{ width: '25%' }}>Vacina (Idade Alvo)</th>
                        <th style={{ width: '10%' }}>Dose</th>
                        <th style={{ width: '15%' }}>Data</th>
                        <th style={{ width: '20%' }}>Lote / Fabricante</th>
                        {/*<th style={{ width: '30%' }}>Assinatura / Carimbo</th>*/}
                    </tr>
                </thead>
                <tbody>
                    {idadesOrdenadas.map((idade) => (
                        gruposVacinas[idade].map((reg) => (
                            <tr key={reg.id}>
                                <td className="fw-bold">
                                    {reg.vacina_nome || reg.nome_vacina} 
                                    <div className="fw-normal small text-muted">{getNomeIdade(idade)}</div>
                                </td>
                                <td className="text-center">{reg.dose}</td>
                                
                                {/* Se aplicada mostra a data, se pendente/atrasada deixa espaço */}
                                <td className="text-center">
                                    {reg.status === 'APLICADA' 
                                        ? (reg.data_aplicacao ? reg.data_aplicacao.split('-').reverse().join('/') : '') 
                                        : '___/___/_____'
                                    }
                                </td>
                                
                                <td className="text-center small">
                                    {reg.status === 'APLICADA' && reg.lote ? reg.lote : ''}
                                </td>
                                
                                {/* Espaço generoso para carimbo */}
                                <td></td>
                            </tr>
                        ))
                    ))}
                </tbody>
            </table>
            
            {/* Assinatura do Responsável na UBS no rodapé da página impressa */}
            <div className="mt-5 pt-5 text-center">
                <div className="d-inline-block border-top border-dark pt-2" style={{ width: '300px' }}>
                    <strong>Profissional Responsável</strong><br/>
                    <small>Assinatura e Carimbo da Unidade</small>
                </div>
            </div>
        </div>

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

      <style>{`
        /* Esconde elementos indesejados na impressão do navegador */
        @media print {
            body { background-color: white !important; -webkit-print-color-adjust: exact; }
            .navbar, .sidebar, footer, .d-print-none { display: none !important; }
            .print-container { max-width: 100% !important; margin: 0 !important; padding: 20px !important; }
            .print-header { border: 2px solid #000 !important; box-shadow: none !important; margin-bottom: 20px !important; border-radius: 0 !important; }
            table { page-break-inside: auto; }
            tr { page-break-inside: avoid; page-break-after: auto; }
        }
      `}</style>
    </Layout>
  )
}

export default Detalhes