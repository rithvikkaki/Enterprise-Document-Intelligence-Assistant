import { api } from '../lib/axios';
import { Project } from '../types';

export const projectsApi = {
  list: async (orgId: string): Promise<Project[]> => {
    const response = await api.get(`/organizations/${orgId}/projects`);
    return response.data;
  },

  create: async (orgId: string, data: { name: string; description?: string }): Promise<Project> => {
    const response = await api.post(`/organizations/${orgId}/projects`, data);
    return response.data;
  },

  get: async (orgId: string, projectId: string): Promise<Project> => {
    const response = await api.get(`/projects/${projectId}`, {
      params: { organization_id: orgId },
    });
    return response.data;
  },

  delete: async (orgId: string, projectId: string): Promise<void> => {
    await api.delete(`/projects/${projectId}`, {
      params: { organization_id: orgId },
    });
  },
};
