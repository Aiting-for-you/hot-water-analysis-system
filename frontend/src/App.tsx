import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, Outlet } from 'react-router-dom';
import { useAuth } from './hooks/useAuth';

// @ts-ignore
import AppLayout from './components/AppLayout';
import LoginPage from './pages/Login/Login';
import DashboardPage from './pages/DashboardPage';
import DataPage from './pages/Data/Data';
import DataConversionPage from './pages/DataConversionPage';
import WaterHabitAnalysisPage from './pages/WaterHabitAnalysisPage';
// @ts-ignore
import ReportsPage from './pages/ReportsPage';
// @ts-ignore
import WeatherPage from './pages/WeatherPage';
// @ts-ignore
import AssistantPage from "./pages/AssistantPage";
import UserCenterPage from "./pages/UserCenterPage";
import AdminRoute from './components/AdminRoute.tsx';
import UserManagementPage from './pages/admin/UserManagementPage';
import DatasetManagementPage from './pages/admin/DatasetManagementPage';
// @ts-ignore
import LogViewerPage from './pages/admin/LogViewerPage';

const PrivateRoute = () => {
    const { isAuthenticated } = useAuth();
    return isAuthenticated ? <Outlet /> : <Navigate to="/login" replace />;
};

const PublicRoute = () => {
    const { isAuthenticated } = useAuth();
    return !isAuthenticated ? <Outlet /> : <Navigate to="/dashboard" replace />;
};

function App() {
    return (
        <Router>
            <Routes>
                <Route element={<PublicRoute />}>
                    <Route path="/login" element={<LoginPage />} />
                </Route>
                
                <Route element={<PrivateRoute />}>
                    <Route path="/" element={<AppLayout />}>
                        <Route index element={<Navigate to="/dashboard" replace />} />
                        <Route path="/dashboard" element={<DashboardPage />} />
                        <Route path="/data" element={<DataPage />} />
                        <Route path="/data-conversion" element={<DataConversionPage />} />
                        <Route path="/water-habit-analysis" element={<WaterHabitAnalysisPage />} />
                        <Route path="/reports" element={<ReportsPage />} />
                        <Route path="/weather" element={<WeatherPage />} />
                        <Route path="/assistant" element={<AssistantPage />} />
                        <Route path="/user-center" element={<UserCenterPage />} />
                        
                        <Route element={<AdminRoute />}>
                            <Route path="/admin/user-management" element={<UserManagementPage />} />
                            <Route path="/admin/dataset-management" element={<DatasetManagementPage />} />
                            <Route path="/admin/logs" element={<LogViewerPage />} />
                        </Route>
                        
                        <Route path="/analysis" element={<Navigate to="/data-conversion" replace />} />
                        
                        <Route path="*" element={<Navigate to="/dashboard" replace />} />
                    </Route>
                </Route>
            </Routes>
        </Router>
    );
}

export default App; 