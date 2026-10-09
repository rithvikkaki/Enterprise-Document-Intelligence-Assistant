import React from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import {
  FileText,
  CheckCircle2,
  Clock,
  XCircle,
  FolderOpen,
  Users,
  Upload,
  Search,
  ArrowRight,
} from 'lucide-react';
import MainLayout from '../components/layout/MainLayout';
import StatusBadge from '../components/common/StatusBadge';
import { useAuth } from '../context/AuthContext';
import { organizationsApi } from '../api/organizations';
import { documentsApi } from '../api/documents';
import { OrganizationStats, Document } from '../types';
import { formatDate } from '../lib/utils';

export default function DashboardPage() {
  const { activeOrg, activeProject } = useAuth();

  const { data: stats, isLoading: statsLoading } = useQuery<OrganizationStats>({
    queryKey: ['org-stats', activeOrg?.id],
    queryFn: () => organizationsApi.getStats(activeOrg!.id),
    enabled: !!activeOrg,
    refetchInterval: 10000,
  });

  const { data: recentDocs = [], isLoading: docsLoading } = useQuery<Document[]>({
    queryKey: ['recent-documents', activeOrg?.id, activeProject?.id],
    queryFn: () => documentsApi.list(activeOrg!.id, activeProject?.id),
    enabled: !!activeOrg,
    refetchInterval: 5000,
  });

  if (!activeOrg) {
    return (
      <MainLayout pageTitle="Dashboard">
        <div className="bg-white rounded-xl border border-slate-200 p-8 text-center max-w-md mx-auto mt-12">
          <h3 className="text-base font-semibold text-slate-900 mb-2">No Organization Selected</h3>
          <p className="text-sm text-slate-500 mb-4">
            Please select an organization context to view documents and analytics.
          </p>
          <Link
            to="/org-select"
            className="inline-flex items-center px-4 py-2 bg-sky-600 text-white rounded-lg text-sm font-medium hover:bg-sky-700"
          >
            Select Organization
          </Link>
        </div>
      </MainLayout>
    );
  }

  const statCards = [
    {
      title: 'Total Documents',
      value: stats?.total_documents ?? 0,
      icon: FileText,
      color: 'text-sky-600',
      bg: 'bg-sky-50',
    },
    {
      title: 'Completed',
      value: stats?.completed_documents ?? 0,
      icon: CheckCircle2,
      color: 'text-emerald-600',
      bg: 'bg-emerald-50',
    },
    {
      title: 'Processing',
      value: stats?.processing_documents ?? 0,
      icon: Clock,
      color: 'text-amber-600',
      bg: 'bg-amber-50',
    },
    {
      title: 'Failed',
      value: stats?.failed_documents ?? 0,
      icon: XCircle,
      color: 'text-red-600',
      bg: 'bg-red-50',
    },
    {
      title: 'Projects',
      value: stats?.total_projects ?? 0,
      icon: FolderOpen,
      color: 'text-indigo-600',
      bg: 'bg-indigo-50',
    },
    {
      title: 'Team Members',
      value: stats?.total_members ?? 0,
      icon: Users,
      color: 'text-purple-600',
      bg: 'bg-purple-50',
    },
  ];

  return (
    <MainLayout pageTitle={`Dashboard — ${activeOrg.name}`}>
      {/* Top Banner / Welcome */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
        <div>
          <h2 className="text-xl font-bold text-slate-900">Knowledge Overview</h2>
          <p className="text-sm text-slate-500">
            Real-time status of document ingestion, semantic embeddings, and project collections.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Link
            to="/search"
            className="inline-flex items-center gap-1.5 px-3.5 py-2 bg-white border border-slate-200 rounded-lg text-sm font-medium text-slate-700 hover:bg-slate-50 transition-colors shadow-sm"
          >
            <Search size={15} />
            Hybrid Search
          </Link>
          <Link
            to="/documents"
            className="inline-flex items-center gap-1.5 px-3.5 py-2 bg-sky-600 text-white rounded-lg text-sm font-medium hover:bg-sky-700 transition-colors shadow-sm"
          >
            <Upload size={15} />
            Upload Document
          </Link>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-8">
        {statCards.map((c) => {
          const Icon = c.icon;
          return (
            <div
              key={c.title}
              className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm"
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-medium text-slate-500">{c.title}</span>
                <div className={`p-1.5 rounded-lg ${c.bg} ${c.color}`}>
                  <Icon size={16} />
                </div>
              </div>
              <p className="text-2xl font-bold text-slate-900">
                {statsLoading ? '—' : c.value}
              </p>
            </div>
          );
        })}
      </div>

      {/* Recent Documents & Pipeline Activity */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between">
          <div>
            <h3 className="text-base font-semibold text-slate-900">Recent Documents</h3>
            <p className="text-xs text-slate-400">
              Latest documents uploaded and processed across active projects
            </p>
          </div>
          <Link
            to="/documents"
            className="text-xs font-medium text-sky-600 hover:text-sky-700 flex items-center gap-1"
          >
            View all <ArrowRight size={13} />
          </Link>
        </div>

        {docsLoading ? (
          <div className="p-8 text-center text-sm text-slate-400">Loading documents...</div>
        ) : recentDocs.length === 0 ? (
          <div className="p-12 text-center">
            <FileText className="mx-auto h-10 w-10 text-slate-300 mb-2" />
            <p className="text-sm font-medium text-slate-700">No documents yet</p>
            <p className="text-xs text-slate-400 mt-1 mb-4">
              Upload PDF, DOCX, XLSX, HTML, or images to begin indexing.
            </p>
            <Link
              to="/documents"
              className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-sky-600 text-white rounded-lg text-xs font-medium hover:bg-sky-700"
            >
              <Upload size={14} /> Upload First File
            </Link>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-sm">
              <thead>
                <tr className="border-b border-slate-100 bg-slate-50/75 text-xs text-slate-500 uppercase tracking-wider font-semibold">
                  <th className="py-3 px-6">Document Title</th>
                  <th className="py-3 px-6">MIME Type</th>
                  <th className="py-3 px-6">Status</th>
                  <th className="py-3 px-6">Uploaded At</th>
                  <th className="py-3 px-6 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {recentDocs.slice(0, 8).map((doc) => (
                  <tr key={doc.id} className="hover:bg-slate-50/60 transition-colors">
                    <td className="py-3.5 px-6 font-medium text-slate-800 flex items-center gap-2">
                      <FileText size={16} className="text-slate-400 shrink-0" />
                      <span className="truncate max-w-xs">{doc.title}</span>
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
                        className="text-xs font-medium text-sky-600 hover:text-sky-700"
                      >
                        Details
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </MainLayout>
  );
}
