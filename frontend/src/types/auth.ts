// As defined in the PRD

export interface User {
    id: string;
    username: string;
    email: string;
    role: 'admin' | 'user' | 'viewer';
    permissions: string[];
    lastLogin: string;
    createdAt: string;
}

export interface LoginRequest {
    username: string;
    password: string;
    remember?: boolean;
}

export interface AuthState {
    user: User | null;
    token: string | null;
    isAuthenticated: boolean;
    loading: boolean;
    error: string | null;
} 