import { ReactNode, useState } from 'react';
import Sidebar from './Sidebar';
import Header from './Header';

interface MainLayoutProps {
  children: ReactNode;
  pageTitle?: string;
}

export default function MainLayout({ children, pageTitle = 'Dashboard' }: MainLayoutProps) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <div className="min-h-screen bg-[#fafafa] text-slate-900 font-sans antialiased selection:bg-red-100 selection:text-red-900">
      <Sidebar isOpen={mobileMenuOpen} onClose={() => setMobileMenuOpen(false)} />
      <div className="lg:ml-64 flex flex-col min-h-screen">
        <Header title={pageTitle} onMenuClick={() => setMobileMenuOpen(true)} />
        <main className="pt-16 p-4 sm:p-6 lg:p-8 min-h-screen bg-[#fafafa] flex-1">
          {children}
        </main>
      </div>
    </div>
  );
}

