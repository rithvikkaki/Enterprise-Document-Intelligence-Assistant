import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  ArrowLeft,
  FileText,
  Clock,
  CheckCircle2,
  AlertTriangle,
  RotateCw,
  Layers,
  Sparkles,
  Database,
} from 'lucide-react';
import MainLayout from '../components/layout/MainLayout';
import StatusBadge from '../components/common/StatusBadge';
import { useAuth } from '../context/AuthContext';
import { documentsApi } from '../api/documents';
import { ProcessingJob, Document } from '../types';
import { formatDate } from '../lib/utils';

export default function DocumentDetailPage() {
  const { documentId } = useParams<{ documentId: string }>();
  const { activeOrg } = useAuth();
  const queryClient = useQueryClient();

  const { data: documents = [] } = useQuery<Document[]>({
    queryKey: ['documents', activeOrg?.id],
    queryFn: () => documentsApi.list(activeOrg!.id),
    enabled: !!activeOrg,
  });

  const doc = documents.find((d) => d.id === documentId);

  const {
    data: job,
    isLoading: jobLoading,
    refetch,
  } = useQuery<ProcessingJob>({
    queryKey: ['document-job', activeOrg?.id, documentId],
    queryFn: () => documentsApi.getStatus(activeOrg!.id, documentId!),
    enabled: !!activeOrg && !!documentId,
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      return status === 'PROCESSING' || status === 'QUEUED' || status === 'UPLOADED'
        ? 2000
        : false;
    },
  });

  const retryMutation = useMutation({
    mutationFn: () => documentsApi.retry(activeOrg!.id, documentId!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['document-job', activeOrg?.id, documentId] });
      queryClient.invalidateQueries({ queryKey: ['documents', activeOrg?.id] });
      refetch();
    },
    onError: (err: any) => {
      alert(err.response?.data?.error?.message || 'Failed to retry processing job.');
    },
  });

  const stages = [
    { name: 'Upload & Storage', icon: FileText, done: true },
    {
      name: 'Text Extraction & OCR',
      icon: Layers,
      done: (job?.progress_percentage ?? 0) >= 30 || job?.status === 'COMPLETED',
    },
    {
      name: 'Token-Aware Chunking',
      icon: Sparkles,
      done: (job?.progress_percentage ?? 0) >= 60 || job?.status === 'COMPLETED',
    },
    {
      name: 'Vector Embeddings (MiniLM-L6)',
      icon: Database,
      done: (job?.progress_percentage ?? 0) >= 85 || job?.status === 'COMPLETED',
    },
    {
      name: 'pgvector & FTS Indexing',
      icon: CheckCircle2,
      done: job?.status === 'COMPLETED',
    },
  ];

  return (
    <MainLayout pageTitle="Document Details">
      <div className="mb-6">
        <Link
          to="/documents"
          className="inline-flex items-center gap-1.5 text-sm font-medium text-slate-500 hover:text-slate-800 transition-colors"
        >
          <ArrowLeft size={16} /> Back to Documents
        </Link>
      </div>

      <div className="flex flex-col lg:flex-row gap-6">
        {/* Left Column: Metadata and Processing Status */}
        <div className="flex-1 space-y-6">
          {/* Header Card */}
          <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
            <div className="flex items-start justify-between gap-4 mb-4">
              <div className="flex items-center gap-3">
                <div className="p-3 bg-sky-50 text-sky-600 rounded-xl">
                  <FileText size={24} />
                </div>
                <div>
                  <h2 className="text-xl font-bold text-slate-900 leading-snug">
                    {doc?.title || 'Document Record'}
                  </h2>
                  <p className="text-xs text-slate-400 mt-0.5">ID: {documentId}</p>
                </div>
              </div>
              <StatusBadge status={job?.status || (doc?.current_version_id ? 'COMPLETED' : 'PROCESSING')} />
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-4 border-t border-slate-100 text-sm">
              <div>
                <p className="text-xs text-slate-400">MIME Type</p>
                <p className="font-semibold text-slate-800 truncate">{doc?.mime_type || '—'}</p>
              </div>
              <div>
                <p className="text-xs text-slate-400">Created</p>
                <p className="font-semibold text-slate-800">
                  {doc ? formatDate(doc.created_at) : '—'}
                </p>
              </div>
              <div>
                <p className="text-xs text-slate-400">Retry Count</p>
                <p className="font-semibold text-slate-800">{job?.retry_count ?? 0}</p>
              </div>
              <div>
                <p className="text-xs text-slate-400">Current Version</p>
                <p className="font-semibold text-slate-800">
                  {doc?.current_version_id ? 'v1' : 'Pending'}
                </p>
              </div>
            </div>
          </div>

          {/* Processing Progress Card */}
          <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-base font-semibold text-slate-900">
                Asynchronous Processing Pipeline
              </h3>
              {job?.status === 'FAILED' && (
                <button
                  onClick={() => retryMutation.mutate()}
                  disabled={retryMutation.isPending}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-red-50 text-red-700 hover:bg-red-100 text-xs font-semibold transition-colors"
                >
                  <RotateCw size={13} className={retryMutation.isPending ? 'animate-spin' : ''} />
                  Retry Processing
                </button>
              )}
            </div>

            {/* Progress Bar */}
            <div className="mb-6 space-y-1.5">
              <div className="flex justify-between text-xs font-semibold text-slate-600">
                <span>Pipeline Completion</span>
                <span>{job?.progress_percentage ?? (job?.status === 'COMPLETED' ? 100 : 0)}%</span>
              </div>
              <div className="w-full bg-slate-100 rounded-full h-2.5 overflow-hidden">
                <div
                  className={`h-2.5 rounded-full transition-all duration-300 ${
                    job?.status === 'FAILED'
                      ? 'bg-red-500'
                      : job?.status === 'COMPLETED'
                      ? 'bg-emerald-500'
                      : 'bg-sky-600'
                  }`}
                  style={{
                    width: `${
                      job?.progress_percentage ?? (job?.status === 'COMPLETED' ? 100 : 0)
                    }%`,
                  }}
                />
              </div>
            </div>

            {/* Error Message if Failed */}
            {job?.error_message && (
              <div className="mb-6 p-4 rounded-xl bg-red-50 border border-red-200 text-sm text-red-700 flex items-start gap-3">
                <AlertTriangle size={18} className="shrink-0 mt-0.5" />
                <div>
                  <p className="font-semibold">Pipeline Failure: {job.error_code || 'Error'}</p>
                  <p className="text-xs mt-0.5">{job.error_message}</p>
                </div>
              </div>
            )}

            {/* Stage Steps */}
            <div className="space-y-3">
              {stages.map((stage, idx) => {
                const Icon = stage.icon;
                return (
                  <div
                    key={stage.name}
                    className={`flex items-center gap-3 p-3 rounded-xl border transition-colors ${
                      stage.done
                        ? 'border-emerald-200 bg-emerald-50/40 text-emerald-800'
                        : 'border-slate-200 bg-slate-50/50 text-slate-400'
                    }`}
                  >
                    <div
                      className={`w-7 h-7 rounded-lg flex items-center justify-center shrink-0 ${
                        stage.done ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-200 text-slate-500'
                      }`}
                    >
                      <Icon size={14} />
                    </div>
                    <span className="text-sm font-medium flex-1">{stage.name}</span>
                    <span className="text-xs font-semibold">
                      {stage.done ? '✓ Done' : `Step ${idx + 1}`}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Right Column: Execution Metadata */}
        <div className="w-full lg:w-80 space-y-6">
          <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm space-y-4">
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">
              Celery Worker Telemetry
            </h4>

            <div className="space-y-3 text-xs">
              <div>
                <p className="text-slate-400">Job ID</p>
                <p className="font-mono text-slate-800 truncate">{job?.job_id || '—'}</p>
              </div>
              <div>
                <p className="text-slate-400">Started At</p>
                <p className="text-slate-800">
                  {job?.started_at ? formatDate(job.started_at) : '—'}
                </p>
              </div>
              <div>
                <p className="text-slate-400">Completed At</p>
                <p className="text-slate-800">
                  {job?.completed_at ? formatDate(job.completed_at) : '—'}
                </p>
              </div>
              <div>
                <p className="text-slate-400">Embedding Model</p>
                <p className="font-medium text-slate-800">sentence-transformers/all-MiniLM-L6-v2</p>
              </div>
              <div>
                <p className="text-slate-400">Dimensions</p>
                <p className="font-medium text-slate-800">384-d Dense Vector (pgvector HNSW)</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </MainLayout>
  );
}
