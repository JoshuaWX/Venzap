'use client';

import { useEffect, useState } from 'react';
import { apiRequest } from '@/lib/api';
import type { OrderListResponse } from '@/lib/vendor-types';

const statuses = [
  'pending',
  'confirmed',
  'preparing',
  'out_for_delivery',
  'delivered',
  'cancelled',
] as const;

export default function VendorOrdersPage() {
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [orders, setOrders] = useState<OrderListResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  async function loadOrders(status: string) {
    setLoading(true);
    setError('');

    const query = status ? `?status=${encodeURIComponent(status)}` : '';
    const res = await apiRequest<OrderListResponse>(`/api/v1/vendor/orders${query}`);

    setLoading(false);

    if (!res.ok || !res.data) {
      setError(res.error || 'Failed to load orders');
      return;
    }

    setOrders(res.data);
  }

  useEffect(() => {
    void loadOrders(statusFilter);
  }, [statusFilter]);

  useEffect(() => {
    const timer = window.setInterval(() => {
      void loadOrders(statusFilter);
    }, 15000);
    return () => window.clearInterval(timer);
  }, [statusFilter]);

  async function updateOrderStatus(orderId: string, nextStatus: string) {
    setError('');
    const res = await apiRequest<{ id: string; status: string }>(
      `/api/v1/vendor/orders/${orderId}/status`,
      {
        method: 'PUT',
        body: JSON.stringify({ status: nextStatus }),
      },
    );

    if (!res.ok) {
      setError(res.error || 'Unable to update order status');
      return;
    }

    await loadOrders(statusFilter);
  }

  return (
    <section className="space-y-6">
      <header className="rounded-2xl glass border border-border p-5 md:p-6">
        <h1 className="text-2xl md:text-3xl font-bold text-foreground">Orders</h1>
        <p className="text-foreground/70 mt-1">Track and update every incoming order in real time.</p>
      </header>

      {error ? (
        <p className="rounded-lg border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-200">{error}</p>
      ) : null}

      <div className="rounded-2xl glass p-4 border border-border">
        <label className="text-sm text-foreground/70">Filter by status</label>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="mt-1 block w-full max-w-xs rounded-lg border border-border bg-background px-3 py-2 text-sm outline-none focus:border-primary"
        >
          <option value="">All</option>
          {statuses.map((status) => (
            <option key={status} value={status}>
              {status}
            </option>
          ))}
        </select>
      </div>

      <div className="space-y-3">
        {loading ? <p className="text-slate-600">Loading orders...</p> : null}

        {!loading && orders?.data.length === 0 ? (
          <p className="rounded-xl border border-border bg-card p-5 text-foreground/70">No orders found.</p>
        ) : null}

        {orders?.data.map((order) => (
          <article key={order.id} className="rounded-2xl glass-hover p-5">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <p className="font-semibold text-foreground">Order {order.id.slice(0, 8)}...</p>
                <p className="text-sm text-foreground/60">{new Date(order.created_at).toLocaleString()}</p>
                <p className="mt-1 text-sm text-foreground/80">Delivery: {order.delivery_address}</p>
              </div>
              <div className="text-right">
                <p className="text-xs text-foreground/60">Status</p>
                <p className="font-medium text-foreground">{order.status}</p>
                <p className="mt-1 font-semibold text-primary">₦{order.total}</p>
              </div>
            </div>

            <ul className="mt-3 space-y-1 text-sm text-foreground/80">
              {order.items.map((item, index) => (
                <li key={`${order.id}-${index}`}>
                  {item.name} x{item.quantity} (₦{item.price})
                </li>
              ))}
            </ul>

            <div className="mt-4 flex flex-wrap gap-2">
              {statuses.map((status) => (
                <button
                  key={status}
                  onClick={() => updateOrderStatus(order.id, status)}
                  className={`rounded-full px-3 py-1.5 text-xs font-medium ${
                    status === order.status
                      ? 'bg-primary text-primary-foreground'
                      : 'bg-card text-foreground/70 hover:bg-card/80'
                  }`}
                >
                  {status}
                </button>
              ))}
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
