import axios from 'axios';
import { message } from 'antd';

const api = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api',
});

// Request interceptor to add the access token to every request
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
        config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
}, (error) => {
    return Promise.reject(error);
});

// A variable to store the refresh token request
let isRefreshing = false;
let failedQueue: any[] = [];

const processQueue = (error: any, token: string | null = null) => {
    failedQueue.forEach(prom => {
        if (error) {
            prom.reject(error);
        } else {
            prom.resolve(token);
        }
    });
    failedQueue = [];
};

// Response interceptor to handle expired tokens and refresh them
api.interceptors.response.use((response) => {
    return response;
}, async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
        if (isRefreshing) {
            return new Promise((resolve, reject) => {
                failedQueue.push({ resolve, reject });
            })
            .then(token => {
                originalRequest.headers.Authorization = 'Bearer ' + token;
                return api(originalRequest);
            })
            .catch(err => {
                return Promise.reject(err);
            });
        }

        originalRequest._retry = true;
        isRefreshing = true;
        const refreshToken = localStorage.getItem('refresh_token');

        if (!refreshToken) {
            // No refresh token, redirect to login
            isRefreshing = false;
            window.location.href = '/login';
            return Promise.reject(error);
        }

        try {
            const { data } = await axios.post(`${api.defaults.baseURL}/auth/refresh`, {}, {
                headers: { Authorization: `Bearer ${refreshToken}` }
            });
            
            const newAccessToken = data.access_token;
            localStorage.setItem('access_token', newAccessToken);
            api.defaults.headers.common['Authorization'] = 'Bearer ' + newAccessToken;
            originalRequest.headers.Authorization = 'Bearer ' + newAccessToken;
            
            processQueue(null, newAccessToken);
            return api(originalRequest);
        } catch (refreshError) {
            processQueue(refreshError, null);
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            window.location.href = '/login';
            message.error('会话已过期，请重新登录。');
            return Promise.reject(refreshError);
        } finally {
            isRefreshing = false;
        }
    }
    return Promise.reject(error);
});

export default api; 