import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Shield, Filter, Search, ChevronDown, ChevronUp, Lock } from 'lucide-react';
import MainLayout from '../components/layout/MainLayout';
import { useAuth } from '../context/AuthContext';
import { auditLogsApi } from '../api/auditLogs';
import { AuditLog } from '../types';
import { formatDate } from '../lib/utils';

export default function AuditLogsPage() {
  const { activeOrg } = useAuth();
  const [filterAction, setFilterAction] = useState('');
  const [expandedLogId, setExpandedLogId] = useState<string | null>(null);

  const { data: logs = [], isLoading } = useQuery<AuditLog[]>({
    queryKey: ['audit-logs', activeOrg?.id],
    queryFn: () => auditLogsApi.list(activeOrg!.id, 100),
    enabled: !!activeOrg,
    refetchInterval: 15000,
  });

  const filteredLogs = logs.filter(
    (l) => !filterAction || l.action.toLowerCase().includes(filterAction.toLowerCase())
  );

  return (
    <MainLayout pageTitle="Audit Logs">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8">
        <div>
          <h2 className="text-xl font-bold text-slate-900 tracking-tight">Immutable Audit Trail</h2>
          <p className="text-sm text-slate-500 mt-0.5">
            Security and operational audit events with automatic sensitive credential redaction.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <div className="relative">
            <Search size={15} className="absolute left-3.5 top-2.5 text-slate-400" />
            <input
              type="text"
              value={filterAction}
              onChange={(e) => setFilterAction(e.target.value)}
              placeholder="Filter actions..."
              className="pl-9 pr-3.5 py-2 border border-slate-200 rounded-xl text-xs bg-white text-slate-700 focus:outline-none focus:border-red-500 focus:ring-4 focus:ring-red-500/10 shadow-2xs"
            />
          </div>
        </div>
      </div>

      <div className="bg-white rounded-2xl border border-slate-200/90 shadow-card overflow-hidden">
        {isLoading ? (
          <div className="p-12 text-center text-sm text-slate-400">Loading audit trail...</div>
        ) : filteredLogs.length === 0 ? (
          <div className="p-12 text-center">
            <div className="w-12 h-12 rounded-2xl bg-red-50 text-red-600 flex items-center justify-center mx-auto mb-3 shadow-2xs">
              <Shield size={22} />
            </div>
            <h3 className="text-base font-semibold text-slate-800">No audit events recorded</h3>
            <p className="text-sm text-slate-500 mt-1">
              Events will automatically appear here as documents are uploaded and searches are performed.
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-sm">
              <thead>
                <tr className="border-b border-slate-100 bg-slate-50/75 text-[11px] text-slate-500 uppercase tracking-wider font-semibold">
                  <th className="py-3 px-6">Timestamp</th>
                  <th className="py-3 px-6">Action</th>
                  <th className="py-3 px-6">Resource</th>
                  <th className="py-3 px-6">Resource ID</th>
                  <th className="py-3 px-6">Request ID</th>
                  <th className="py-3 px-6 text-right">Details</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-mono text-xs">
                {filteredLogs.map((log) => {
                  const isExpanded = expandedLogId === log.id;
                  return (
                    <React.Fragment key={log.id}>
                      <tr className="hover:bg-slate-50/70 transition-colors">
                        <td className="py-3.5 px-6 font-sans text-slate-500">
                          {formatDate(log.created_at)}
                        </td>
                        <td className="py-3.5 px-6">
                          <span className="px-2.5 py-0.5 rounded-full bg-red-50 text-red-700 font-semibold text-[11px] border border-red-100">
                            {log.action}
                          </span>
                        </td>
                        <td className="py-3.5 px-6 font-sans text-slate-700 font-medium">
                          {log.resource_type}
                        </td>
                        <td className="py-3.5 px-6 text-slate-500 truncate max-w-[120px]">
                          {log.resource_id ? `${log.resource_id.substring(0, 10)}...` : '—'}
                        </td>
                        <td className="py-3.5 px-6 text-slate-400 truncate max-w-[100px]">
                          {log.request_id ? `${log.request_id.substring(0, 8)}...` : '—'}
                        </td>
                        <td className="py-3.5 px-6 text-right font-sans">
                          <button
                            onClick={() => setExpandedLogId(isExpanded ? null : log.id)}
                            className="text-xs text-red-600 hover:text-red-800 font-semibold inline-flex items-center gap-1 cursor-pointer"
                          >
                            <span>{isExpanded ? 'Hide' : 'Inspect'}</span>
                            {isExpanded ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
                          </button>
                        </td>
                      </tr>

                      {isExpanded && (
                        <tr className="bg-slate-50/60">
                          <td colSpan={6} className="p-4 px-6">
                            <div className="bg-slate-50 border border-slate-200 rounded-xl p-3.5 text-slate-800 text-xs font-mono overflow-x-auto space-y-1.5 shadow-2xs">
                              <div className="flex items-center gap-1.5 text-slate-500 text-[11px] pb-1.5 border-b border-slate-200">
                                <Lock size={12} className="text-emerald-600" />
                                <span className="font-sans font-medium">Redacted Metadata Payload (Secrets & Passwords Excluded)</span>
                              </div>
                              <pre className="text-slate-700">{JSON.stringify(log.metadata_json || {}, null, 2)}</pre>
                            </div>
                          </td>
                        </tr>
                      )}
                    </React.Fragment>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </MainLayout>
  );
}
