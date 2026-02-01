import { useState, useEffect, useMemo } from 'react'
import api from '../api'

function ModalVacina({ registro, onClose, onSave }) {
  
  // FUNÇÃO PARA PEGAR DATA LOCAL (BRASIL) CORRETA
  const getDataHoje = () => {
    const hoje = new Date()
    const ano = hoje.getFullYear()
    const mes = String(hoje.getMonth() + 1).padStart(2, '0') // Adiciona zero à esquerda (02)
    const dia = String(hoje.getDate()).padStart(2, '0')      // Adiciona zero à esquerda (01)
    return `${ano}-${mes}-${dia}`
  }

  // --- ESTADOS ---
  const [formData, setFormData] = useState({
    status: registro?.status || 'PENDENTE',
    // CORREÇÃO AQUI: Usa a função local em vez de toISOString
    data_aplicacao: registro?.data_aplicacao || getDataHoje(),
    lote: registro?.lote || '',
    fabricante: registro?.fabricante || '',
    
    // Mantenha os códigos em MAIÚSCULO como vimos antes
    estrategia: registro?.estrategia || 'ROTINA', 
    via_administracao: registro?.via_administracao || 'INTRAMUSCULAR',
    local_aplicacao: registro?.local_aplicacao || '', 
    
    observacoes: registro?.observacoes || ''
  })

  const [listaLotes, setListaLotes] = useState([])
  
  // Inicia carregando se tivermos o ID da vacina
  const [carregandoLotes, setCarregandoLotes] = useState(() => !!registro?.vacina_id)

  // --- BUSCA DADOS NA API ---
  useEffect(() => {
    if (!registro?.vacina_id) {
        setCarregandoLotes(false)
        return
    }

    api.get(`vacinas/${registro.vacina_id}/lotes/`)
      .then(response => {
        setListaLotes(response.data)
        
        // Se já tem um lote salvo, garante que o fabricante bata com ele
        if (registro.lote) {
            const loteSalvo = response.data.find(l => l.numero_lote === registro.lote)
            if (loteSalvo) {
                setFormData(prev => ({ ...prev, fabricante: loteSalvo.fabricante }))
            }
        }
      })
      .catch(err => console.error("Erro ao buscar lotes:", err))
      .finally(() => setCarregandoLotes(false))
  }, [registro])


  // --- LÓGICA DE FILTRAGEM (O "Vínculo" que você pediu) ---
  
  // 1. Extrai fabricantes únicos baseados nos lotes disponíveis no banco
  const fabricantesDisponiveis = useMemo(() => {
    const fabs = listaLotes.map(l => l.fabricante)
    return [...new Set(fabs)] // Remove duplicados
  }, [listaLotes])

  // 2. Filtra os lotes: Se tiver fabricante selecionado, só mostra lotes dele
  const lotesFiltrados = useMemo(() => {
    if (formData.fabricante) {
        return listaLotes.filter(l => l.fabricante === formData.fabricante)
    }
    return listaLotes
  }, [listaLotes, formData.fabricante])


  // --- HANDLERS ---

  const handleFabricanteChange = (e) => {
    const novoFabricante = e.target.value
    setFormData({
        ...formData,
        fabricante: novoFabricante,
        // Se mudou o fabricante, limpa o lote pois o lote antigo pode não ser desse fabricante
        lote: '' 
    })
  }

  const handleLoteChange = (e) => {
    const novoLote = e.target.value
    // Acha os dados desse lote para pegar o fabricante correto
    const dadosLote = listaLotes.find(l => l.numero_lote === novoLote)
    
    setFormData({
      ...formData,
      lote: novoLote,
      // Se escolheu um lote, trava o fabricante nele
      fabricante: dadosLote ? dadosLote.fabricante : formData.fabricante
    })
  }

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      await api.patch(`registros/${registro.id}/`, formData)
      onSave()
      onClose()
    } catch (error) {
      console.error("Erro detalhado:", error)
      
      // Lógica para mostrar o erro real na tela
      if (error.response) {
        // O servidor respondeu (ex: 400 ou 500)
        const msg = JSON.stringify(error.response.data, null, 2)
        alert(`Erro no Servidor (${error.response.status}):\n${msg}`)
      } else if (error.request) {
        // A requisição saiu mas não teve resposta (rede caiu mesmo)
        alert("Erro de Rede: O servidor não respondeu.")
      } else {
        // Erro na montagem da requisição
        alert(`Erro Interno: ${error.message}`)
      }
    }
  }

  if (!registro) return null

