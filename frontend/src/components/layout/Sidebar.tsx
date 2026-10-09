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

export default function Sidebar() {
  const { activeOrg } = useAuth();

  return (
    <aside className="fixed inset-y-0 left-0 w-56 flex flex-col border-r border-slate-200 bg-white z-30">
      {/* Logo */}
      <div className="flex flex-col px-4 pt-5 pb-4 border-b border-slate-100">
        <span className="text-sky-600 font-bold text-xl tracking-tight">EDIP</span>
        <span className="text-slate-400 text-xs mt-0.5">Document Intelligence</span>
      </div>

      {/* Nav */}
      <nav className="flex-1 overflow-y-auto px-2 py-3 space-y-0.5">
        {navItems.map(({ label, icon: Icon, to }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              [
                'flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors',
                isActive
                  ? 'bg-slate-100 text-slate-900 font-medium'
                  : 'text-slate-600 hover:bg-slate-50',
              ].join(' ')
            }
          >
            <Icon size={16} strokeWidth={1.75} />
            {label}
          </NavLink>
        ))}
      </nav>

      {/* Active org */}
      <div className="px-4 py-3 border-t border-slate-100">
        <p className="text-xs text-slate-400 mb-0.5">Organization</p>
        <p className="text-sm text-slate-700 font-medium truncate">
          {activeOrg?.name ?? '—'}
        </p>
      </div>
    </aside>
  );
}
