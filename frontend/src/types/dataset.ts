// As defined in the PRD

export interface Dataset {
    id: string;
    name: string;
    filename: string;
    filepath: string;
    file_size: number;
    created_at: string;
    user_id: string;
    description?: string;
}
  
export interface UploadProgress {
    percent: number;
    status: 'uploading' | 'success' | 'error';
    message?: string;
}
  
export interface DataPreview {
    columns: string[];
    data: Record<string, any>[];
    totalRows: number;
    sampleRows: number;
} 