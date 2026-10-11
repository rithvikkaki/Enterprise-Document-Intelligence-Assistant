import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  FileText,
  Search,
  MessageSquare,
  FolderOpen,
  Users,
  Key,
  Shield,
  Layers,
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

const navItems = [
  { label: 'Dashboard',    icon: LayoutDashboard, to: '/dashboard' },
  { label: 'Documents',    icon: FileText,         to: '/documents' },
  { label: 'Search',       icon: Search,           to: '/search' },
  { label: 'AI Assistant', icon: MessageSquare,    to: '/assistant' },
  { label: 'Projects',     icon: FolderOpen,       to: '/projects' },
  { label: 'Members',      icon: Users,            to: '/members' },
  { label: 'API Keys',     icon: Key,              to: '/api-keys' },
  { label: 'Audit Logs',   icon: Shield,           to: '/audit-logs' },
];

interface SidebarProps {
  isOpen?: boolean;
  onClose?: () => void;
}

export default function Sidebar({ isOpen = false, onClose }: SidebarProps) {
  const { activeOrg } = useAuth();

  return (
    <>
      {/* Mobile backdrop overlay */}
      {isOpen && (
        <div
          onClick={onClose}
          className="fixed inset-0 bg-slate-900/50 backdrop-blur-xs z-40 lg:hidden transition-opacity animate-in fade-in duration-200"
          aria-hidden="true"
        />
      )}

      <aside
        className={`fixed inset-y-0 left-0 w-64 flex flex-col border-r border-slate-200/90 bg-white z-40 lg:z-30 shadow-subtle transition-transform duration-200 ease-in-out lg:translate-x-0 ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {/* Brand Header */}
        <div className="flex items-center justify-between px-5 pt-5 pb-4 border-b border-slate-100">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-red-600 flex items-center justify-center text-white shadow-xs">
              <Layers size={18} strokeWidth={2.2} />
            </div>
            <div>
              <span className="text-slate-900 font-bold text-base tracking-tight block">DocIntel</span>
              <span className="text-slate-400 text-xs font-normal block -mt-0.5">Enterprise AI</span>
            </div>
          </div>
          {/* Mobile close toggle */}
          {onClose && (
            <button
              onClick={onClose}
              className="lg:hidden p-1.5 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors"
              aria-label="Close navigation"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          )}
        </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-1">
        <div className="px-3 pb-2 text-[11px] font-semibold uppercase tracking-wider text-slate-400">
          Navigation
        </div>
        {navItems.map(({ label, icon: Icon, to }) => (
          <NavLink
            key={to}
            to={to}
            onClick={() => onClose?.()}
            className={({ isActive }) =>
              [
                'flex items-center gap-3 px-3 py-2 rounded-xl text-sm font-medium transition-all duration-150',
                isActive
                  ? 'bg-red-50 text-red-700 shadow-xs'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50',
              ].join(' ')
            }
          >
            {({ isActive }) => (
              <>
                <Icon
                  size={17}
                  strokeWidth={isActive ? 2 : 1.75}
                  className={isActive ? 'text-red-600' : 'text-slate-400'}
                />
                <span>{label}</span>
              </>
            )}
          </NavLink>
        ))}
      </nav>

      {/* Active Organization Footer */}
      <div className="p-3.5 mx-3 mb-4 rounded-xl bg-slate-50 border border-slate-200/80">
        <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
          <span className="font-medium text-[11px] uppercase tracking-wider">Workspace</span>
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
        </div>
        <p className="text-sm font-semibold text-slate-800 truncate">
          {activeOrg?.name ?? 'No Organization'}
        </p>
      </div>
    </aside>
  </>
  );
}
