export interface AnalysisTask {
    id: string;
    task_name: string;
    task_type: string;
    status: 'pending' | 'running' | 'completed' | 'failed';
    created_at: string;
    result?: any;
    parameters?: Record<string, any>;
} 