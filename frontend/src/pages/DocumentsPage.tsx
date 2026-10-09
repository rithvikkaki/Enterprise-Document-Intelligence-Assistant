import React, { useState, useRef } from 'react';
import { Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  FileText,
  Upload,
  Search,
  Filter,
  AlertCircle,
  CheckCircle2,
  FileCode,
  FileSpreadsheet,
  FileArchive,
  Image as ImageIcon,
} from 'lucide-react';
import MainLayout from '../components/layout/MainLayout';
import Modal from '../components/common/Modal';
import StatusBadge from '../components/common/StatusBadge';
import { useAuth } from '../context/AuthContext';
import { documentsApi } from '../api/documents';
import { projectsApi } from '../api/projects';
import { Document, Project } from '../types';
import { formatDate } from '../lib/utils';

function getFileIcon(mimeType: string) {
  if (mimeType.includes('pdf')) return <FileText className="text-red-500 shrink-0" size={18} />;
  if (mimeType.includes('spreadsheet') || mimeType.includes('excel') || mimeType.includes('csv'))
    return <FileSpreadsheet className="text-emerald-500 shrink-0" size={18} />;
  if (mimeType.includes('zip') || mimeType.includes('archive'))
    return <FileArchive className="text-amber-500 shrink-0" size={18} />;
  if (mimeType.includes('image')) return <ImageIcon className="text-purple-500 shrink-0" size={18} />;
  return <FileCode className="text-sky-500 shrink-0" size={18} />;
}

