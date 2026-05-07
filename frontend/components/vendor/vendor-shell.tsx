'use client';

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { useEffect, useMemo, useState } from 'react';
import { apiRequest } from '@/lib/api';
import type { VendorProfile } from '@/lib/vendor-types';

type Props = {
  children: React.ReactNode;
};

const publicPaths = new Set(['/vendor/login', '/vendor/register']);

export function VendorShell({ children }: Props) {
  const pathname = usePathname();
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [profile, setProfile] = useState<VendorProfile | null>(null);

  const isPublicRoute = useMemo(() => {
    if (!pathname) {
      return false;
    }
    return publicPaths.has(pathname);
  }, [pathname]);

  useEffect(() => {
    if (isPublicRoute) {
      setLoading(false);
      return;
    }

    let active = true;

    async function checkAuth() {
      const res = await apiRequest<VendorProfile>('/api/v1/vendor/profile');
      if (!active) {
        return;
      }

      if (!res.ok || !res.data) {
        router.replace('/vendor/login');
        return;
      }

      setProfile(res.data);
      setLoading(false);
    }

    void checkAuth();

    return () => {
      active = false;
    };
  }, [isPublicRoute, router]);

  if (isPublicRoute) {
    return <>{children}</>;
  }

  if (loading) {
    return (
      <main className="min-h-screen bg-background flex items-center justify-center">
        <p className="text-foreground/70">Loading vendor workspace...</p>
      </main>
    );
  }

  const navItems = [
    { href: '/vendor/dashboard', label: 'Dashboard' },
    { href: '/vendor/catalogue', label: 'Catalogue' },
    { href: '/vendor/orders', label: 'Orders' },
    { href: '/vendor/earnings', label: 'Earnings' },
  ];

  return (
    <div className="min-h-screen bg-background text-foreground">
      <header className="sticky top-0 z-20 border-b border-border bg-background/85 backdrop-blur-xl">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
          <Link href="/vendor/dashboard" className="font-bold text-primary">
            Venzap Vendor
          </Link>
          <div className="text-sm text-foreground/70">
            {profile?.business_name || 'Vendor'}
          </div>
        </div>
        <nav className="mx-auto flex max-w-6xl gap-2 px-4 pb-3 overflow-x-auto">
          {navItems.map((item) => {
            const active = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`rounded-full px-4 py-2 text-sm transition ${
                  active
                    ? 'bg-primary text-primary-foreground'
                    : 'bg-card text-foreground/70 hover:bg-card/80'
                }`}
              >
                {item.label}
              </Link>
            );
          })}
          <Link
            href="/vendor/login"
            className="ml-auto rounded-full px-4 py-2 text-sm bg-card text-foreground/70 hover:bg-card/80"
          >
            Switch Account
          </Link>
        </nav>
      </header>
      <main className="mx-auto max-w-6xl px-4 py-6">{children}</main>
    </div>
  );
}
