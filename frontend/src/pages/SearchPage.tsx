import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useQuery, useMutation } from '@tanstack/react-query';
import {
  Search as SearchIcon,
  Sparkles,
  FileText,
  Filter,
  ArrowRight,
  SlidersHorizontal,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';
import MainLayout from '../components/layout/MainLayout';
import { useAuth } from '../context/AuthContext';
import { searchApi } from '../api/search';
import { projectsApi } from '../api/projects';
import { Project, SearchResultChunk } from '../types';

export default function SearchPage() {
  const { activeOrg, activeProject, setActiveProject } = useAuth();

  const [query, setQuery] = useState('');
  const [selectedProjectId, setSelectedProjectId] = useState<string>(activeProject?.id || '');
  const [limit, setLimit] = useState<number>(10);
  const [expandedChunkId, setExpandedChunkId] = useState<string | null>(null);

  const { data: projects = [] } = useQuery<Project[]>({
    queryKey: ['projects', activeOrg?.id],
    queryFn: () => projectsApi.list(activeOrg!.id),
    enabled: !!activeOrg,
  });

  const searchMutation = useMutation({
    mutationFn: async () => {
      if (!query.trim() || !selectedProjectId) {
        throw new Error('Please specify a query and select a project.');
      }
      return searchApi.search(activeOrg!.id, selectedProjectId, query.trim(), limit);
    },
  });

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim() || !selectedProjectId) return;
    searchMutation.mutate();
  };

  const results: SearchResultChunk[] = searchMutation.data?.results || [];

  return (
    <MainLayout pageTitle="Hybrid Semantic Search">
      <div className="max-w-4xl mx-auto space-y-6">
        <div>
          <h2 className="text-xl font-bold text-slate-900">Hybrid Search Engine</h2>
          <p className="text-sm text-slate-500">
            Combines dense vector similarity (all-MiniLM-L6-v2) and full-text search (PostgreSQL FTS) using Reciprocal Rank Fusion ($k=60$).
          </p>
        </div>

        {/* Search Bar and Project Filter Form */}
        <form onSubmit={handleSearch} className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm space-y-3">
          <div className="flex gap-2">
            <div className="relative flex-1">
              <SearchIcon size={18} className="absolute left-3.5 top-3 text-slate-400" />
              <input
                type="text"
                required
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Ask or search e.g. 'What is the quarterly revenue retention rate?'"
                className="w-full pl-10 pr-4 py-2.5 border border-slate-200 rounded-xl text-sm placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-transparent transition-colors"
              />
            </div>
            <button
              type="submit"
              disabled={searchMutation.isPending || !query.trim() || !selectedProjectId}
              className="px-5 py-2.5 bg-sky-600 text-white rounded-xl text-sm font-medium hover:bg-sky-700 disabled:opacity-50 transition-colors flex items-center gap-1.5 shadow-sm cursor-pointer"
            >
              {searchMutation.isPending ? (
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : (
                <Sparkles size={16} />
              )}
              <span>Search</span>
            </button>
          </div>

          <div className="flex flex-wrap items-center justify-between gap-3 pt-2 border-t border-slate-100 text-xs text-slate-600">
            <div className="flex items-center gap-2">
              <Filter size={14} className="text-slate-400" />
              <span className="font-medium text-slate-500">Project Context:</span>
              <select
                value={selectedProjectId}
                onChange={(e) => {
                  setSelectedProjectId(e.target.value);
                  const p = projects.find((x) => x.id === e.target.value);
                  if (p) setActiveProject(p);
                }}
                className="py-1 px-2 border border-slate-200 rounded-lg bg-white text-xs text-slate-700 focus:ring-2 focus:ring-sky-500 focus:outline-none font-medium"
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

            <div className="flex items-center gap-2">
              <SlidersHorizontal size={14} className="text-slate-400" />
              <span>Top K:</span>
              <select
                value={limit}
                onChange={(e) => setLimit(Number(e.target.value))}
                className="py-1 px-2 border border-slate-200 rounded-lg bg-white text-xs text-slate-700 focus:ring-2 focus:ring-sky-500 focus:outline-none"
              >
                <option value={5}>5 Results</option>
                <option value={10}>10 Results</option>
                <option value={20}>20 Results</option>
              </select>
            </div>
          </div>
        </form>

        {/* Search Results Area */}
        {searchMutation.isPending ? (
          <div className="py-16 text-center space-y-3">
            <div className="w-8 h-8 border-2 border-sky-600 border-t-transparent rounded-full animate-spin mx-auto" />
            <p className="text-sm font-medium text-slate-600">
              Executing dense vector retrieval + full-text search fusion...
            </p>
          </div>
        ) : searchMutation.isError ? (
          <div className="p-4 rounded-xl bg-red-50 border border-red-200 text-sm text-red-700 text-center">
            {(searchMutation.error as any)?.response?.data?.error?.message ||
              (searchMutation.error as Error).message ||
              'Search query failed.'}
          </div>
        ) : !searchMutation.isSuccess ? (
          <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center">
            <SearchIcon className="mx-auto h-12 w-12 text-slate-300 mb-3" />
            <h3 className="text-base font-semibold text-slate-800">Ready to search</h3>
            <p className="text-sm text-slate-500 max-w-sm mx-auto mt-1">
              Select a project and enter a natural language question or keyword query to retrieve relevant chunks.
            </p>
          </div>
        ) : results.length === 0 ? (
          <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center">
            <FileText className="mx-auto h-12 w-12 text-slate-300 mb-3" />
            <h3 className="text-base font-semibold text-slate-800">No matching chunks found</h3>
            <p className="text-sm text-slate-500 max-w-sm mx-auto mt-1">
              Try adjusting your query or uploading more documents to this project collection.
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="flex items-center justify-between text-xs text-slate-500 px-1">
              <span>
                Found <strong className="text-slate-800">{results.length}</strong> matching chunks for{' '}
                <em className="text-slate-700">"{searchMutation.data?.query}"</em>
              </span>
              <span className="bg-sky-50 text-sky-700 px-2 py-0.5 rounded font-medium">
                Reciprocal Rank Fusion (RRF k=60)
              </span>
            </div>

            {results.map((r, idx) => {
              const isExpanded = expandedChunkId === r.chunk_id;
              return (
                <div
                  key={r.chunk_id}
                  className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm hover:border-slate-300 transition-colors"
                >
                  <div className="flex items-start justify-between gap-4 mb-2">
                    <div className="flex items-center gap-2">
                      <span className="w-5 h-5 rounded-full bg-slate-100 text-slate-600 text-xs font-bold flex items-center justify-center">
                        {idx + 1}
                      </span>
                      <h4 className="text-sm font-semibold text-slate-900">
                        {r.document_name}
                      </h4>
                      <span className="text-xs font-medium px-2 py-0.5 rounded bg-slate-100 text-slate-600">
                        v{r.version_number} • chunk #{r.chunk_index}
                      </span>
                    </div>

                    <div className="flex items-center gap-2">
                      <span className="text-xs font-mono font-semibold px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 border border-emerald-100">
                        Score: {r.score.toFixed(4)}
                      </span>
                      <Link
                        to={`/documents/${r.document_id}`}
                        className="text-xs font-medium text-sky-600 hover:text-sky-700 flex items-center gap-0.5"
                      >
                        Doc <ArrowRight size={12} />
                      </Link>
                    </div>
                  </div>

                  {/* Chunk text content */}
                  <p className="text-sm text-slate-700 leading-relaxed font-sans bg-slate-50/70 p-3 rounded-lg border border-slate-100">
                    {r.content}
                  </p>

                  {/* Expandable Technical Details (RRF details) */}
                  {r.metadata && Object.keys(r.metadata).length > 0 && (
                    <div className="mt-2 pt-2 border-t border-slate-100">
                      <button
                        onClick={() => setExpandedChunkId(isExpanded ? null : r.chunk_id)}
                        className="text-xs text-slate-400 hover:text-slate-600 flex items-center gap-1 cursor-pointer"
                      >
                        {isExpanded ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
                        <span>{isExpanded ? 'Hide metadata' : 'Inspect chunk metadata'}</span>
                      </button>

                      {isExpanded && (
                        <pre className="mt-2 p-2 bg-slate-900 text-slate-200 text-xs font-mono rounded overflow-x-auto">
                          {JSON.stringify(r.metadata, null, 2)}
                        </pre>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </MainLayout>
  );
}
