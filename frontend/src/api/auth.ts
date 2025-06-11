import api from './index';
import { LoginRequest } from '../types/auth';

const API_URL = '/auth'; // Base URL is already set in the api instance

export const login = async (username: string, password: string): Promise<{ access_token: string }> => {
    const response = await api.post(`${API_URL}/login`, {
        username,
        password,
    });
    if (response.data.access_token) {
        localStorage.setItem('access_token', response.data.access_token);
    }
    return response.data;
};

export const register = (username: string, email: string, password: string): Promise<any> => {
    return api.post(`${API_URL}/register`, {
        username,
        email,
        password,
    });
};

export const logout = () => {
    localStorage.removeItem('access_token');
};

export const getMe = async () => {
    const response = await api.get('/auth/me');
    return response.data;
}; 