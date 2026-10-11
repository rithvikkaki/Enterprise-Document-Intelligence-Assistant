import { useState, useRef, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { ChevronDown, LogOut, Building2, Check, Menu } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { api } from '../../lib/axios';
import { Organization } from '../../types';

interface HeaderProps {
  title?: string;
  onMenuClick?: () => void;
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

export default function Header({ title = 'Dashboard', onMenuClick }: HeaderProps) {
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
    <header className="fixed top-0 right-0 left-0 lg:left-64 h-16 z-20 flex items-center justify-between px-4 sm:px-6 lg:px-8 bg-white/95 backdrop-blur-md border-b border-slate-200/80 transition-all">
      <div className="flex items-center gap-3">
        {/* Mobile Hamburger Button */}
        {onMenuClick && (
          <button
            onClick={onMenuClick}
            className="lg:hidden p-2 rounded-xl text-slate-600 hover:text-slate-900 hover:bg-slate-100 transition-colors"
            aria-label="Open navigation menu"
          >
            <Menu size={20} />
          </button>
        )}
        <h1 className="text-sm sm:text-base font-semibold text-slate-900 truncate max-w-[180px] sm:max-w-xs md:max-w-md">
          {title}
        </h1>
      </div>

      <div className="flex items-center gap-3">
        {/* Org selector dropdown */}
        <div className="relative" ref={orgRef}>
          <button
            onClick={() => setOrgOpen((v) => !v)}
            className="flex items-center gap-2 px-3 py-1.5 rounded-xl border border-slate-200 text-sm font-medium text-slate-700 bg-white hover:bg-slate-50 transition-colors shadow-xs"
          >
            <Building2 size={15} className="text-red-600 shrink-0" />
            <span className="max-w-[150px] truncate">{activeOrg?.name ?? 'Select Org'}</span>
            <ChevronDown size={14} className="text-slate-400 shrink-0" />
          </button>

          {orgOpen && (
            <div className="absolute right-0 mt-2 w-56 bg-white rounded-xl shadow-dropdown border border-slate-200/90 py-1.5 z-50 animate-in fade-in zoom-in-95 duration-100">
              <div className="px-3 py-1.5 text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                Organizations
              </div>
              {orgs.length === 0 && (
                <p className="px-3 py-2 text-xs text-slate-400">No organizations found</p>
              )}
              {orgs.map((org) => {
                const isSelected = activeOrg?.id === org.id;
                return (
                  <button
                    key={org.id}
                    onClick={() => {
                      setActiveOrg(org);
                      setOrgOpen(false);
                    }}
                    className={[
                      'w-full flex items-center justify-between px-3.5 py-2 text-sm transition-colors text-left',
                      isSelected
                        ? 'bg-red-50 text-red-700 font-semibold'
                        : 'text-slate-700 hover:bg-slate-50',
                    ].join(' ')}
                  >
                    <span className="truncate">{org.name}</span>
                    {isSelected && <Check size={14} className="text-red-600 shrink-0" />}
                  </button>
                );
              })}
            </div>
          )}
        </div>

        {/* User avatar + profile dropdown */}
        <div className="relative" ref={userRef}>
          <button
            onClick={() => setUserOpen((v) => !v)}
            className="flex items-center gap-2 p-1 rounded-full hover:ring-2 hover:ring-red-100 transition-all focus:outline-none"
          >
            <span className="w-8 h-8 rounded-full bg-red-600 text-white flex items-center justify-center text-xs font-semibold shadow-xs select-none">
              {getInitials(user?.full_name)}
            </span>
            <ChevronDown size={14} className="text-slate-400" />
          </button>

          {userOpen && (
            <div className="absolute right-0 mt-2 w-52 bg-white rounded-xl shadow-dropdown border border-slate-200/90 py-1.5 z-50">
              <div className="px-3.5 py-2.5 border-b border-slate-100">
                <p className="text-xs font-semibold text-slate-900 truncate">{user?.full_name}</p>
                <p className="text-xs text-slate-400 truncate">{user?.email}</p>
              </div>
              <div className="p-1">
                <button
                  onClick={() => {
                    setUserOpen(false);
                    logout();
                  }}
                  className="w-full flex items-center gap-2 px-3 py-2 text-sm text-rose-600 hover:bg-rose-50 rounded-lg transition-colors"
                >
                  <LogOut size={14} />
                  Sign Out
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
