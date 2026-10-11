import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Key,
  Plus,
  Trash2,
  Copy,
  Check,
  AlertTriangle,
  ShieldAlert,
  Calendar,
} from 'lucide-react';
import MainLayout from '../components/layout/MainLayout';
import Modal from '../components/common/Modal';
import { useAuth } from '../context/AuthContext';
import { apiKeysApi } from '../api/apiKeys';
import { APIKey, APIKeyCreateResponse } from '../types';
import { formatDate } from '../lib/utils';

export default function ApiKeysPage() {
  const queryClient = useQueryClient();
  const { activeOrg } = useAuth();

  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [createdKeyData, setCreatedKeyData] = useState<APIKeyCreateResponse | null>(null);
  const [copied, setCopied] = useState(false);

  // Form state
  const [keyName, setKeyName] = useState('');
  const [selectedScopes, setSelectedScopes] = useState<string[]>([
    'read:documents',
    'write:documents',
    'search',
    'chat',
  ]);
  const [expiresInDays, setExpiresInDays] = useState<number>(30);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const { data: apiKeys = [], isLoading } = useQuery<APIKey[]>({
    queryKey: ['api-keys', activeOrg?.id],
    queryFn: () => apiKeysApi.list(activeOrg!.id),
    enabled: !!activeOrg,
  });

  const createMutation = useMutation({
    mutationFn: (data: {
      organization_id: string;
      name: string;
      scopes: string[];
      expires_in_days?: number;
    }) => apiKeysApi.create(data),
    onSuccess: (res) => {
      queryClient.invalidateQueries({ queryKey: ['api-keys', activeOrg?.id] });
      setIsCreateOpen(false);
      setCreatedKeyData(res);
      setKeyName('');
    },
    onError: (err: any) => {
      setErrorMessage(
        err.response?.data?.error?.message || 'Failed to create API key. Admin permissions required.'
      );
    },
  });

  const revokeMutation = useMutation({
    mutationFn: (keyId: string) => apiKeysApi.revoke(keyId, activeOrg!.id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['api-keys', activeOrg?.id] });
    },
    onError: (err: any) => {
      alert(err.response?.data?.error?.message || 'Failed to revoke API key.');
    },
  });

  const handleScopeToggle = (scope: string) => {
    setSelectedScopes((prev) =>
      prev.includes(scope) ? prev.filter((s) => s !== scope) : [...prev, scope]
    );
  };

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    if (!keyName.trim()) return;
    createMutation.mutate({
      organization_id: activeOrg!.id,
      name: keyName.trim(),
      scopes: selectedScopes,
      expires_in_days: expiresInDays || undefined,
    });
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <MainLayout pageTitle="API Key Management">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8">
        <div>
          <h2 className="text-xl font-bold text-slate-900 tracking-tight">Service API Keys</h2>
          <p className="text-sm text-slate-500 mt-0.5">
            Generate and manage Argon2-hashed scoped credentials for external pipelines and SDKs.
          </p>
        </div>
        <button
          onClick={() => {
            setErrorMessage(null);
            setIsCreateOpen(true);
          }}
          className="inline-flex items-center gap-1.5 px-4 py-2 bg-red-600 text-white rounded-xl text-sm font-semibold hover:bg-red-700 transition-colors shadow-xs cursor-pointer"
        >
          <Plus size={16} /> Generate API Key
        </button>
      </div>

      {/* Keys Table */}
      <div className="bg-white rounded-2xl border border-slate-200/90 shadow-card overflow-hidden">
        {isLoading ? (
          <div className="p-12 text-center text-sm text-slate-400">Loading API keys...</div>
        ) : apiKeys.length === 0 ? (
          <div className="p-12 text-center">
            <div className="w-12 h-12 rounded-2xl bg-red-50 text-red-600 flex items-center justify-center mx-auto mb-3 shadow-2xs">
              <Key size={22} />
            </div>
            <h3 className="text-base font-semibold text-slate-800">No active API keys</h3>
            <p className="text-sm text-slate-500 mt-1 mb-6">
              Create an API key to interact with document intelligence via curl, Python, or external services.
            </p>
            <button
              onClick={() => setIsCreateOpen(true)}
              className="inline-flex items-center gap-2 px-4 py-2.5 bg-red-600 text-white rounded-xl text-sm font-semibold hover:bg-red-700 shadow-xs"
            >
              <Plus size={16} /> Generate Key
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-sm">
              <thead>
                <tr className="border-b border-slate-100 bg-slate-50/75 text-[11px] text-slate-500 uppercase tracking-wider font-semibold">
                  <th className="py-3 px-6">Name</th>
                  <th className="py-3 px-6">Key Prefix</th>
                  <th className="py-3 px-6">Scopes</th>
                  <th className="py-3 px-6">Status</th>
                  <th className="py-3 px-6">Created</th>
                  <th className="py-3 px-6 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {apiKeys.map((k) => {
                  const isRevoked = !!k.revoked_at;
                  return (
                    <tr
                      key={k.id}
                      className={`hover:bg-slate-50/70 transition-colors ${
                        isRevoked ? 'opacity-60 bg-slate-50/40' : ''
                      }`}
                    >
                      <td className="py-3.5 px-6 font-medium text-slate-800">
                        {k.name}
                      </td>
                      <td className="py-3.5 px-6 font-mono text-xs text-slate-600">
                        <span className="bg-slate-100 px-2 py-0.5 rounded-lg border border-slate-200">
                          edip_live_{k.key_prefix}_••••••••
                        </span>
                      </td>
                      <td className="py-3.5 px-6">
                        <div className="flex flex-wrap gap-1">
                          {k.scopes.map((s) => (
                            <span
                              key={s}
                              className="text-[11px] px-2 py-0.5 rounded-full bg-red-50 text-red-700 border border-red-100 font-mono font-medium"
                            >
                              {s}
                            </span>
                          ))}
                        </div>
                      </td>
                      <td className="py-3.5 px-6">
                        {isRevoked ? (
                          <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-slate-100 text-slate-500 border border-slate-200">
                            Revoked
                          </span>
                        ) : (
                          <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200/60">
                            Active
                          </span>
                        )}
                      </td>
                      <td className="py-3.5 px-6 text-slate-500 text-xs">
                        {formatDate(k.created_at)}
                      </td>
                      <td className="py-3.5 px-6 text-right">
                        {!isRevoked && (
                          <button
                            onClick={() => {
                              if (confirm(`Revoke API key "${k.name}" immediately?`)) {
                                revokeMutation.mutate(k.id);
                              }
                            }}
                            className="text-xs text-rose-600 hover:text-rose-700 font-semibold cursor-pointer"
                          >
                            Revoke
                          </button>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Create Key Modal */}
      <Modal
        isOpen={isCreateOpen}
        onClose={() => setIsCreateOpen(false)}
        title="Generate New API Key"
      >
        <form onSubmit={handleCreate} className="space-y-4">
          {errorMessage && (
            <div className="p-3 rounded-xl bg-rose-50 border border-rose-200 text-sm text-rose-700">
              {errorMessage}
            </div>
          )}

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-700 mb-1.5">
              Key Name *
            </label>
            <input
              type="text"
              required
              value={keyName}
              onChange={(e) => setKeyName(e.target.value)}
              placeholder="e.g. Production Ingestion Service"
              className="w-full px-3.5 py-2.5 bg-white border border-slate-200 rounded-xl text-sm placeholder-slate-400 text-slate-900 focus:outline-none focus:border-red-500 focus:ring-4 focus:ring-red-500/10 transition-all"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-700 mb-2">
              Assigned Permissions / Scopes
            </label>
            <div className="space-y-2.5">
              {['read:documents', 'write:documents', 'search', 'chat'].map((scope) => (
                <label key={scope} className="flex items-center gap-2.5 text-sm text-slate-700 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={selectedScopes.includes(scope)}
                    onChange={() => handleScopeToggle(scope)}
                    className="rounded-md border-slate-300 text-red-600 focus:ring-red-500 w-4 h-4"
                  />
                  <span className="font-mono text-xs">{scope}</span>
                </label>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-700 mb-1.5">
              Expiration (Days)
            </label>
            <input
              type="number"
              min={1}
              max={365}
              value={expiresInDays}
              onChange={(e) => setExpiresInDays(Number(e.target.value))}
              className="w-full px-3.5 py-2.5 bg-white border border-slate-200 rounded-xl text-sm placeholder-slate-400 text-slate-900 focus:outline-none focus:border-red-500 focus:ring-4 focus:ring-red-500/10 transition-all"
            />
          </div>

          <div className="flex justify-end gap-2.5 pt-3 border-t border-slate-100">
            <button
              type="button"
              onClick={() => setIsCreateOpen(false)}
              className="px-4 py-2 border border-slate-200 rounded-xl text-sm font-medium text-slate-700 hover:bg-slate-50 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={createMutation.isPending || !keyName.trim()}
              className="px-4 py-2 bg-red-600 text-white rounded-xl text-sm font-semibold hover:bg-red-700 disabled:opacity-50 transition-colors shadow-xs"
            >
              {createMutation.isPending ? 'Generating...' : 'Generate Key'}
            </button>
          </div>
        </form>
      </Modal>

      {/* One-Time Secret Key Display Modal */}
      {createdKeyData && (
        <Modal
          isOpen={true}
          onClose={() => setCreatedKeyData(null)}
          title="Save Your API Key"
          size="lg"
        >
          <div className="space-y-4">
            <div className="p-4 bg-amber-50 border border-amber-200 rounded-xl flex items-start gap-3 text-amber-800 text-sm">
              <ShieldAlert size={20} className="shrink-0 mt-0.5 text-amber-600" />
              <div>
                <p className="font-semibold">Copy this API key now.</p>
                <p className="text-xs mt-0.5 text-amber-700">
                  For security reasons, the raw secret is never stored on the server and will{' '}
                  <strong>never be shown again</strong> after you close this modal.
                </p>
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1.5">
                Raw Secret Key
              </label>
              <div className="flex items-center gap-2">
                <input
                  type="text"
                  readOnly
                  value={createdKeyData.secret_key}
                  className="flex-1 px-3.5 py-2.5 bg-slate-50 text-slate-900 font-mono text-xs rounded-xl border border-slate-200 select-all"
                />
                <button
                  onClick={() => copyToClipboard(createdKeyData.secret_key)}
                  className="px-4 py-2.5 bg-slate-800 hover:bg-slate-900 text-white rounded-xl text-xs font-semibold flex items-center gap-1.5 transition-colors cursor-pointer shadow-xs"
                >
                  {copied ? <Check size={14} className="text-emerald-400" /> : <Copy size={14} />}
                  <span>{copied ? 'Copied!' : 'Copy'}</span>
                </button>
              </div>
            </div>

            <div className="pt-3 border-t border-slate-100 flex justify-end">
              <button
                onClick={() => setCreatedKeyData(null)}
                className="px-4 py-2 bg-red-600 text-white rounded-xl text-sm font-semibold hover:bg-red-700 transition-colors shadow-xs"
              >
                I have safely stored this key
              </button>
            </div>
          </div>
        </Modal>
      )}
    </MainLayout>
  );
}
