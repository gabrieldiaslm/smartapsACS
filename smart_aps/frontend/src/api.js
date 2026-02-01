import axios from 'axios';

const api = axios.create({
    baseURL: 'http://127.0.0.1:8000/api/',
});

// 1. Antes de enviar: Coloca o token no cabeçalho
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// 2. Se der erro na resposta (Token Vencido): Tenta renovar
api.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;

        // Se o erro for 401 (Não autorizado) e a gente ainda não tentou renovar...
        if (error.response.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;

            try {
                // Pega o token de renovação
                const refreshToken = localStorage.getItem('refresh_token');
                
                // Pede um novo token para o Django
                const response = await axios.post('http://127.0.0.1:8000/api/token/refresh/', {
                    refresh: refreshToken
                });

                // Salva o novo token
                localStorage.setItem('token', response.data.access);

                // Atualiza o cabeçalho da requisição original e tenta de novo
                api.defaults.headers.common['Authorization'] = `Bearer ${response.data.access}`;
                originalRequest.headers['Authorization'] = `Bearer ${response.data.access}`;

                return api(originalRequest);
            } catch {
                // Se nem renovar funcionou, desloga o usuário
                console.error("Sessão expirada. Faça login novamente.");
                localStorage.removeItem('token');
                localStorage.removeItem('refresh_token');
                window.location.href = '/login';
            }
        }

        return Promise.reject(error);
    }
);

export default api;