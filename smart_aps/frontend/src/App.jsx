import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Home from './pages/Home'
import ListaCriancas from './pages/ListaCriancas'
import Detalhes from './pages/Detalhes'
import Login from './pages/Login' // <--- Importe aqui
import Censo from './pages/Censo'

function App() {
  return (
    <BrowserRouter>
      {/* Removemos o Navbar global daqui para ele não duplicar no Login */}
      
      <Routes>
        <Route path="/login" element={<Login />} />
        
        {/* Rotas protegidas (Futuramente vamos bloquear se não tiver login) */}
        <Route path="/" element={<Home />} />
        <Route path="/lista" element={<ListaCriancas />} />
        <Route path="/crianca/:id" element={<Detalhes />} />
        <Route path="/censo" element={<Censo />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App