import { useState, useEffect } from 'react'
import api from '../api'
import { Link } from 'react-router-dom'

function ListaCriancas() {
  const [criancas, setCriancas] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get('criancas/') 
      .then(response => {
        setCriancas(response.data)
        setLoading(false)
      })
      .catch(error => {
        console.error("Erro:", error)
        setLoading(false)
        // Dica: Se der erro 401, o token venceu ou não existe.
        if (error.response && error.response.status === 401) {
            alert("Sua sessão expirou. Faça login novamente.")
            window.location.href = '/login'
        }
      })
  }, [])

  return (
    <div className="container mt-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2 className="text-primary"><i className="fa-solid fa-list"></i> Crianças</h2>
        <Link to="/" className="btn btn-outline-secondary">
             <i className="fa-solid fa-arrow-left"></i> Voltar
        </Link>
      </div>
      
      {loading ? <p>Carregando...</p> : (
        <div className="list-group">
          {criancas.map(crianca => (
            <Link to={`/crianca/${crianca.id}`} key={crianca.id} className="list-group-item list-group-item-action d-flex justify-content-between align-items-center">
              <div>
                <h5 className="mb-1">{crianca.nome}</h5>
                <small className="text-muted">{crianca.idade_formatada} - {crianca.localidade}</small>
              </div>
              {crianca.status_geral === 'ATRASADO' ? (
                 <span className="badge bg-danger rounded-pill">Atrasado</span>
              ) : (
                 <span className="badge bg-success rounded-pill">Em dia</span>
              )}
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}

export default ListaCriancas