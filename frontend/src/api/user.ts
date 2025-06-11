import api from './index';

const API_URL = '/user';

export const getUserProfile = async () => {
    const response = await api.get(`${API_URL}/profile`);
    return response.data;
};

export const updateUserProfile = async (profileData: { username: string; email: string }) => {
    const response = await api.put(`${API_URL}/profile`, profileData);
    return response.data;
};

export const changePassword = async (passwordData: { old_password: any; new_password: any; }) => {
    const response = await api.post(`${API_URL}/change-password`, passwordData);
    return response.data;
};
