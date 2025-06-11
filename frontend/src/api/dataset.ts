import api from './';
import { Dataset } from '../types/dataset';

const API_URL = '/datasets/';

export const getDatasets = async (): Promise<Dataset[]> => {
    const response = await api.get(API_URL);
    return response.data;
};

export const uploadDataset = async (file: File, onUploadProgress: (progressEvent: any) => void): Promise<Dataset> => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post('/datasets/upload', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
        onUploadProgress,
    });
    return response.data;
};

export const deleteDataset = async (datasetId: string): Promise<void> => {
    await api.delete(`${API_URL}${datasetId}`);
};

export const getDatasetColumns = async (datasetId: string): Promise<string[]> => {
    const response = await api.get(`${API_URL}${datasetId}/columns`);
    return response.data.columns;
};
