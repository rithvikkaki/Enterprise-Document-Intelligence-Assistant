import { api } from '../lib/axios';
import { Document, ProcessingJob } from '../types';

export const documentsApi = {
  list: async (orgId: string, projectId?: string): Promise<Document[]> => {
    const params: Record<string, string> = { organization_id: orgId };
    if (projectId) params.project_id = projectId;
    const response = await api.get('/documents', { params });
    return response.data;
  },

  upload: async (
    orgId: string,
    projectId: string,
    file: File,
    existingDocumentId?: string,
    idempotencyKey?: string,
    onProgress?: (percent: number) => void
  ): Promise<{ document_id: string; version_id: string; job_id: string; status: string }> => {
    const formData = new FormData();
    formData.append('organization_id', orgId);
    formData.append('project_id', projectId);
    formData.append('file', file);
    if (existingDocumentId) {
      formData.append('document_id', existingDocumentId);
    }

    const headers: Record<string, string> = {};
    if (idempotencyKey) {
      headers['Idempotency-Key'] = idempotencyKey;
    }

    const response = await api.post('/documents/upload', formData, {
      headers,
      onUploadProgress: (evt) => {
        if (evt.total && onProgress) {
          const percent = Math.round((evt.loaded * 100) / evt.total);
          onProgress(percent);
        }
      },
    });
    return response.data;
  },

  getStatus: async (orgId: string, documentId: string): Promise<ProcessingJob> => {
    const response = await api.get(`/documents/${documentId}/status`, {
      params: { organization_id: orgId },
    });
    return response.data;
  },

  retry: async (orgId: string, documentId: string): Promise<void> => {
    await api.post(`/documents/${documentId}/retry`, null, {
      params: { organization_id: orgId },
    });
  },
};
