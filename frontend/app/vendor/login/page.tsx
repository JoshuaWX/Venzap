'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { FormEvent, useState } from 'react';
import { apiRequest } from '@/lib/api';

type AuthMessage = {
  message: string;
  account_id?: string;
};

export default function VendorLoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError('');
    setSubmitting(true);

    const res = await apiRequest<AuthMessage>('/api/v1/auth/vendor/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });

    setSubmitting(false);

    if (!res.ok) {
      setError(res.error || 'Login failed');
      return;
    }

    router.push('/vendor/dashboard');
  }

  return (
    <main className="min-h-screen bg-slate-950 text-white flex items-center justify-center px-4">
      <div className="w-full max-w-md rounded-2xl border border-white/10 bg-white/5 p-6 shadow-xl">
        <h1 className="text-2xl font-bold">Vendor Login</h1>
        <p className="mt-1 text-sm text-white/70">Access your Venzap dashboard.</p>

        <form onSubmit={onSubmit} className="mt-6 space-y-4">
          <label className="block text-sm">
            <span className="mb-1 block text-white/80">Email</span>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full rounded-lg border border-white/20 bg-black/30 px-3 py-2 outline-none focus:border-orange-400"
            />
          </label>

          <label className="block text-sm">
            <span className="mb-1 block text-white/80">Password</span>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full rounded-lg border border-white/20 bg-black/30 px-3 py-2 outline-none focus:border-orange-400"
            />
          </label>

          {error ? <p className="text-sm text-red-300">{error}</p> : null}

          <button
            disabled={submitting}
            className="w-full rounded-lg bg-orange-500 py-2.5 font-semibold text-white hover:bg-orange-400 disabled:opacity-50"
          >
            {submitting ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        <p className="mt-4 text-sm text-white/70">
          New vendor?{' '}
          <Link href="/vendor/register" className="text-orange-300 hover:text-orange-200">
            Create account
          </Link>
        </p>
      </div>
    </main>
  );
}
