'use client';

import { useEffect, useState } from 'react';
import { apiRequest } from '@/lib/api';
import type { VendorEarningsResponse } from '@/lib/vendor-types';

export default function VendorEarningsPage() {
  const [earnings, setEarnings] = useState<VendorEarningsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    async function load() {
      const res = await apiRequest<VendorEarningsResponse>('/api/v1/vendor/earnings');
      setLoading(false);
      if (!res.ok || !res.data) {
        setError(res.error || 'Failed to load earnings');
        return;
      }
      setEarnings(res.data);
    }

    void load();
  }, []);

  return (
    <section className="space-y-6">
      <header className="rounded-2xl glass border border-border p-5 md:p-6">
        <h1 className="text-2xl md:text-3xl font-bold text-foreground">Earnings</h1>
        <p className="text-foreground/70 mt-1">Track settled payouts and pending escrow releases.</p>
      </header>

      {error ? (
        <p className="rounded-lg border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-200">{error}</p>
      ) : null}

      <div className="grid gap-4 sm:grid-cols-3">
        <article className="rounded-2xl glass-hover p-5">
          <p className="text-sm text-foreground/60">Total Earned</p>
          <p className="mt-2 text-3xl font-bold text-foreground">₦{earnings?.summary.total_earned ?? '0.00'}</p>
        </article>
        <article className="rounded-2xl glass-hover p-5">
          <p className="text-sm text-foreground/60">This Month</p>
          <p className="mt-2 text-3xl font-bold text-foreground">₦{earnings?.summary.this_month ?? '0.00'}</p>
        </article>
        <article className="rounded-2xl glass-hover p-5">
          <p className="text-sm text-foreground/60">Pending Escrow</p>
          <p className="mt-2 text-3xl font-bold text-foreground">₦{earnings?.summary.pending_escrow ?? '0.00'}</p>
        </article>
      </div>

      <div className="rounded-2xl glass p-5 border border-border">
        <h2 className="text-lg font-semibold text-foreground">Payout History</h2>

        {loading ? <p className="mt-3 text-foreground/70">Loading history...</p> : null}
        {!loading && earnings?.history.length === 0 ? (
          <p className="mt-3 text-foreground/70">No payouts yet.</p>
        ) : null}

        <div className="mt-3 space-y-3">
          {earnings?.history.map((row) => (
            <article key={row.id} className="rounded-xl border border-border bg-card/60 p-4">
              <div className="flex flex-wrap items-center justify-between gap-2">
                  <p className="font-medium text-foreground">Order {row.order_id.slice(0, 8)}...</p>
                  <p className="font-semibold text-primary">₦{row.amount}</p>
              </div>
                <p className="mt-1 text-sm text-foreground/60">
                Status: {row.status} · Created: {new Date(row.created_at).toLocaleString()}
              </p>
              {row.released_at ? (
                  <p className="mt-1 text-sm text-emerald-300">
                  Released: {new Date(row.released_at).toLocaleString()}
                </p>
              ) : null}
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
