import { ReactNode } from 'react';
import Sidebar from './Sidebar';
import Header from './Header';

interface MainLayoutProps {
  children: ReactNode;
  pageTitle?: string;
}

export default function MainLayout({ children, pageTitle = 'Dashboard' }: MainLayoutProps) {
  return (
    <div className="min-h-screen bg-slate-50">
      <Sidebar />
      <div className="ml-56">
        <Header title={pageTitle} />
        <main className="pt-14 p-6 min-h-screen bg-slate-50">
          {children}
        </main>
      </div>
    </div>
  );
}
