import React from 'react'

const Pagination = ({ currentPage, totalItems, pageSize, onPageChange }) => {
  const totalPages = Math.ceil(totalItems / pageSize)

  if (totalPages <= 1) return null // Se só tem 1 página, não mostra nada

  // Gera array de páginas [1, 2, 3...]
  const pages = []
  for (let i = 1; i <= totalPages; i++) {
    pages.push(i)
  }

  return (
    <nav className="d-flex justify-content-center mt-4">
      <ul className="pagination shadow-sm">
        
        {/* Botão Anterior */}
        <li className={`page-item ${currentPage === 1 ? 'disabled' : ''}`}>
          <button 
            className="page-link border-0 text-dark fw-bold" 
            onClick={() => onPageChange(currentPage - 1)}
            disabled={currentPage === 1}
          >
            <i className="fa-solid fa-chevron-left"></i>
          </button>
        </li>

        {/* Números das Páginas */}
        {pages.map(page => (
            <li key={page} className={`page-item ${currentPage === page ? 'active' : ''}`}>
                <button 
                    className={`page-link border-0 fw-bold ${currentPage === page ? 'bg-primary text-white' : 'text-dark'}`}
                    onClick={() => onPageChange(page)}
                >
                    {page}
                </button>
            </li>
        ))}

        {/* Botão Próximo */}
        <li className={`page-item ${currentPage === totalPages ? 'disabled' : ''}`}>
          <button 
            className="page-link border-0 text-dark fw-bold" 
            onClick={() => onPageChange(currentPage + 1)}
            disabled={currentPage === totalPages}
          >
            <i className="fa-solid fa-chevron-right"></i>
          </button>
        </li>

      </ul>
    </nav>
  )
}

export default Pagination