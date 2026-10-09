import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from './context/AuthContext';
import { ProtectedRoute, OrgRequiredRoute } from './components/routing/ProtectedRoute';

// Pages - lazy loaded for performance
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import OrgSelectPage from './pages/OrgSelectPage';
import DashboardPage from './pages/DashboardPage';
import ProjectsPage from './pages/ProjectsPage';
import DocumentsPage from './pages/DocumentsPage';
import DocumentDetailPage from './pages/DocumentDetailPage';
import SearchPage from './pages/SearchPage';
import AssistantPage from './pages/AssistantPage';
import ApiKeysPage from './pages/ApiKeysPage';
import AuditLogsPage from './pages/AuditLogsPage';
import MembersPage from './pages/MembersPage';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      staleTime: 30_000,
    },
  },
});

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            {/* Public routes */}
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />

            {/* Authenticated, org selection */}
            <Route element={<ProtectedRoute />}>
              <Route path="/org-select" element={<OrgSelectPage />} />
            </Route>

            {/* Authenticated + org required */}
            <Route element={<OrgRequiredRoute />}>
              <Route path="/dashboard" element={<DashboardPage />} />
              <Route path="/projects" element={<ProjectsPage />} />
              <Route path="/documents" element={<DocumentsPage />} />
              <Route path="/documents/:documentId" element={<DocumentDetailPage />} />
              <Route path="/search" element={<SearchPage />} />
              <Route path="/assistant" element={<AssistantPage />} />
              <Route path="/api-keys" element={<ApiKeysPage />} />
              <Route path="/audit-logs" element={<AuditLogsPage />} />
              <Route path="/members" element={<MembersPage />} />
            </Route>

            {/* Default redirect */}
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </QueryClientProvider>
  );
}
