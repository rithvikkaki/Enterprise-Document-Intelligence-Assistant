export type Role = 'OWNER' | 'ADMIN' | 'EDITOR' | 'VIEWER';

export type ProcessingStatus = 'QUEUED' | 'UPLOADED' | 'PROCESSING' | 'COMPLETED' | 'FAILED';

export interface User {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface Organization {
  id: string;
  name: string;
  slug: string;
  created_at: string;
  updated_at: string;
}

export interface Member {
  id: string;
  user_id: string;
  organization_id: string;
  role: Role;
  user_email: string;
  user_full_name: string;
  created_at: string;
}

export interface Project {
  id: string;
  organization_id: string;
  name: string;
  slug?: string | null;
  description?: string | null;
  created_at: string;
  updated_at: string;
}

export interface Document {
  id: string;
  organization_id: string;
  project_id: string;
  title: string;
  mime_type: string;
  current_version_id?: string | null;
  created_at: string;
  updated_at: string;
}

export interface DocumentVersion {
  id: string;
  document_id: string;
  version_number: number;
  original_filename: string;
  file_size: number;
  mime_type: string;
  checksum: string;
  processing_status: ProcessingStatus;
  detected_language?: string | null;
  created_at: string;
}

export interface ProcessingJob {
  job_id: string;
  document_version_id: string;
  status: ProcessingStatus;
  progress_percentage: number;
  error_code?: string | null;
  error_message?: string | null;
  retry_count: number;
  started_at?: string | null;
  completed_at?: string | null;
  failed_at?: string | null;
}

export interface SearchResultChunk {
  chunk_id: string;
  document_id: string;
  document_version_id: string;
  document_name: string;
  version_number: number;
  chunk_index: number;
  content: string;
  score: number;
  metadata: Record<string, unknown>;
}

export interface HybridSearchResponse {
  query: string;
  organization_id: string;
  project_id: string;
  total_results: number;
  results: SearchResultChunk[];
}

export interface SourceCitation {
  document_id: string;
  document_name: string;
  document_version: number;
  page?: number | null;
  chunk_id: string;
  snippet: string;
}

export interface ChatResponse {
  answer: string;
  sources: SourceCitation[];
  question: string;
  organization_id: string;
  project_id: string;
}

export interface APIKey {
  id: string;
  organization_id: string;
  name: string;
  key_prefix: string;
  scopes: string[];
  created_by_id: string;
  expires_at?: string | null;
  revoked_at?: string | null;
  created_at: string;
}

export interface APIKeyCreateResponse {
  id: string;
  organization_id: string;
  name: string;
  key_prefix: string;
  secret_key: string; // Shown only once
  scopes: string[];
  expires_at?: string | null;
  created_at: string;
}

export interface AuditLog {
  id: string;
  organization_id?: string | null;
  user_id?: string | null;
  action: string;
  resource_type: string;
  resource_id?: string | null;
  request_id?: string | null;
  ip_address?: string | null;
  metadata_json?: Record<string, unknown> | null;
  created_at: string;
}

export interface OrganizationStats {
  total_documents: number;
  completed_documents: number;
  processing_documents: number;
  failed_documents: number;
  total_projects: number;
  total_members: number;
}
