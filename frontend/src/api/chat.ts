import { api } from '../lib/axios';
import { ChatResponse } from '../types';

export const chatApi = {
  ask: async (
    orgId: string,
    question: string,
    projectId: string,
    documentId?: string
  ): Promise<ChatResponse> => {
    const response = await api.post('/chat', {
      organization_id: orgId,
      project_id: projectId,
      question,
      document_id: documentId || null,
    });
    return response.data;
  },
};
