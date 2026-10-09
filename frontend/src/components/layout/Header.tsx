import { useState, useRef, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { ChevronDown, LogOut, Building2 } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { api } from '../../lib/axios';
import { Organization } from '../../types';

interface HeaderProps {
  title?: string;
}

function getInitials(fullName?: string | null): string {
  if (!fullName) return '?';
  return fullName
    .trim()
    .split(/\s+/)
    .slice(0, 2)
    .map((w) => w[0]?.toUpperCase() ?? '')
    .join('');
}

export default function Header({ title = 'Dashboard' }: HeaderProps) {
  const { user, activeOrg, setActiveOrg, logout } = useAuth();

  const [orgOpen, setOrgOpen] = useState(false);
  const [userOpen, setUserOpen] = useState(false);

  const orgRef = useRef<HTMLDivElement>(null);
  const userRef = useRef<HTMLDivElement>(null);

  const { data: orgs = [] } = useQuery<Organization[]>({
    queryKey: ['organizations'],
    queryFn: async () => {
      const res = await api.get('/organizations');
      return res.data;
    },
  });

  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (orgRef.current && !orgRef.current.contains(e.target as Node)) {
        setOrgOpen(false);
      }
      if (userRef.current && !userRef.current.contains(e.target as Node)) {
        setUserOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, []);

  return (
    <header className="fixed top-0 right-0 left-56 h-14 z-20 flex items-center justify-between px-6 bg-white border-b border-slate-200">
      <h1 className="text-base font-semibold text-slate-800">{title}</h1>

      <div className="flex items-center gap-3">
        {/* Org selector */}
        <div className="relative" ref={orgRef}>
          <button
            onClick={() => setOrgOpen((v) => !v)}
            className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-slate-200 text-sm text-slate-700 hover:bg-slate-50 transition-colors"
          >
            <Building2 size={14} className="text-slate-400" />
            <span className="max-w-[140px] truncate">{activeOrg?.name ?? 'Select org'}</span>
            <ChevronDown size={14} className="text-slate-400" />
          </button>

          {orgOpen && (
            <div className="absolute right-0 mt-1 w-52 bg-white rounded-xl shadow-lg border border-slate-100 py-1 z-50">
              {orgs.length === 0 && (
                <p className="px-3 py-2 text-xs text-slate-400">No organizations</p>
              )}
              {orgs.map((org) => (
                <button
                  key={org.id}
                  onClick={() => {
                    setActiveOrg(org);
                    setOrgOpen(false);
                  }}
                  className={[
                    'w-full text-left px-3 py-2 text-sm transition-colors',
                    activeOrg?.id === org.id
                      ? 'bg-sky-50 text-sky-700 font-medium'
                      : 'text-slate-700 hover:bg-slate-50',
                  ].join(' ')}
                >
                  {org.name}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* User avatar + dropdown */}
        <div className="relative" ref={userRef}>
          <button
            onClick={() => setUserOpen((v) => !v)}
            className="flex items-center gap-2 focus:outline-none"
          >
            <span className="w-8 h-8 rounded-full bg-sky-600 text-white flex items-center justify-center text-xs font-semibold select-none">
              {getInitials(user?.full_name)}
            </span>
            <ChevronDown size={14} className="text-slate-400" />
          </button>

          {userOpen && (
            <div className="absolute right-0 mt-1 w-44 bg-white rounded-xl shadow-lg border border-slate-100 py-1 z-50">
              <div className="px-3 py-2 border-b border-slate-100">
                <p className="text-xs font-medium text-slate-800 truncate">{user?.full_name}</p>
                <p className="text-xs text-slate-400 truncate">{user?.email}</p>
              </div>
              <button
                onClick={() => {
                  setUserOpen(false);
                  logout();
                }}
                className="w-full flex items-center gap-2 px-3 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors"
              >
                <LogOut size={14} />
                Sign Out
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
