import { api } from '../lib/axios';
import { Organization, Member, OrganizationStats, Role } from '../types';

export const organizationsApi = {
  list: async (): Promise<Organization[]> => {
    const response = await api.get('/organizations');
    return response.data;
  },

  create: async (data: { name: string; slug?: string }): Promise<Organization> => {
    const response = await api.post('/organizations', data);
    return response.data;
  },

  get: async (id: string): Promise<Organization> => {
    const response = await api.get(`/organizations/${id}`);
    return response.data;
  },

  getStats: async (id: string): Promise<OrganizationStats> => {
    const response = await api.get(`/organizations/${id}/stats`);
    return response.data;
  },

  listMembers: async (orgId: string): Promise<Member[]> => {
    const response = await api.get(`/organizations/${orgId}/members`);
    return response.data;
  },

  addMember: async (orgId: string, data: { email: string; role: Role }): Promise<Member> => {
    const response = await api.post(`/organizations/${orgId}/members`, data);
    return response.data;
  },

  updateMemberRole: async (orgId: string, memberId: string, role: Role): Promise<Member> => {
    const response = await api.patch(`/organizations/${orgId}/members/${memberId}`, { role });
    return response.data;
  },

  removeMember: async (orgId: string, memberId: string): Promise<void> => {
    await api.delete(`/organizations/${orgId}/members/${memberId}`);
  },
};
