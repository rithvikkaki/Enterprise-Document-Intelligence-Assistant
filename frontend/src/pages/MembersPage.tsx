import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Users, UserPlus, Trash2, Mail } from 'lucide-react';
import MainLayout from '../components/layout/MainLayout';
import Modal from '../components/common/Modal';
import { useAuth } from '../context/AuthContext';
import { organizationsApi } from '../api/organizations';
import { Member, Role } from '../types';
import { formatDate } from '../lib/utils';

function getRoleBadge(role: Role) {
  switch (role) {
    case 'OWNER':
      return 'bg-violet-50 text-violet-700 border-violet-200';
    case 'ADMIN':
      return 'bg-red-50 text-red-700 border-red-200';
    case 'EDITOR':
      return 'bg-amber-50 text-amber-700 border-amber-200';
    case 'VIEWER':
      return 'bg-slate-100 text-slate-700 border-slate-200';
  }
}

export default function MembersPage() {
  const queryClient = useQueryClient();
  const { activeOrg, user } = useAuth();

  const [isAddOpen, setIsAddOpen] = useState(false);
  const [email, setEmail] = useState('');
  const [role, setRole] = useState<Role>('VIEWER');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const { data: members = [], isLoading } = useQuery<Member[]>({
    queryKey: ['members', activeOrg?.id],
    queryFn: () => organizationsApi.listMembers(activeOrg!.id),
    enabled: !!activeOrg,
  });

  const addMutation = useMutation({
    mutationFn: (data: { email: string; role: Role }) =>
      organizationsApi.addMember(activeOrg!.id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['members', activeOrg?.id] });
      queryClient.invalidateQueries({ queryKey: ['org-stats', activeOrg?.id] });
      setIsAddOpen(false);
      setEmail('');
      setRole('VIEWER');
    },
    onError: (err: any) => {
      setErrorMessage(err.response?.data?.error?.message || 'Failed to add member.');
    },
  });

  const updateRoleMutation = useMutation({
    mutationFn: ({ memberId, newRole }: { memberId: string; newRole: Role }) =>
      organizationsApi.updateMemberRole(activeOrg!.id, memberId, newRole),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['members', activeOrg?.id] });
    },
    onError: (err: any) => {
      alert(err.response?.data?.error?.message || 'Failed to update member role.');
    },
  });

  const removeMutation = useMutation({
    mutationFn: (memberId: string) => organizationsApi.removeMember(activeOrg!.id, memberId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['members', activeOrg?.id] });
      queryClient.invalidateQueries({ queryKey: ['org-stats', activeOrg?.id] });
    },
    onError: (err: any) => {
      alert(err.response?.data?.error?.message || 'Failed to remove member.');
    },
  });

  const handleAdd = (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.trim()) return;
    addMutation.mutate({ email: email.trim(), role });
  };

  return (
    <MainLayout pageTitle="Team & Access Control">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8">
        <div>
          <h2 className="text-xl font-bold text-slate-900 tracking-tight">Organization Members</h2>
          <p className="text-sm text-slate-500 mt-0.5">
            Role-Based Access Control (RBAC): OWNER, ADMIN, EDITOR, and VIEWER permissions.
          </p>
        </div>
        <button
          onClick={() => {
            setErrorMessage(null);
            setIsAddOpen(true);
          }}
          className="inline-flex items-center gap-1.5 px-4 py-2 bg-red-600 text-white rounded-xl text-sm font-semibold hover:bg-red-700 transition-colors shadow-xs cursor-pointer"
        >
          <UserPlus size={16} /> Add Member
        </button>
      </div>

      <div className="bg-white rounded-2xl border border-slate-200/90 shadow-card overflow-hidden">
        {isLoading ? (
          <div className="p-12 text-center text-sm text-slate-400">Loading members...</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-sm">
              <thead>
                <tr className="border-b border-slate-100 bg-slate-50/75 text-[11px] text-slate-500 uppercase tracking-wider font-semibold">
                  <th className="py-3 px-6">Name</th>
                  <th className="py-3 px-6">Email</th>
                  <th className="py-3 px-6">Role</th>
                  <th className="py-3 px-6">Joined</th>
                  <th className="py-3 px-6 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {members.map((m) => {
                  const isSelf = m.user_id === user?.id;
                  const isOwner = m.role === 'OWNER';
                  return (
                    <tr key={m.id} className="hover:bg-slate-50/70 transition-colors">
                      <td className="py-3.5 px-6 font-medium text-slate-800">
                        {m.user_full_name || 'Member'}
                        {isSelf && (
                          <span className="ml-2 text-[10px] bg-red-50 text-red-700 border border-red-100 px-1.5 py-0.5 rounded-full font-bold">
                            YOU
                          </span>
                        )}
                      </td>
                      <td className="py-3.5 px-6 text-slate-500 text-xs">
                        {m.user_email}
                      </td>
                      <td className="py-3.5 px-6">
                        <select
                          disabled={isOwner}
                          value={m.role}
                          onChange={(e) =>
                            updateRoleMutation.mutate({
                              memberId: m.id,
                              newRole: e.target.value as Role,
                            })
                          }
                          className={`text-xs font-semibold px-2.5 py-1 rounded-full border focus:ring-2 focus:ring-red-500 focus:outline-none ${getRoleBadge(
                            m.role
                          )} ${isOwner ? 'cursor-not-allowed opacity-90' : 'cursor-pointer'}`}
                        >
                          <option value="VIEWER">VIEWER</option>
                          <option value="EDITOR">EDITOR</option>
                          <option value="ADMIN">ADMIN</option>
                          <option value="OWNER" disabled>
                            OWNER
                          </option>
                        </select>
                      </td>
                      <td className="py-3.5 px-6 text-slate-500 text-xs">
                        {formatDate(m.created_at)}
                      </td>
                      <td className="py-3.5 px-6 text-right">
                        {!isOwner && !isSelf && (
                          <button
                            onClick={() => {
                              if (confirm(`Remove member ${m.user_email} from this organization?`)) {
                                removeMutation.mutate(m.id);
                              }
                            }}
                            className="text-slate-400 hover:text-rose-600 p-1 rounded-lg transition-colors"
                            title="Remove Member"
                          >
                            <Trash2 size={15} />
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

      {/* Add Member Modal */}
      <Modal
        isOpen={isAddOpen}
        onClose={() => setIsAddOpen(false)}
        title="Add Organization Member"
      >
        <form onSubmit={handleAdd} className="space-y-4">
          {errorMessage && (
            <div className="p-3 rounded-xl bg-rose-50 border border-rose-200 text-sm text-rose-700">
              {errorMessage}
            </div>
          )}

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-700 mb-1.5">
              Registered User Email *
            </label>
            <div className="relative">
              <Mail size={16} className="absolute left-3.5 top-3 text-slate-400" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="colleague@enterprise.com"
                className="w-full pl-10 pr-3.5 py-2.5 bg-white border border-slate-200 rounded-xl text-sm placeholder-slate-400 text-slate-900 focus:outline-none focus:border-red-500 focus:ring-4 focus:ring-red-500/10 transition-all"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-700 mb-1.5">
              Initial Role *
            </label>
            <select
              value={role}
              onChange={(e) => setRole(e.target.value as Role)}
              className="w-full px-3.5 py-2.5 border border-slate-200 rounded-xl text-sm bg-white focus:outline-none focus:border-red-500 focus:ring-4 focus:ring-red-500/10 text-slate-800"
            >
              <option value="VIEWER">VIEWER (Search & Ask Questions)</option>
              <option value="EDITOR">EDITOR (Upload Documents & Create Projects)</option>
              <option value="ADMIN">ADMIN (Manage Members & API Keys)</option>
            </select>
          </div>

          <div className="flex justify-end gap-2.5 pt-3 border-t border-slate-100">
            <button
              type="button"
              onClick={() => setIsAddOpen(false)}
              className="px-4 py-2 border border-slate-200 rounded-xl text-sm font-medium text-slate-700 hover:bg-slate-50 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={addMutation.isPending || !email.trim()}
              className="px-4 py-2 bg-red-600 text-white rounded-xl text-sm font-semibold hover:bg-red-700 disabled:opacity-50 transition-colors shadow-xs"
            >
              {addMutation.isPending ? 'Adding...' : 'Add Member'}
            </button>
          </div>
        </form>
      </Modal>
    </MainLayout>
  );
}
