import { api } from '../lib/axios';
import { APIKey, APIKeyCreateResponse } from '../types';

export const apiKeysApi = {
  list: async (orgId: string): Promise<APIKey[]> => {
    const response = await api.get('/api-keys', {
      params: { organization_id: orgId },
    });
    return response.data;
  },

  create: async (data: {
    organization_id: string;
    name: string;
    scopes: string[];
    expires_in_days?: number;
  }): Promise<APIKeyCreateResponse> => {
    const response = await api.post('/api-keys', data);
    return response.data;
  },

  revoke: async (keyId: string, orgId: string): Promise<void> => {
    await api.delete(`/api-keys/${keyId}`, {
      params: { organization_id: orgId },
    });
  },
};
