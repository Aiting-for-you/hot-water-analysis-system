import api from './index';

const API_URL = '/dashboard';

export const getDashboardStats = async () => {
    const response = await api.get(`${API_URL}/stats`);
    return response.data;
}; 