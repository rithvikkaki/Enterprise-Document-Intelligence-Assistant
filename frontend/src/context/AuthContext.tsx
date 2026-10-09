import React, { createContext, useContext, useState, useCallback, useEffect } from 'react';
import { User, Organization, Project } from '../types';
import { authApi } from '../api/auth';

interface AuthState {
  user: User | null;
  activeOrg: Organization | null;
  activeProject: Project | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

interface AuthContextValue extends AuthState {
  login: (accessToken: string, refreshToken: string) => Promise<void>;
  logout: () => void;
  setActiveOrg: (org: Organization) => void;
  setActiveProject: (project: Project | null) => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [activeOrg, setActiveOrgState] = useState<Organization | null>(() => {
    const stored = localStorage.getItem('active_org');
    return stored ? JSON.parse(stored) : null;
  });
  const [activeProject, setActiveProjectState] = useState<Project | null>(() => {
    const stored = localStorage.getItem('active_project');
    return stored ? JSON.parse(stored) : null;
  });
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      authApi
        .getMe()
        .then((u) => setUser(u))
        .catch(() => {
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
        })
        .finally(() => setIsLoading(false));
    } else {
      setIsLoading(false);
    }
  }, []);

  const login = useCallback(async (accessToken: string, refreshToken: string) => {
    localStorage.setItem('access_token', accessToken);
    localStorage.setItem('refresh_token', refreshToken);
    const me = await authApi.getMe();
    setUser(me);
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('active_org');
    localStorage.removeItem('active_project');
    setUser(null);
    setActiveOrgState(null);
    setActiveProjectState(null);
  }, []);

  const setActiveOrg = useCallback((org: Organization) => {
    setActiveOrgState(org);
    localStorage.setItem('active_org', JSON.stringify(org));
    // Clear project when org changes
    setActiveProjectState(null);
    localStorage.removeItem('active_project');
  }, []);

  const setActiveProject = useCallback((project: Project | null) => {
    setActiveProjectState(project);
    if (project) {
      localStorage.setItem('active_project', JSON.stringify(project));
    } else {
      localStorage.removeItem('active_project');
    }
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        activeOrg,
        activeProject,
        isAuthenticated: !!user,
        isLoading,
        login,
        logout,
        setActiveOrg,
        setActiveProject,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
