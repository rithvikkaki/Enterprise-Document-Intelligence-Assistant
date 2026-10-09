import { api } from '../lib/axios';
import { Project } from '../types';

export const projectsApi = {
  list: async (orgId: string): Promise<Project[]> => {
    const response = await api.get('/projects', {
      headers: { 'X-Organization-ID': orgId },
    });
    return response.data;
  },

  create: async (orgId: string, data: { name: string; slug?: string; description?: string }): Promise<Project> => {
    const response = await api.post('/projects', data, {
      headers: { 'X-Organization-ID': orgId },
    });
    return response.data;
  },

  get: async (orgId: string, projectId: string): Promise<Project> => {
    const response = await api.get(`/projects/${projectId}`, {
      headers: { 'X-Organization-ID': orgId },
    });
    return response.data;
  },

  delete: async (orgId: string, projectId: string): Promise<void> => {
    await api.delete(`/projects/${projectId}`, {
      headers: { 'X-Organization-ID': orgId },
    });
  },
};
