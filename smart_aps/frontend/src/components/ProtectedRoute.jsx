import { Navigate } from 'react-router-dom'

function ProtectedRoute({ children }) {
  // 1. Tenta pegar o token salvo
  const token = localStorage.getItem('token')

  // 2. Se NÃO tiver token, chuta para o Login
  if (!token) {
    // 'replace' impede que o usuário volte para cá clicando na setinha "voltar" do navegador
    return <Navigate to="/login" replace />
  }

  // 3. Se tiver token, deixa renderizar a página filha (o conteúdo real)
  return children
}

export default ProtectedRoute