export default function DocumentsPage() {
  const queryClient = useQueryClient();
  const { activeOrg, activeProject } = useAuth();

  const [searchQuery, setSearchQuery] = useState('');
  const [selectedProjectId, setSelectedProjectId] = useState<string>(activeProject?.id || '');
  const [isUploadOpen, setIsUploadOpen] = useState(false);

  // Upload Form state
  const [uploadProject, setUploadProject] = useState<string>(activeProject?.id || '');
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploadProgress, setUploadProgress] = useState<number | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const { data: projects = [] } = useQuery<Project[]>({
    queryKey: ['projects', activeOrg?.id],
    queryFn: () => projectsApi.list(activeOrg!.id),
    enabled: !!activeOrg,
  });

  const { data: documents = [], isLoading } = useQuery<Document[]>({
    queryKey: ['documents', activeOrg?.id, selectedProjectId || undefined],
    queryFn: () => documentsApi.list(activeOrg!.id, selectedProjectId || undefined),
    enabled: !!activeOrg,
    refetchInterval: (query) => {
      const data = query.state.data;
      const hasPending = data?.some((d) => !d.current_version_id);
      return hasPending ? 3000 : 10000;
    },
  });

  const uploadMutation = useMutation({
    mutationFn: async () => {
      if (!uploadFile || !uploadProject) throw new Error('File and project are required.');
      const idempotencyKey = `up_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;
      return documentsApi.upload(
        activeOrg!.id,
        uploadProject,
        uploadFile,
        undefined,
        idempotencyKey,
        (percent) => setUploadProgress(percent)
      );
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents', activeOrg?.id] });
      queryClient.invalidateQueries({ queryKey: ['org-stats', activeOrg?.id] });
      setIsUploadOpen(false);
      setUploadFile(null);
      setUploadProgress(null);
      setUploadError(null);
    },
    onError: (err: any) => {
      setUploadProgress(null);
      setUploadError(err.response?.data?.error?.message || err.message || 'Upload failed.');
    },
  });

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setUploadFile(e.dataTransfer.files[0]);
    }
  };

  const filteredDocs = documents.filter((d) =>
    d.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <MainLayout pageTitle="Documents">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
        <div>
          <h2 className="text-xl font-bold text-slate-900">Document Repository</h2>
          <p className="text-sm text-slate-500">
            Upload, inspect extracted chunks, and monitor asynchronous embedding pipeline.
          </p>
        </div>
        <button
          onClick={() => {
            setUploadProject(selectedProjectId || (projects[0]?.id ?? ''));
            setIsUploadOpen(true);
          }}
          className="inline-flex items-center gap-1.5 px-4 py-2 bg-sky-600 text-white rounded-lg text-sm font-medium hover:bg-sky-700 transition-colors shadow-sm cursor-pointer"
        >
          <Upload size={16} /> Upload Document
        </button>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm mb-6 flex flex-col md:flex-row gap-3 items-center justify-between">
        <div className="relative w-full md:w-80">
          <Search size={16} className="absolute left-3 top-2.5 text-slate-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Filter by title..."
            className="w-full pl-9 pr-3 py-1.5 border border-slate-200 rounded-lg text-sm placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-sky-500"
          />
        </div>

        <div className="flex items-center gap-2 w-full md:w-auto">
          <Filter size={15} className="text-slate-400 shrink-0" />
          <select
            value={selectedProjectId}
            onChange={(e) => setSelectedProjectId(e.target.value)}
            className="w-full md:w-56 py-1.5 px-2.5 border border-slate-200 rounded-lg text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-sky-500 bg-white"
          >
            <option value="">All Projects</option>
            {projects.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Documents Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        {isLoading ? (
          <div className="p-12 text-center text-sm text-slate-400">Loading documents...</div>
        ) : filteredDocs.length === 0 ? (
          <div className="p-12 text-center">
            <FileText className="mx-auto h-12 w-12 text-slate-300 mb-3" />
            <h3 className="text-base font-semibold text-slate-800">No documents found</h3>
            <p className="text-sm text-slate-500 mt-1 mb-6">
              {searchQuery
                ? 'No documents match your filter.'
                : 'Upload files (PDF, DOCX, XLSX, HTML, EML, Images, ZIP) to start processing.'}
            </p>
            <button
              onClick={() => {
                setUploadProject(selectedProjectId || (projects[0]?.id ?? ''));
                setIsUploadOpen(true);
              }}
              className="inline-flex items-center gap-2 px-4 py-2 bg-sky-600 text-white rounded-lg text-sm font-medium hover:bg-sky-700"
            >
              <Upload size={16} /> Upload Document
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-sm">
              <thead>
                <tr className="border-b border-slate-100 bg-slate-50/75 text-xs text-slate-500 uppercase tracking-wider font-semibold">
                  <th className="py-3 px-6">File Name</th>
                  <th className="py-3 px-6">MIME Type</th>
                  <th className="py-3 px-6">Status</th>
                  <th className="py-3 px-6">Uploaded At</th>
                  <th className="py-3 px-6 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {filteredDocs.map((doc) => (
                  <tr key={doc.id} className="hover:bg-slate-50/60 transition-colors">
                    <td className="py-3.5 px-6 font-medium text-slate-800 flex items-center gap-3">
                      {getFileIcon(doc.mime_type)}
                      <span className="truncate max-w-sm">{doc.title}</span>
                    </td>
                    <td className="py-3.5 px-6 text-slate-500 text-xs">
                      {doc.mime_type}
                    </td>
                    <td className="py-3.5 px-6">
                      <StatusBadge status={doc.current_version_id ? 'COMPLETED' : 'PROCESSING'} />
                    </td>
                    <td className="py-3.5 px-6 text-slate-500 text-xs">
                      {formatDate(doc.created_at)}
                    </td>
                    <td className="py-3.5 px-6 text-right">
                      <Link
                        to={`/documents/${doc.id}`}
                        className="text-xs font-semibold text-sky-600 hover:text-sky-700"
                      >
                        Inspect
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Upload Document Modal */}
      <Modal
        isOpen={isUploadOpen}
        onClose={() => {
          setIsUploadOpen(false);
          setUploadFile(null);
          setUploadError(null);
        }}
        title="Upload Document for Ingestion"
        size="lg"
      >
        <div className="space-y-4">
          {uploadError && (
            <div className="p-3 rounded-lg bg-red-50 border border-red-200 flex items-center gap-2 text-sm text-red-700">
              <AlertCircle size={16} className="shrink-0" />
              <span>{uploadError}</span>
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Target Project *
            </label>
            <select
              value={uploadProject}
              onChange={(e) => setUploadProject(e.target.value)}
              className="w-full py-2 px-3 border border-slate-300 rounded-lg text-sm bg-white focus:ring-2 focus:ring-sky-500 focus:outline-none"
            >
              <option value="" disabled>
                Select a project...
              </option>
              {projects.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">File</label>
            <div
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
              className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-colors ${
                isDragging
                  ? 'border-sky-500 bg-sky-50/50'
                  : 'border-slate-300 hover:border-slate-400 bg-slate-50/50'
              }`}
            >
              <input
                ref={fileInputRef}
                type="file"
                className="hidden"
                onChange={(e) => {
                  if (e.target.files && e.target.files[0]) {
                    setUploadFile(e.target.files[0]);
                  }
                }}
              />
              <Upload className="mx-auto h-10 w-10 text-slate-400 mb-2" />
              {uploadFile ? (
                <div>
                  <p className="text-sm font-semibold text-slate-800">{uploadFile.name}</p>
                  <p className="text-xs text-slate-500 mt-0.5">
                    {(uploadFile.size / 1024).toFixed(1)} KB • Click to change
                  </p>
                </div>
              ) : (
                <div>
                  <p className="text-sm font-medium text-slate-700">
                    Drag and drop file here, or click to browse
                  </p>
                  <p className="text-xs text-slate-400 mt-1">
                    PDF, DOCX, PPTX, XLSX, HTML, EML, TXT, Images, ZIP
                  </p>
                </div>
              )}
            </div>
          </div>

          {uploadProgress !== null && (
            <div className="space-y-1">
              <div className="flex justify-between text-xs text-slate-500 font-medium">
                <span>Uploading to storage...</span>
                <span>{uploadProgress}%</span>
              </div>
              <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                <div
                  className="bg-sky-600 h-2 rounded-full transition-all duration-200"
                  style={{ width: `${uploadProgress}%` }}
                />
              </div>
            </div>
          )}

          <div className="flex justify-end gap-2 pt-3 border-t border-slate-100">
            <button
              type="button"
              onClick={() => setIsUploadOpen(false)}
              className="px-4 py-2 border border-slate-200 rounded-lg text-sm text-slate-700 hover:bg-slate-50"
            >
              Cancel
            </button>
            <button
              type="button"
              onClick={() => uploadMutation.mutate()}
              disabled={uploadMutation.isPending || !uploadFile || !uploadProject}
              className="px-4 py-2 bg-sky-600 text-white rounded-lg text-sm font-medium hover:bg-sky-700 disabled:opacity-50 flex items-center gap-1.5"
            >
              <Upload size={15} />
              {uploadMutation.isPending ? 'Queuing Job...' : 'Upload and Process'}
            </button>
          </div>
        </div>
      </Modal>
    </MainLayout>
  );
}
