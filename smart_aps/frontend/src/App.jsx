import { BrowserRouter, Routes, Route } from 'react-router-dom'

// Importe o seu novo componente de segurança
import ProtectedRoute from './components/ProtectedRoute'

// Suas Páginas
import Home from './pages/Home'
import ListaCriancas from './pages/ListaCriancas'
import Detalhes from './pages/Detalhes'
import Login from './pages/Login'
import Censo from './pages/Censo'
import GuiaVacinal from './pages/GuiaVacinal'
import CadastrarCrianca from './pages/CadastrarCrianca'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        
        {/* --- ROTA PÚBLICA (Qualquer um acessa) --- */}
        <Route path="/login" element={<Login />} />

        {/* --- ROTAS PROTEGIDAS (Só com Token) --- */}
        
        <Route path="/" element={
          <ProtectedRoute>
            <Home />
          </ProtectedRoute>
        } />

        <Route path="/lista" element={
          <ProtectedRoute>
            <ListaCriancas />
          </ProtectedRoute>
        } />

        <Route path="/crianca/:id" element={
          <ProtectedRoute>
            <Detalhes />
          </ProtectedRoute>
        } />

        <Route path="/censo" element={
          <ProtectedRoute>
            <Censo />
          </ProtectedRoute>
        } />

        <Route path="/guia-vacinal" element={
          <ProtectedRoute>
            <GuiaVacinal />
          </ProtectedRoute>
        } />
        <Route path="/cadastrar-crianca" element={
          <ProtectedRoute>
            <CadastrarCrianca/>
          </ProtectedRoute>
        } />

      </Routes>
    </BrowserRouter>
  )
}

export default App