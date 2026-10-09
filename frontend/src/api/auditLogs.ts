import { api } from '../lib/axios';
import { AuditLog } from '../types';

export const auditLogsApi = {
  list: async (orgId: string, limit = 50): Promise<AuditLog[]> => {
    const response = await api.get(`/organizations/${orgId}/audit-logs`, {
      params: { limit },
    });
    return response.data;
  },
};
