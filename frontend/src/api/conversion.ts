import api from './index'; // Corrected: Use the default export from index.ts

export interface ConvertedDataset {
  id: string;
  name: string;
  file_path: string;
  file_size: number;
  created_at: string;
}

export interface ConversionTask {
  id: number;
  original_dataset_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  created_at: string;
  converted_datasets: ConvertedDataset[];
}

// Fetch all conversion tasks
export const getConversionTasks = async (): Promise<ConversionTask[]> => {
  // Token is handled by the interceptor in api/index.ts
  const response = await api.get('/conversion/tasks');
  return response.data;
};

// Start a new conversion task for an original dataset
export const runConversion = async (datasetId: string): Promise<ConversionTask> => {
  const response = await api.post(`/conversion/run/${datasetId}`);
  return response.data;
};

// Delete a converted dataset
export const deleteConvertedDataset = async (datasetId: string): Promise<void> => {
  await api.delete(`/conversion/datasets/${datasetId}`);
};

// Fetches the file as a blob and creates a temporary URL for download
export const downloadConvertedDataset = async (datasetId: string, filename: string) => {
    // The interceptor will add the auth header for this GET request
    const response = await api.get(`/conversion/datasets/${datasetId}`, {
        responseType: 'blob',
    });

    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
}; 