import api from './index';

// Interface for the dataset dropdown
export interface DatasetForAnalysis {
  id: string;
  name: string;
  task_id: number;
  created_at: string;
}

// Interface for a single chart object
export interface AnalysisChart {
    id: number;
    title: string;
    image_base64: string; // This will be a data URL: "data:image/png;base64,..."
}

// Interface for the full analysis results object
export interface AnalysisResult {
  id: string;
  name: string;
  report: string;
  charts: AnalysisChart[];
  created_at: string;
}

// Interface for historical analysis items
export interface AnalysisHistoryItem {
    id: string;
    name: string;
    created_at: string;
}

/**
 * Fetches all successfully converted datasets suitable for analysis.
 */
export const getDatasetsForAnalysis = async (): Promise<DatasetForAnalysis[]> => {
  const response = await api.get('/analysis/datasets');
  return response.data;
};

/**
 * Starts the analysis process for a given dataset.
 * @param datasetId The ID of the converted dataset to analyze.
 * @returns A promise that resolves to an object containing the result_id.
 */
export const runAnalysis = async (datasetIds: string[]): Promise<{ result_id: string }> => {
  const response = await api.post(`/analysis/`, { dataset_ids: datasetIds });
  return response.data;
};

/**
 * Retrieves the stored analysis results using the result_id.
 * @param resultId The ID of the analysis result to fetch.
 * @returns A promise that resolves to the full analysis result object.
 */
export const getAnalysisResult = async (resultId: string): Promise<AnalysisResult> => {
    const response = await api.get(`/analysis/results/${resultId}`);
    return response.data;
};

/**
 * Fetches the list of historical analysis results.
 */
export const getAnalysisHistory = async (): Promise<AnalysisHistoryItem[]> => {
    const response = await api.get('/analysis/history');
    return response.data;
};

/**
 * Deletes a specific analysis result.
 * @param resultId The ID of the analysis result to delete.
 */
export const deleteAnalysisResult = async (resultId: string): Promise<void> => {
    await api.delete(`/analysis/results/${resultId}`);
};

/**
 * Triggers the download of an analysis report.
 * @param resultId The ID of the result whose report is to be downloaded.
 * @param filename The desired filename for the downloaded report.
 */
export const downloadAnalysisReport = async (resultId: string, filename: string): Promise<void> => {
    const response = await api.get(`/analysis/results/${resultId}/report`, {
        responseType: 'blob', // Important to handle the file download correctly
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
