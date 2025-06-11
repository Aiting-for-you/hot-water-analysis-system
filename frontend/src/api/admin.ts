import api from './index';

const API_URL = '/admin';

export const getUsers = async (page = 1, per_page = 10) => {
    const response = await api.get(`${API_URL}/users`, { params: { page, per_page } });
    return response.data;
};

export const updateUser = async (userId: string, userData: any) => {
    const response = await api.put(`${API_URL}/users/${userId}`, userData);
    return response.data;
};

export const deleteUser = async (userId: string) => {
    const response = await api.delete(`${API_URL}/users/${userId}`);
    return response.data;
};

export const getAllDatasets = async (page = 1, per_page = 10) => {
    const response = await api.get(`${API_URL}/datasets`, { params: { page, per_page } });
    return response.data;
};

export const deleteDataset = async (datasetId: string) => {
    const response = await api.delete(`${API_URL}/datasets/${datasetId}`);
    return response.data;
};
