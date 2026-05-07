'use client';

import { useCallback, useEffect, useRef, useState } from 'react';
import { apiRequest } from '@/lib/api';
import type { VendorDashboardStats, VendorOrderStreamEvent, VendorProfile } from '@/lib/vendor-types';
import { useOrderStream } from '@/components/vendor/use-order-stream';
import { Bell, Store, TrendingUp, ClipboardList } from 'lucide-react';

export default function VendorDashboardPage() {
  const [profile, setProfile] = useState<VendorProfile | null>(null);
  const [stats, setStats] = useState<VendorDashboardStats | null>(null);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const [unreadOrders, setUnreadOrders] = useState(0);
  const [streamStatus, setStreamStatus] = useState<'live' | 'polling'>('live');
  const audioContextRef = useRef<AudioContext | null>(null);

  const loadDashboard = useCallback(async () => {
    const [profileRes, statsRes] = await Promise.all([
      apiRequest<VendorProfile>('/api/v1/vendor/profile'),
      apiRequest<VendorDashboardStats>('/api/v1/vendor/dashboard/stats'),
    ]);

    if (!profileRes.ok || !profileRes.data) {
      setError(profileRes.error || 'Failed to load profile');
      return;
    }

    if (!statsRes.ok || !statsRes.data) {
      setError(statsRes.error || 'Failed to load stats');
      return;
    }

    setProfile(profileRes.data);
    setStats(statsRes.data);
  }, []);

  useEffect(() => {
    void loadDashboard();
  }, [loadDashboard]);

  useEffect(() => {
    const timer = window.setInterval(() => {
      void loadDashboard();
    }, 20000);
    return () => window.clearInterval(timer);
  }, [loadDashboard]);

  const handleStreamEvent = useCallback((event: VendorOrderStreamEvent) => {
    setUnreadOrders((current) => current + 1);
    setError('');
    setStats((current) =>
      current
        ? {
            ...current,
            orders_today: event.total_orders,
          }
        : current,
    );

    if (typeof window !== 'undefined') {
      const AudioContextClass = window.AudioContext || (window as Window & { webkitAudioContext?: typeof AudioContext }).webkitAudioContext;
      if (AudioContextClass) {
        if (!audioContextRef.current) {
          audioContextRef.current = new AudioContextClass();
        }
        const context = audioContextRef.current;
        const oscillator = context.createOscillator();
        const gain = context.createGain();
        oscillator.frequency.value = 880;
        oscillator.type = 'sine';
        gain.gain.value = 0.02;
        oscillator.connect(gain);
        gain.connect(context.destination);
        oscillator.start();
        oscillator.stop(context.currentTime + 0.18);
      }
    }
  }, []);

  useOrderStream({
    onOrderEvent: handleStreamEvent,
    onError: () => setStreamStatus('polling'),
  });

  async function toggleOpen(nextOpen: boolean) {
    setBusy(true);
    setError('');

    const res = await apiRequest<{ message: string; is_open: boolean }>(
      '/api/v1/vendor/toggle-open',
      {
        method: 'PUT',
        body: JSON.stringify({ is_open: nextOpen }),
      },
    );

    setBusy(false);

    if (!res.ok || !res.data) {
      setError(res.error || 'Unable to update open status');
      return;
    }

    setProfile((prev) => (prev ? { ...prev, is_open: res.data!.is_open } : prev));
  }

  return (
    <section className="space-y-6">
      <header className="rounded-2xl glass border border-border p-5 md:p-6">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl md:text-3xl font-bold text-foreground">Vendor Dashboard</h1>
            <p className="text-foreground/70 mt-1">{profile?.business_name || 'Loading business...'}</p>
          </div>
          <div className="flex items-center gap-2 rounded-full border border-border bg-card px-3 py-2 text-xs text-foreground/70">
            <Bell className="h-4 w-4 text-primary" />
            <span>{streamStatus === 'live' ? 'Live order stream' : 'Polling fallback active'}</span>
            {unreadOrders > 0 ? (
              <span className="rounded-full bg-primary px-2 py-0.5 text-primary-foreground">
                {unreadOrders}
              </span>
            ) : null}
          </div>
        </div>

        <div className="mt-4 flex items-center gap-3">
          <span
            className={`inline-flex rounded-full px-3 py-1 text-xs font-medium ${
              profile?.is_open
                ? 'bg-emerald-500/15 text-emerald-300 border border-emerald-500/20'
                : 'bg-card text-foreground/70 border border-border'
            }`}
          >
            {profile?.is_open ? 'Open' : 'Closed'}
          </span>
          <button
            onClick={() => toggleOpen(!profile?.is_open)}
            disabled={busy}
            className="btn-primary disabled:opacity-50"
          >
            {busy ? 'Saving...' : profile?.is_open ? 'Close Store' : 'Open Store'}
          </button>
        </div>
      </header>

      {error ? (
        <p className="rounded-lg border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-200">
          {error}
        </p>
      ) : null}

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <article className="rounded-2xl glass-hover p-5">
          <div className="mb-2 flex items-center gap-2 text-sm text-foreground/60">
            <ClipboardList className="h-4 w-4 text-primary" />
            <span>Orders Today</span>
          </div>
          <p className="mt-2 text-3xl font-bold text-foreground">{stats?.orders_today ?? 0}</p>
        </article>
        <article className="rounded-2xl glass-hover p-5">
          <div className="mb-2 flex items-center gap-2 text-sm text-foreground/60">
            <TrendingUp className="h-4 w-4 text-primary" />
            <span>Revenue Today</span>
          </div>
          <p className="mt-2 text-3xl font-bold text-foreground">₦{stats?.revenue_today ?? '0.00'}</p>
        </article>
        <article className="rounded-2xl glass-hover p-5">
          <div className="mb-2 flex items-center gap-2 text-sm text-foreground/60">
            <Store className="h-4 w-4 text-primary" />
            <span>Total Orders</span>
          </div>
          <p className="mt-2 text-3xl font-bold text-foreground">{stats?.total_orders ?? 0}</p>
        </article>
        <article className="rounded-2xl glass-hover p-5">
          <p className="text-sm text-foreground/60">Catalogue Items</p>
          <p className="mt-2 text-3xl font-bold text-foreground">{stats?.catalogue_items ?? 0}</p>
        </article>
      </div>
    </section>
  );
}
