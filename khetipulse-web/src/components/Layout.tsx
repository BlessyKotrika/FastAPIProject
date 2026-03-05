import React, { useEffect, useState } from 'react';
import { Home, TrendingUp, BookOpen, MessageSquare, Menu, User, Bell, LayoutDashboard } from 'lucide-react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useTranslation } from '@/lib/i18n';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export default function Layout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const { t } = useTranslation();
  const [isOffline, setIsOffline] = useState(false);

  const navItems = [
    { label: t('nav.dashboard'), icon: Home, path: '/' },
    { label: t('nav.mandi'), icon: TrendingUp, path: '/mandi' },
    { label: t('nav.policies'), icon: BookOpen, path: '/policies' },
    { label: t('nav.advisor'), icon: MessageSquare, path: '/advisor' },
  ];

  useEffect(() => {
    setIsOffline(!navigator.onLine);
    const handleOnline = () => setIsOffline(false);
    const handleOffline = () => setIsOffline(true);
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col max-w-md mx-auto relative shadow-2xl border-x border-slate-200">
      {/* Header */}
      <header className="sticky top-0 z-30 bg-white/80 backdrop-blur-md border-b border-slate-100 p-4 flex justify-between items-center">
        <div className="flex items-center gap-2">
          <div className="bg-primary-600 p-1.5 rounded-xl shadow-lg shadow-primary-100">
            <LayoutDashboard className="text-white w-5 h-5" />
          </div>
          <div>
            <h1 className="text-lg font-bold tracking-tight text-slate-900 leading-none">KhetiPulse</h1>
            <p className="text-[10px] font-semibold text-primary-600 uppercase tracking-widest">{t('common.smartAgri')}</p>
          </div>
        </div>
        <div className="flex gap-2">
          <button 
            onClick={() => alert(t('more.notifications') + ': ' + t('common.loading'))}
            className="p-2 bg-slate-100 text-slate-600 rounded-xl hover:bg-slate-200 transition-colors"
          >
            <Bell className="w-5 h-5" />
          </button>
          <Link 
            href="/more"
            className="p-2 bg-slate-100 text-slate-600 rounded-xl hover:bg-slate-200 transition-colors"
          >
            <User className="w-5 h-5" />
          </Link>
        </div>
      </header>

      {/* Offline Banner */}
      {isOffline && (
        <div className="bg-amber-100 text-amber-800 text-[10px] py-1.5 px-4 text-center font-bold uppercase tracking-wider animate-pulse border-b border-amber-200">
          {t('common.offline')}
        </div>
      )}

      {/* Main Content */}
      <main className="flex-1 pb-24 overflow-y-auto">
        {children}
      </main>

      {/* Bottom Navigation */}
      <div className="fixed bottom-6 left-1/2 -translate-x-1/2 w-[92%] max-w-[360px] z-40">
        <nav className="bg-slate-900/90 backdrop-blur-xl border border-white/10 px-3 py-2 flex justify-around items-center rounded-full shadow-2xl shadow-slate-900/20">
          {navItems.map((item) => {
            const isActive = pathname === item.path;
            return (
              <Link 
                key={item.path} 
                href={item.path}
                className={cn(
                  "flex flex-col items-center gap-1 p-2 rounded-full transition-all duration-300",
                  isActive ? "text-primary-400 bg-white/10 scale-105 px-4" : "text-slate-400 hover:text-white"
                )}
              >
                <item.icon className={cn("w-5 h-5", isActive && "stroke-[2.5px]")} />
                <span className="text-[8px] font-bold uppercase tracking-tight">{item.label}</span>
              </Link>
            );
          })}
        </nav>
      </div>
    </div>
  );
}
