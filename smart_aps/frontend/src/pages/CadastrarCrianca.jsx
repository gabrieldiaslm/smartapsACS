import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import api from '../api'
import Layout from '../components/Layout'

function CadastrarCrianca() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  
  // Estado que guarda os valores digitados
  const [formData, setFormData] = useState({
    nome: '',
    data_nascimento: '',
    cpf: '',
    cns: '',
    localidade: '',
    nome_mae: '',
    sexo: ''
  })

  // Estado que guarda as mensagens de erro do Django
  const [erros, setErros] = useState({})

  // Atualiza o estado conforme o usuário digita
  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
    // Limpa o erro daquele campo específico quando o usuário volta a digitar
    if (erros[e.target.name]) {
      setErros({ ...erros, [e.target.name]: null })
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setErros({}) // Limpa os erros anteriores

    try {
      // Envia os dados para a API (o DRF fará as validações)
      const response = await api.post('criancas/', formData)
      
      // Se deu certo, redireciona direto para o Cartão de Vacinas do novo paciente!
      navigate(`/crianca/${response.data.id}`)
      
    } catch (error) {
      console.error("Erro ao cadastrar:", error)
      setLoading(false)
      
      // Se o Django retornou erro de validação (HTTP 400), o DRF manda um objeto com os erros
      if (error.response && error.response.status === 400) {
        setErros(error.response.data)
      } else {
        alert("Erro inesperado de conexão. Verifique o servidor.")
      }
    }
  }

  return (
    <Layout>
      <div className="container mt-4 pb-5">
        <div className="row justify-content-center">
          <div className="col-md-8 col-lg-6">
            <div className="card shadow-sm border-0 rounded-3">
              
              {/* Cabeçalho */}
              <div className="card-header text-white rounded-top-3 p-3" style={{ backgroundColor: '#0d6efd' }}>
                <h5 className="mb-0 fw-bold">
                  <i className="fa-solid fa-baby me-2"></i> Cadastrar Novo Paciente
                </h5>
              </div>
              
              <div className="card-body p-4 bg-light">
                <form onSubmit={handleSubmit}>
                  
                  {/* Nome da Criança */}
                  <div className="mb-3">
                    <label className="form-label fw-bold text-secondary">Nome Completo da Criança *</label>
                    <input 
                      type="text" 
                      className={`form-control ${erros.nome ? 'is-invalid' : ''}`}
                      name="nome" 
                      value={formData.nome} 
                      onChange={handleChange} 
                      required 
                      placeholder="Ex: João da Silva"
                    />
                    {erros.nome && <div className="invalid-feedback fw-bold">{erros.nome}</div>}
                  </div>

                  {/* Linha: Data de Nascimento e Sexo */}
                  <div className="row g-3 mb-3">
                    <div className="col-md-6">
                      <label className="form-label fw-bold text-secondary">Data de Nascimento *</label>
                      <input 
                        type="date" 
                        className={`form-control ${erros.data_nascimento ? 'is-invalid' : ''}`}
                        name="data_nascimento" 
                        value={formData.data_nascimento} 
                        onChange={handleChange} 
                        required 
                      />
                      {erros.data_nascimento && <div className="invalid-feedback fw-bold">{erros.data_nascimento}</div>}
                    </div>
                    
                    <div className="col-md-6">
                      <label className="form-label fw-bold text-secondary">Sexo *</label>
                      <select 
                        className={`form-select ${erros.sexo ? 'is-invalid' : ''}`}
                        name="sexo" 
                        value={formData.sexo} 
                        onChange={handleChange} 
                        required
                      >
                        <option value="">Selecione...</option>
                        <option value="M">Masculino</option>
                        <option value="F">Feminino</option>
                      </select>
                      {erros.sexo && <div className="invalid-feedback fw-bold">{erros.sexo}</div>}
                    </div>
                  </div>

                  {/* Nome da Mãe */}
                  <div className="mb-3">
                    <label className="form-label fw-bold text-secondary">Nome da Mãe *</label>
                    <input 
                      type="text" 
                      className={`form-control ${erros.nome_mae ? 'is-invalid' : ''}`}
                      name="nome_mae" 
                      value={formData.nome_mae} 
                      onChange={handleChange} 
                      required 
                      placeholder="Nome completo da mãe"
                    />
                    {erros.nome_mae && <div className="invalid-feedback fw-bold">{erros.nome_mae}</div>}
                  </div>

                  {/* Linha: CNS e CPF */}
                  <div className="row g-3 mb-3">
                    <div className="col-md-6">
                      <label className="form-label fw-bold text-secondary">Cartão SUS (CNS) *</label>
                      <input 
                        type="text" 
                        className={`form-control ${erros.cns ? 'is-invalid' : ''}`}
                        name="cns" 
                        value={formData.cns} 
                        onChange={handleChange} 
                        required 
                        maxLength="15"
                        placeholder="Apenas números"
                      />
                      {erros.cns && <div className="invalid-feedback fw-bold">{erros.cns}</div>}
                    </div>

                    <div className="col-md-6">
                      <label className="form-label fw-bold text-secondary">CPF (Opcional)</label>
                      <input 
                        type="text" 
                        className={`form-control ${erros.cpf ? 'is-invalid' : ''}`}
                        name="cpf" 
                        value={formData.cpf} 
                        onChange={handleChange} 
                        maxLength="14"
                        placeholder="000.000.000-00"
                      />
                      {erros.cpf && <div className="invalid-feedback fw-bold">{erros.cpf}</div>}
                    </div>
                  </div>

                  {/* Localidade / Bairro */}
                  <div className="mb-4">
                    <label className="form-label fw-bold text-secondary">Localidade / Bairro *</label>
                    <input 
                      type="text" 
                      className={`form-control ${erros.localidade ? 'is-invalid' : ''}`}
                      name="localidade" 
                      value={formData.localidade} 
                      onChange={handleChange} 
                      required 
                      placeholder="Ex: Centro"
                    />
                    {erros.localidade && <div className="invalid-feedback fw-bold">{erros.localidade}</div>}
                  </div>

                  <hr className="my-4 text-secondary" />

                  {/* Botões de Ação */}
                  <div className="d-flex justify-content-between align-items-center">
                    <Link to="/lista" className="btn btn-outline-secondary rounded-pill px-4 fw-bold">
                      Cancelar
                    </Link>
                    
                    <button type="submit" className="btn btn-primary shadow-sm px-4 rounded-pill fw-bold" disabled={loading}>
                      {loading ? (
                        <><span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span> Salvando...</>
                      ) : (
                        <><i className="fa-solid fa-check me-2"></i> Salvar Cadastro</>
                      )}
                    </button>
                  </div>

                </form>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  )
}

export default CadastrarCrianca