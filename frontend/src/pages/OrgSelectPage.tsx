import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Building2, Plus, ArrowRight, ShieldCheck, AlertCircle } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { organizationsApi } from '../api/organizations';
import { Organization } from '../types';
import Modal from '../components/common/Modal';

export default function OrgSelectPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { setActiveOrg, user, logout } = useAuth();

  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [newOrgName, setNewOrgName] = useState('');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const { data: orgs = [], isLoading } = useQuery<Organization[]>({
    queryKey: ['organizations'],
    queryFn: organizationsApi.list,
  });

  const createMutation = useMutation({
    mutationFn: organizationsApi.create,
    onSuccess: (newOrg) => {
      queryClient.invalidateQueries({ queryKey: ['organizations'] });
      setIsCreateOpen(false);
      setNewOrgName('');
      setActiveOrg(newOrg);
      navigate('/dashboard');
    },
    onError: (err: any) => {
      setErrorMessage(err.response?.data?.error?.message || 'Failed to create organization.');
    },
  });

  const handleSelectOrg = (org: Organization) => {
    setActiveOrg(org);
    navigate('/dashboard');
  };

  const handleCreateSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newOrgName.trim()) return;
    createMutation.mutate({ name: newOrgName.trim() });
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-lg">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-sky-600 text-white font-bold text-xl shadow-md mb-3">
            ED
          </div>
          <h2 className="text-2xl font-bold text-slate-900">Select Organization</h2>
          <p className="mt-1 text-sm text-slate-500">
            Welcome, {user?.full_name || 'User'}. Choose an organization context to continue.
          </p>
        </div>

        <div className="bg-white shadow-sm border border-slate-200 rounded-2xl p-6 sm:p-8">
          {isLoading ? (
            <div className="flex flex-col items-center justify-center py-10">
              <div className="w-8 h-8 border-2 border-sky-600 border-t-transparent rounded-full animate-spin mb-2" />
              <p className="text-sm text-slate-500">Loading your organizations...</p>
            </div>
          ) : orgs.length === 0 ? (
            <div className="text-center py-8">
              <Building2 className="mx-auto h-12 w-12 text-slate-400 mb-3" />
              <h3 className="text-base font-semibold text-slate-800">No organizations found</h3>
              <p className="text-sm text-slate-500 max-w-sm mx-auto mt-1 mb-6">
                You are not currently a member of any organization. Create your first organization to get started.
              </p>
              <button
                onClick={() => setIsCreateOpen(true)}
                className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-sky-600 text-white text-sm font-medium hover:bg-sky-700 transition-colors shadow-sm"
              >
                <Plus size={16} />
                Create Organization
              </button>
            </div>
          ) : (
            <div className="space-y-3">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                  Your Organizations ({orgs.length})
                </span>
                <button
                  onClick={() => setIsCreateOpen(true)}
                  className="text-xs font-medium text-sky-600 hover:text-sky-700 flex items-center gap-1"
                >
                  <Plus size={14} /> New Org
                </button>
              </div>

              {orgs.map((org) => (
                <div
                  key={org.id}
                  onClick={() => handleSelectOrg(org)}
                  className="group flex items-center justify-between p-4 rounded-xl border border-slate-200 hover:border-sky-500 hover:bg-sky-50/50 cursor-pointer transition-all duration-150"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-slate-100 group-hover:bg-sky-100 flex items-center justify-center text-slate-600 group-hover:text-sky-600 transition-colors">
                      <Building2 size={20} />
                    </div>
                    <div>
                      <h4 className="text-sm font-semibold text-slate-900 group-hover:text-sky-700">
                        {org.name}
                      </h4>
                      <p className="text-xs text-slate-400">slug: {org.slug}</p>
                    </div>
                  </div>
                  <ArrowRight
                    size={16}
                    className="text-slate-400 group-hover:text-sky-600 group-hover:translate-x-0.5 transition-all"
                  />
                </div>
              ))}
            </div>
          )}

          <div className="mt-8 pt-4 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
            <span className="inline-flex items-center gap-1">
              <ShieldCheck size={14} className="text-emerald-500" />
              Strict tenant isolation enforced
            </span>
            <button
              onClick={logout}
              className="text-slate-500 hover:text-red-600 transition-colors"
            >
              Sign out
            </button>
          </div>
        </div>
      </div>

      <Modal
        isOpen={isCreateOpen}
        onClose={() => {
          setIsCreateOpen(false);
          setErrorMessage(null);
        }}
        title="Create Organization"
        size="md"
      >
        <form onSubmit={handleCreateSubmit} className="space-y-4">
          {errorMessage && (
            <div className="p-3 rounded-lg bg-red-50 border border-red-200 flex items-center gap-2 text-sm text-red-700">
              <AlertCircle size={16} className="shrink-0" />
              <span>{errorMessage}</span>
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Organization Name
            </label>
            <input
              type="text"
              required
              value={newOrgName}
              onChange={(e) => setNewOrgName(e.target.value)}
              placeholder="e.g. Acme Corporation"
              className="block w-full px-3 py-2 border border-slate-300 rounded-lg text-sm placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-transparent"
            />
            <p className="text-xs text-slate-400 mt-1">
              You will become the Owner of this new organization.
            </p>
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
              disabled={createMutation.isPending || !newOrgName.trim()}
              className="px-4 py-2 bg-sky-600 text-white rounded-lg text-sm font-medium hover:bg-sky-700 disabled:opacity-50"
            >
              {createMutation.isPending ? 'Creating...' : 'Create'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
