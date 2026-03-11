import { useState, useEffect } from 'react'
import api from '../api'

function ModalVacina({ registro, onClose, onSave }) {
  
  // FUNÇÃO PARA PEGAR DATA LOCAL (BRASIL) CORRETA
  const getDataHoje = () => {
    const hoje = new Date()
    const ano = hoje.getFullYear()
    const mes = String(hoje.getMonth() + 1).padStart(2, '0')
    const dia = String(hoje.getDate()).padStart(2, '0')
    return `${ano}-${mes}-${dia}`
  }

  // --- ESTADOS ---
  const [formData, setFormData] = useState({
    status: registro?.status === 'PENDENTE' || (registro?.status === 'ATRASADA') ? 'APLICADA' : (registro?.status || 'APLICADA'), // Já abre como APLICADA para poupar cliques
    data_aplicacao: registro?.data_aplicacao || getDataHoje(),
    estrategia: registro?.estrategia || 'ROTINA', 
    via_administracao: registro?.via_administracao || 'INTRAMUSCULAR',
    local_aplicacao: registro?.local_aplicacao || '', 
    observacoes: registro?.observacoes || '',

    // --- NOVOS CAMPOS DO MODELO HÍBRIDO ---
    eh_transcricao: registro?.eh_transcricao || false,
    lote_vinculado: registro?.lote_vinculado || '', // ID do Lote (Estoque UBS)
    lote: registro?.lote || '',                     // Texto Livre (Caderneta)
    fabricante: registro?.fabricante || ''          // Texto Livre ou Auto-preenchido
  })

  const [listaLotes, setListaLotes] = useState([])
  const [carregandoLotes, setCarregandoLotes] = useState(() => !!registro?.vacina_id)

  // --- BUSCA DADOS NA API ---
  useEffect(() => {
    if (!registro?.vacina_id) {
        setCarregandoLotes(false)
        return
    }

    // Certifique-se de que a URL aqui bate com o seu urls.py do Django
    api.get(`vacinas/${registro.vacina_id}/lotes/`)
      .then(response => {
        setListaLotes(response.data)
      })
      .catch(err => console.error("Erro ao buscar lotes:", err))
      .finally(() => setCarregandoLotes(false))
  }, [registro])

  // --- HANDLERS ---
  const handleChange = (e) => {
    const { name, value, type, checked } = e.target
    setFormData({ 
        ...formData, 
        [name]: type === 'checkbox' ? checked : value 
    })
  }

  // Quando escolhe um lote da UBS, preenche o fabricante automaticamente na tela
  const handleLoteVinculadoChange = (e) => {
    const idLoteSelecionado = e.target.value
    const loteEncontrado = listaLotes.find(l => String(l.id) === String(idLoteSelecionado))
    
    setFormData({
        ...formData,
        lote_vinculado: idLoteSelecionado,
        fabricante: loteEncontrado ? loteEncontrado.fabricante : ''
    })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()

    const payload = { ...formData }
    if (payload.eh_transcricao) {
        payload.lote_vinculado = null // Limpa estoque se for transcrição
    } else {
        payload.lote = null 
        payload.fabricante = null
        if (payload.lote_vinculado === '') {
            payload.lote_vinculado = null;
        }
    }

    try {
      await api.patch(`registros/${registro.id}/`, payload)
      onSave()
      onClose()
    } catch (error) {
      console.error("Erro detalhado:", error)
      if (error.response) {
        const msg = JSON.stringify(error.response.data, null, 2)
        alert(`Erro no Servidor (${error.response.status}):\n${msg}`)
      } else if (error.request) {
        alert("Erro de Rede: O servidor não respondeu.")
      } else {
        alert(`Erro Interno: ${error.message}`)
      }
    }
  }

  if (!registro) return null

  // --- OPÇÕES FIXAS ---
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
          
          <div className="modal-header text-white" style={{ backgroundColor: '#0d6efd' }}>
            <h5 className="modal-title"><i className="fa-solid fa-syringe me-2"></i>Registrar Vacinação</h5>
            <button type="button" className="btn-close btn-close-white" onClick={onClose}></button>
          </div>

          <form onSubmit={handleSubmit}>
            <div className="modal-body p-4 bg-light">
              
              <div className="alert alert-info py-2 mb-4 shadow-sm d-flex justify-content-between align-items-center">
                <span><strong>Vacina:</strong> {registro.nome_vacina}</span>
                <span className="badge bg-primary fs-6">{registro.dose}</span>
              </div>

              {/* CHAVE DE TRANSCRIÇÃO (E-SUS) */}
              <div className="d-flex align-items-center mb-4 p-3 bg-white border rounded shadow-sm">
                <div className="form-check form-switch fs-5 mb-0">
                  <input 
                    className="form-check-input" 
                    type="checkbox" 
                    id="switchTranscricao"
                    name="eh_transcricao"
                    checked={formData.eh_transcricao}
                    onChange={handleChange}
                    style={{ cursor: 'pointer' }}
                  />
                  <label className="form-check-label fw-bold text-secondary ms-2" htmlFor="switchTranscricao" style={{ cursor: 'pointer', fontSize: '1rem' }}>
                    É Transcrição (Registro Anterior da Caderneta)
                  </label>
                </div>
              </div>

              {/* RASTREABILIDADE: UBS vs TRANSCRIÇÃO */}
              <div className={`card mb-4 ${formData.eh_transcricao ? 'border-secondary' : 'border-primary'}`}>
                <div className={`card-header text-white fw-bold ${formData.eh_transcricao ? 'bg-secondary' : 'bg-primary'}`}>
                    <i className={formData.eh_transcricao ? "fa-solid fa-pen me-2" : "fa-solid fa-box-open me-2"}></i> 
                    {formData.eh_transcricao ? "Dados da Caderneta" : "Controle de Estoque da UBS"}
                </div>
                <div className="card-body bg-white">
                    <div className="row g-3">
                        
                        {!formData.eh_transcricao ? (
                            // BLOCO 1: ESTOQUE DA UBS
                            <>
                                <div className="col-md-6">
                                    <label className="form-label fw-bold text-primary">Lote da Geladeira {carregandoLotes && <small className="text-muted">(Buscando...)</small>}</label>
                                    <select 
                                        name="lote_vinculado" 
                                        className="form-select border-primary" 
                                        value={formData.lote_vinculado} 
                                        onChange={handleLoteVinculadoChange}
                                        disabled={carregandoLotes}
                                    >
                                        <option value="">Selecione o Lote...</option>
                                        {listaLotes.map(l => (
                                            <option key={l.id} value={l.id}>
                                                {l.numero_lote} (Qtd: {l.quantidade_disponivel})
                                            </option>
                                        ))}
                                    </select>
                                    {listaLotes.length === 0 && !carregandoLotes && (
                                        <small className="text-danger">Nenhum lote com estoque disponível.</small>
                                    )}
                                </div>
                                <div className="col-md-6">
                                    <label className="form-label fw-bold text-primary">Fabricante</label>
                                    <input 
                                        type="text" 
                                        className="form-control bg-light text-muted" 
                                        value={formData.fabricante} 
                                        readOnly 
                                        placeholder="Preenchimento automático"
                                    />
                                </div>
                            </>
                        ) : (
                            // BLOCO 2: TRANSCRIÇÃO (TEXTO LIVRE)
                            <>
                                <div className="col-md-6">
                                    <label className="form-label fw-bold text-secondary">Lote Descrito no Papel</label>
                                    <input 
                                        type="text" 
                                        name="lote"
                                        className="form-control" 
                                        value={formData.lote} 
                                        onChange={handleChange}
                                        placeholder="Digite o lote..."
                                    />
                                </div>
                                <div className="col-md-6">
                                    <label className="form-label fw-bold text-secondary">Fabricante Descrito</label>
                                    <input 
                                        type="text" 
                                        name="fabricante"
                                        className="form-control" 
                                        value={formData.fabricante} 
                                        onChange={handleChange}
                                        placeholder="Digite o fabricante..."
                                    />
                                </div>
                            </>
                        )}
                    </div>
                </div>
              </div>

              {/* DADOS CLÍNICOS BÁSICOS */}
              <div className="row g-3 mb-3">
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
              <button type="button" className="btn btn-secondary px-4" onClick={onClose}>Cancelar</button>
              <button type="submit" className="btn btn-primary fw-bold px-4">
                <i className="fa-solid fa-check me-2"></i>Salvar Registro
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}

export default ModalVacina