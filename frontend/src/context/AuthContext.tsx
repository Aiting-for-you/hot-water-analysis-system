import React, { createContext, useState, useEffect, ReactNode, useCallback } from 'react';
import { getMe } from '../api/auth';

interface User {
    id: string;
    username: string;
    email: string;
    role: 'admin' | 'user';
    is_admin: boolean;
}

interface AuthContextType {
    isAuthenticated: boolean;
    user: User | null;
    loading: boolean;
    login: (token: string) => Promise<void>;
    logout: () => void;
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
    const [user, setUser] = useState<User | null>(null);
    const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
    const [loading, setLoading] = useState<boolean>(true);

    const fetchUser = useCallback(async () => {
        const token = localStorage.getItem('access_token');
        if (token) {
            try {
                const userData = await getMe();
                setUser(userData);
                setIsAuthenticated(true);
            } catch (error) {
                console.error("Authentication Error:", error);
                localStorage.removeItem('access_token');
                setUser(null);
                setIsAuthenticated(false);
            }
        }
        setLoading(false);
    }, []);

    useEffect(() => {
        fetchUser();
    }, [fetchUser]);

    const login = useCallback(async (token: string) => {
        setLoading(true);
        localStorage.setItem('access_token', token);
        await fetchUser();
    }, [fetchUser]);

    const logout = useCallback(() => {
        localStorage.removeItem('access_token');
        setUser(null);
        setIsAuthenticated(false);
    }, []);

    return (
        <AuthContext.Provider value={{ isAuthenticated, user, loading, login, logout }}>
            {children}
        </AuthContext.Provider>
    );
}; 