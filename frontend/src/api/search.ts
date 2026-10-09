import { api } from '../lib/axios';
import { HybridSearchResponse } from '../types';

export const searchApi = {
  search: async (
    orgId: string,
    projectId: string,
    query: string,
    limit = 10
  ): Promise<HybridSearchResponse> => {
    const response = await api.get('/search', {
      params: {
        organization_id: orgId,
        project_id: projectId,
        query,
        limit,
      },
    });
    return response.data;
  },
};