// --- OPÇÕES FIXAS (Valor: Maiúsculo | Rótulo: Bonito) ---
  const OPCOES_ESTRATEGIA = [
    { value: 'ROTINA', label: 'Rotina' },
    { value: 'CAMPANHA', label: 'Campanha' },
    { value: 'BLOQUEIO', label: 'Bloqueio' },
    { value: 'ESPECIAL', label: 'Especial' }
  ]

  const OPCOES_VIA = [
    { value: 'INTRAMUSCULAR', label: 'Intramuscular' },
    { value: 'ORAL', label: 'Oral' },
    { value: 'SUBCUTANEA', label: 'Subcutânea' },
    { value: 'INTRADERMICA', label: 'Intradérmica' }
  ]

  const OPCOES_LOCAL = [
    { value: 'DELTOIDE_D', label: 'Deltoide Direito (Braço)' },
    { value: 'DELTOIDE_E', label: 'Deltoide Esquerdo (Braço)' },
    { value: 'VASTO_LATERAL_D', label: 'Vasto Lateral da Coxa D' },
    { value: 'VASTO_LATERAL_E', label: 'Vasto Lateral da Coxa E' },
    { value: 'GLUTEO_D', label: 'Glúteo (Dorso-Glúteo)' },
    { value: 'BOCA', label: 'Boca (Oral)' }
  ]

  return (
    <div className="modal show d-block" style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
      <div className="modal-dialog modal-lg modal-dialog-centered">
        <div className="modal-content border-0 shadow">
          
          {/* Header */}
          <div className="modal-header text-white" style={{ backgroundColor: '#0d6efd' }}>
            <h5 className="modal-title">Registrar Vacinação</h5>
            <button type="button" className="btn-close btn-close-white" onClick={onClose}></button>
          </div>

          <form onSubmit={handleSubmit}>
            <div className="modal-body p-4 bg-light">
              
              <div className="alert alert-info py-2 mb-4 shadow-sm">
                <strong>Vacina:</strong> {registro.nome_vacina} <span className="badge bg-info text-dark">{registro.dose}</span>
              </div>

              {/* Linha 1: Status, Data, Estratégia */}
              <div className="row g-3 mb-4">
                <div className="col-md-4">
                  <label className="form-label fw-bold">Status</label>
                  <select name="status" className="form-select" value={formData.status} onChange={handleChange}>
                    <option value="PENDENTE">Pendente</option>
                    <option value="APLICADA">Aplicada</option>
                    <option value="ATRASADA">Atrasada</option>
                  </select>
                </div>
                <div className="col-md-4">
                  <label className="form-label fw-bold">Data da Aplicação</label>
                  <input type="date" name="data_aplicacao" className="form-control" value={formData.data_aplicacao} onChange={handleChange} />
                </div>
                <div className="col-md-4">
                  <label className="form-label fw-bold">Estratégia</label>
                  <select name="estrategia" className="form-select" value={formData.estrategia} onChange={handleChange}>
                        {OPCOES_ESTRATEGIA.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
                    </select>
                </div>
              </div>

              {/* SEÇÃO INTELIGENTE: Lotes e Fabricantes */}
              <div className="card mb-4 border-warning">
                <div className="card-header bg-warning text-dark fw-bold">
                    <i className="fa-solid fa-box-open me-2"></i> Controle de Estoque
                </div>
                <div className="card-body bg-white">
                    <div className="row g-3">
                        {/* 1. Selecionar Fabricante Primeiro (Filtra os lotes) */}
                        <div className="col-md-6">
                          <label className="form-label fw-bold">Fabricante</label>
                          <select 
                            name="fabricante" 
                            className="form-select" 
                            value={formData.fabricante} 
                            onChange={handleFabricanteChange}
                            disabled={carregandoLotes}
                          >
                            <option value="">Todos os Fabricantes</option>
                            {fabricantesDisponiveis.map(fab => (
                                <option key={fab} value={fab}>{fab}</option>
                            ))}
                          </select>
                        </div>

                        {/* 2. Selecionar Lote (Filtrado) */}
                        <div className="col-md-6">
                          <label className="form-label fw-bold">
                            Lote Disponível 
                            {carregandoLotes && <small className="ms-2 text-muted">Buscando...</small>}
                          </label>
                          <select 
                            name="lote" 
                            className="form-select" 
                            value={formData.lote} 
                            onChange={handleLoteChange}
                            disabled={carregandoLotes}
                          >
                            <option value="">Selecione o lote...</option>
                            {lotesFiltrados.map(l => (
                              <option key={l.numero_lote} value={l.numero_lote}>
                                 {l.numero_lote} (Qtd: {l.quantidade_disponivel})
                              </option>
                            ))}
                          </select>
                          {lotesFiltrados.length === 0 && !carregandoLotes && formData.fabricante && (
                              <small className="text-danger">Sem lotes para este fabricante.</small>
                          )}
                        </div>
                    </div>
                </div>
              </div>

              {/* Dados Clínicos e Obs */}
              <div className="row g-3">
                 <div className="col-md-6">
                    <label className="form-label fw-bold small">Via de Administração</label>
                    <select name="via_administracao" className="form-select" value={formData.via_administracao} onChange={handleChange}>
                        {OPCOES_VIA.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
                    </select>
                 </div>
                 <div className="col-md-6">
                    <label className="form-label fw-bold small">Local de Aplicação</label>
                    <select name="local_aplicacao" className="form-select" value={formData.local_aplicacao} onChange={handleChange}>
                        <option value="">Selecione...</option>
                        {OPCOES_LOCAL.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
                    </select>
                 </div>
                 <div className="col-12 mt-3">
                    <label className="form-label fw-bold">Observações</label>
                    <textarea name="observacoes" className="form-control" rows="2" value={formData.observacoes} onChange={handleChange}></textarea>
                 </div>
              </div>

            </div>
            <div className="modal-footer bg-white">
              <button type="button" className="btn btn-secondary" onClick={onClose}>Cancelar</button>
              <button type="submit" className="btn btn-primary fw-bold px-4">Salvar Registro</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}

export default ModalVacina