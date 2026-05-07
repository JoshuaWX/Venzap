'use client';

import { FormEvent, useEffect, useState } from 'react';
import { apiRequest } from '@/lib/api';
import type { CatalogueItem, VendorProfile } from '@/lib/vendor-types';

type CatalogueCreatePayload = {
  name: string;
  description: string | null;
  price: number;
  emoji: string | null;
  category: string | null;
  is_available: boolean;
};

const initialForm = {
  name: '',
  description: '',
  price: '',
  emoji: '',
  category: '',
};

export default function VendorCataloguePage() {
  const [vendorId, setVendorId] = useState('');
  const [items, setItems] = useState<CatalogueItem[]>([]);
  const [form, setForm] = useState(initialForm);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  async function loadCatalogue() {
    setError('');
    const profileRes = await apiRequest<VendorProfile>('/api/v1/vendor/profile');
    if (!profileRes.ok || !profileRes.data) {
      setError(profileRes.error || 'Failed to load vendor profile');
      setLoading(false);
      return;
    }

    setVendorId(profileRes.data.id);

    const itemRes = await apiRequest<CatalogueItem[]>(
      `/api/v1/catalogue/vendor/${profileRes.data.id}?include_unavailable=true`,
    );

    if (!itemRes.ok || !itemRes.data) {
      setError(itemRes.error || 'Failed to load catalogue');
      setLoading(false);
      return;
    }

    setItems(itemRes.data);
    setLoading(false);
  }

  useEffect(() => {
    void loadCatalogue();
  }, []);

  async function createItem(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError('');
    setSaving(true);

    const payload: CatalogueCreatePayload = {
      name: form.name,
      description: form.description || null,
      price: Number(form.price || 0),
      emoji: form.emoji || null,
      category: form.category || null,
      is_available: true,
    };

    const res = await apiRequest<CatalogueItem>('/api/v1/catalogue', {
      method: 'POST',
      body: JSON.stringify(payload),
    });

    setSaving(false);

    if (!res.ok || !res.data) {
      setError(res.error || 'Failed to create item');
      return;
    }

    setItems((prev) => [res.data!, ...prev]);
    setForm(initialForm);
  }

  async function toggleItem(itemId: string) {
    setError('');
    const res = await apiRequest<CatalogueItem>(`/api/v1/catalogue/${itemId}/toggle`, {
      method: 'PUT',
      body: JSON.stringify({}),
    });

    if (!res.ok || !res.data) {
      setError(res.error || 'Failed to toggle item');
      return;
    }

    setItems((prev) => prev.map((item) => (item.id === itemId ? res.data! : item)));
  }

  async function deleteItem(itemId: string) {
    setError('');
    const res = await apiRequest<null>(`/api/v1/catalogue/${itemId}`, {
      method: 'DELETE',
    });

    if (!res.ok) {
      setError(res.error || 'Failed to delete item');
      return;
    }

    setItems((prev) => prev.filter((item) => item.id !== itemId));
  }

  return (
    <section className="space-y-6">
      <header className="rounded-2xl glass border border-border p-5 md:p-6">
        <h1 className="text-2xl md:text-3xl font-bold text-foreground">Catalogue</h1>
        <p className="text-foreground/70 mt-1">Add products, update stock, and control visibility.</p>
      </header>

      {error ? (
        <p className="rounded-lg border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-200">{error}</p>
      ) : null}

      <form onSubmit={createItem} className="grid gap-3 rounded-2xl glass p-5 sm:grid-cols-2 border border-border">
        <h2 className="sm:col-span-2 text-lg font-semibold text-foreground">Add Catalogue Item</h2>
        <input
          required
          placeholder="Item name"
          value={form.name}
          onChange={(e) => setForm((prev) => ({ ...prev, name: e.target.value }))}
          className="rounded-lg border border-border bg-background px-3 py-2 text-sm outline-none focus:border-primary"
        />
        <input
          placeholder="Category"
          value={form.category}
          onChange={(e) => setForm((prev) => ({ ...prev, category: e.target.value }))}
          className="rounded-lg border border-border bg-background px-3 py-2 text-sm outline-none focus:border-primary"
        />
        <input
          required
          type="number"
          min={0}
          step="0.01"
          placeholder="Price"
          value={form.price}
          onChange={(e) => setForm((prev) => ({ ...prev, price: e.target.value }))}
          className="rounded-lg border border-border bg-background px-3 py-2 text-sm outline-none focus:border-primary"
        />
        <input
          placeholder="Emoji"
          maxLength={10}
          value={form.emoji}
          onChange={(e) => setForm((prev) => ({ ...prev, emoji: e.target.value }))}
          className="rounded-lg border border-border bg-background px-3 py-2 text-sm outline-none focus:border-primary"
        />
        <textarea
          rows={3}
          placeholder="Description"
          value={form.description}
          onChange={(e) => setForm((prev) => ({ ...prev, description: e.target.value }))}
          className="sm:col-span-2 rounded-lg border border-border bg-background px-3 py-2 text-sm outline-none focus:border-primary"
        />
        <button
          disabled={saving}
          className="sm:col-span-2 btn-primary disabled:opacity-50"
        >
          {saving ? 'Saving...' : 'Add Item'}
        </button>
      </form>

      <div className="rounded-2xl glass p-5 border border-border">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-foreground">Current Items</h2>
          <span className="text-sm text-foreground/60">{vendorId ? `Vendor ${vendorId.slice(0, 8)}...` : ''}</span>
        </div>

        {loading ? <p className="text-foreground/70">Loading catalogue...</p> : null}
        {!loading && items.length === 0 ? <p className="text-foreground/70">No items yet.</p> : null}

        <ul className="space-y-3">
          {items.map((item) => (
            <li key={item.id} className="rounded-xl border border-border bg-card/60 p-4">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <p className="font-semibold text-foreground">
                    {item.emoji ? `${item.emoji} ` : ''}
                    {item.name}
                  </p>
                  <p className="text-sm text-foreground/60">
                    ₦{item.price} {item.category ? `· ${item.category}` : ''}
                  </p>
                  {item.description ? <p className="mt-1 text-sm text-foreground/70">{item.description}</p> : null}
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => toggleItem(item.id)}
                    className="rounded-md bg-card px-3 py-1.5 text-xs font-medium text-foreground/80 hover:bg-card/80"
                  >
                    {item.is_available ? 'Set Unavailable' : 'Set Available'}
                  </button>
                  <button
                    onClick={() => deleteItem(item.id)}
                    className="rounded-md bg-red-500/10 px-3 py-1.5 text-xs font-medium text-red-200 hover:bg-red-500/20"
                  >
                    Delete
                  </button>
                </div>
              </div>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
