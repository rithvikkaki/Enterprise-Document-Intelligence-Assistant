import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { FolderOpen, Plus, Trash2, Check, AlertCircle } from 'lucide-react';
import MainLayout from '../components/layout/MainLayout';
import Modal from '../components/common/Modal';
import { useAuth } from '../context/AuthContext';
import { projectsApi } from '../api/projects';
import { Project } from '../types';
import { formatDate } from '../lib/utils';

export default function ProjectsPage() {
  const queryClient = useQueryClient();
  const { activeOrg, activeProject, setActiveProject } = useAuth();

  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const { data: projects = [], isLoading } = useQuery<Project[]>({
    queryKey: ['projects', activeOrg?.id],
    queryFn: () => projectsApi.list(activeOrg!.id),
    enabled: !!activeOrg,
  });

  const createMutation = useMutation({
    mutationFn: (data: { name: string; description?: string }) =>
      projectsApi.create(activeOrg!.id, data),
    onSuccess: (newProj) => {
      queryClient.invalidateQueries({ queryKey: ['projects', activeOrg?.id] });
      setIsCreateOpen(false);
      setName('');
      setDescription('');
      if (!activeProject) setActiveProject(newProj);
    },
    onError: (err: any) => {
      setErrorMessage(err.response?.data?.error?.message || 'Failed to create project.');
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (projectId: string) => projectsApi.delete(activeOrg!.id, projectId),
    onSuccess: (_, deletedId) => {
      queryClient.invalidateQueries({ queryKey: ['projects', activeOrg?.id] });
      if (activeProject?.id === deletedId) {
        setActiveProject(null);
      }
    },
    onError: (err: any) => {
      alert(err.response?.data?.error?.message || 'Failed to delete project. Admin permissions required.');
    },
  });

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;
    createMutation.mutate({ name: name.trim(), description: description.trim() || undefined });
  };

  return (
    <MainLayout pageTitle="Projects">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
        <div>
          <h2 className="text-xl font-bold text-slate-900">Project Collections</h2>
          <p className="text-sm text-slate-500">
            Organize documents into isolated knowledge bases for search and RAG assistant queries.
          </p>
        </div>
        <button
          onClick={() => setIsCreateOpen(true)}
          className="inline-flex items-center gap-1.5 px-4 py-2 bg-sky-600 text-white rounded-lg text-sm font-medium hover:bg-sky-700 transition-colors shadow-sm"
        >
          <Plus size={16} /> New Project
        </button>
      </div>

      {isLoading ? (
        <div className="py-12 text-center text-sm text-slate-400">Loading projects...</div>
      ) : projects.length === 0 ? (
        <div className="bg-white rounded-xl border border-slate-200 p-12 text-center max-w-lg mx-auto">
          <FolderOpen className="mx-auto h-12 w-12 text-slate-300 mb-3" />
          <h3 className="text-base font-semibold text-slate-800">No projects yet</h3>
          <p className="text-sm text-slate-500 mt-1 mb-6">
            Create your first project to organize documents and scope semantic queries.
          </p>
          <button
            onClick={() => setIsCreateOpen(true)}
            className="inline-flex items-center gap-2 px-4 py-2 bg-sky-600 text-white rounded-lg text-sm font-medium hover:bg-sky-700"
          >
            <Plus size={16} /> Create Project
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {projects.map((proj) => {
            const isActive = activeProject?.id === proj.id;
            return (
              <div
                key={proj.id}
                className={`bg-white rounded-xl border p-5 flex flex-col justify-between transition-all duration-150 ${
                  isActive
                    ? 'border-sky-500 shadow-md ring-1 ring-sky-500/20'
                    : 'border-slate-200 hover:border-slate-300 shadow-sm'
                }`}
              >
                <div>
                  <div className="flex items-start justify-between gap-2 mb-3">
                    <div className="flex items-center gap-2.5">
                      <div
                        className={`w-9 h-9 rounded-lg flex items-center justify-center ${
                          isActive ? 'bg-sky-100 text-sky-700' : 'bg-slate-100 text-slate-600'
                        }`}
                      >
                        <FolderOpen size={18} />
                      </div>
                      <div>
                        <h4 className="text-sm font-semibold text-slate-900 leading-snug">
                          {proj.name}
                        </h4>
                        <span className="text-xs text-slate-400">slug: {proj.slug}</span>
                      </div>
                    </div>
                    {isActive && (
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-semibold bg-sky-100 text-sky-800">
                        <Check size={12} /> Active
                      </span>
                    )}
                  </div>

                  <p className="text-xs text-slate-600 line-clamp-2 min-h-[32px] mb-4">
                    {proj.description || 'No description provided.'}
                  </p>
                </div>

                <div className="pt-3 border-t border-slate-100 flex items-center justify-between">
                  <span className="text-xs text-slate-400">
                    Created {formatDate(proj.created_at)}
                  </span>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() =>
                        deleteMutation.mutate(proj.id)
                      }
                      title="Delete Project"
                      className="p-1.5 rounded-lg text-slate-400 hover:text-red-600 hover:bg-red-50 transition-colors"
                    >
                      <Trash2 size={14} />
                    </button>
                    {!isActive ? (
                      <button
                        onClick={() => setActiveProject(proj)}
                        className="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-xs font-medium transition-colors"
                      >
                        Select
                      </button>
                    ) : (
                      <button
                        onClick={() => setActiveProject(null)}
                        className="px-3 py-1.5 bg-sky-50 text-sky-700 rounded-lg text-xs font-medium"
                      >
                        Deselect
                      </button>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Create Project Modal */}
      <Modal
        isOpen={isCreateOpen}
        onClose={() => {
          setIsCreateOpen(false);
          setErrorMessage(null);
        }}
        title="Create New Project"
      >
        <form onSubmit={handleCreate} className="space-y-4">
          {errorMessage && (
            <div className="p-3 rounded-lg bg-red-50 border border-red-200 flex items-center gap-2 text-sm text-red-700">
              <AlertCircle size={16} className="shrink-0" />
              <span>{errorMessage}</span>
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Project Name *
            </label>
            <input
              type="text"
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. Legal Contracts 2026"
              className="block w-full px-3 py-2 border border-slate-300 rounded-lg text-sm placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Description (optional)
            </label>
            <textarea
              rows={3}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Brief description of the documents stored here..."
              className="block w-full px-3 py-2 border border-slate-300 rounded-lg text-sm placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-transparent"
            />
          </div>

          <div className="flex justify-end gap-2 pt-2">
            <button
              type="button"
              onClick={() => setIsCreateOpen(false)}
              className="px-4 py-2 border border-slate-200 rounded-lg text-sm text-slate-700 hover:bg-slate-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={createMutation.isPending || !name.trim()}
              className="px-4 py-2 bg-sky-600 text-white rounded-lg text-sm font-medium hover:bg-sky-700 disabled:opacity-50"
            >
              {createMutation.isPending ? 'Creating...' : 'Create Project'}
            </button>
          </div>
        </form>
      </Modal>
    </MainLayout>
  );
}
