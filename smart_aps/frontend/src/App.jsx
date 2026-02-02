import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Home from './pages/Home'
import ListaCriancas from './pages/ListaCriancas'
import Detalhes from './pages/Detalhes'
import Login from './pages/Login'
import Censo from './pages/Censo'
import GuiaVacinal from './pages/GuiaVacinal'


function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        {/* Rotas protegidas (Futuramente vamos bloquear se não tiver login) */}
        <Route path="/" element={<Home />} />
        <Route path="/lista" element={<ListaCriancas />} />
        <Route path="/crianca/:id" element={<Detalhes />} />
        <Route path="/censo" element={<Censo />} />
        <Route path="/guia-vacinal" element={<GuiaVacinal />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App