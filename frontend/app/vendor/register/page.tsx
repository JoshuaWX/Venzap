'use client';

import Link from 'next/link';
import { FormEvent, useState } from 'react';
import { apiRequest } from '@/lib/api';

type AuthMessage = {
  message: string;
  account_id?: string;
};

type VerifyResponse = {
  message: string;
};

type RegisterForm = {
  business_name: string;
  email: string;
  phone: string;
  password: string;
  address: string;
  description: string;
  vendor_type: 'food' | 'grocery' | 'pharmacy' | 'laundry' | 'fashion' | 'other';
  delivery_fee: string;
};

const initialForm: RegisterForm = {
  business_name: '',
  email: '',
  phone: '',
  password: '',
  address: '',
  description: '',
  vendor_type: 'food',
  delivery_fee: '0',
};

export default function VendorRegisterPage() {
  const [form, setForm] = useState<RegisterForm>(initialForm);
  const [otp, setOtp] = useState('');
  const [registeredEmail, setRegisteredEmail] = useState('');
  const [step, setStep] = useState<'register' | 'verify'>('register');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  async function onRegister(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError('');
    setSuccess('');
    setSubmitting(true);

    const payload = {
      ...form,
      delivery_fee: Number(form.delivery_fee || 0),
      description: form.description || null,
    };

    const res = await apiRequest<AuthMessage>('/api/v1/auth/vendor/register', {
      method: 'POST',
      body: JSON.stringify(payload),
    });

    setSubmitting(false);

    if (!res.ok) {
      setError(res.error || 'Registration failed');
      return;
    }

    setRegisteredEmail(form.email);
    setStep('verify');
    setSuccess('Account created. Enter the OTP sent to your email.');
  }

  async function onVerify(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError('');
    setSuccess('');
    setSubmitting(true);

    const res = await apiRequest<VerifyResponse>('/api/v1/auth/verify-email', {
      method: 'POST',
      body: JSON.stringify({
        email: registeredEmail,
        otp,
        account_type: 'vendor',
      }),
    });

    setSubmitting(false);

    if (!res.ok) {
      setError(res.error || 'Verification failed');
      return;
    }

    setSuccess('Email verified. You can now log in.');
  }

  return (
    <main className="min-h-screen bg-slate-950 text-white flex items-center justify-center px-4 py-8">
      <div className="w-full max-w-2xl rounded-2xl border border-white/10 bg-white/5 p-6 shadow-xl">
        <h1 className="text-2xl font-bold">Vendor Registration</h1>
        <p className="mt-1 text-sm text-white/70">Launch your Venzap storefront in minutes.</p>

        {step === 'register' ? (
          <form onSubmit={onRegister} className="mt-6 grid gap-4 sm:grid-cols-2">
            <label className="block text-sm sm:col-span-2">
              <span className="mb-1 block text-white/80">Business Name</span>
              <input
                required
                value={form.business_name}
                onChange={(e) => setForm((prev) => ({ ...prev, business_name: e.target.value }))}
                className="w-full rounded-lg border border-white/20 bg-black/30 px-3 py-2 outline-none focus:border-orange-400"
              />
            </label>

            <label className="block text-sm">
              <span className="mb-1 block text-white/80">Email</span>
              <input
                type="email"
                required
                value={form.email}
                onChange={(e) => setForm((prev) => ({ ...prev, email: e.target.value }))}
                className="w-full rounded-lg border border-white/20 bg-black/30 px-3 py-2 outline-none focus:border-orange-400"
              />
            </label>

            <label className="block text-sm">
              <span className="mb-1 block text-white/80">Phone (e.g. 08012345678)</span>
              <input
                required
                value={form.phone}
                onChange={(e) => setForm((prev) => ({ ...prev, phone: e.target.value }))}
                className="w-full rounded-lg border border-white/20 bg-black/30 px-3 py-2 outline-none focus:border-orange-400"
              />
            </label>

            <label className="block text-sm">
              <span className="mb-1 block text-white/80">Password</span>
              <input
                type="password"
                required
                minLength={8}
                value={form.password}
                onChange={(e) => setForm((prev) => ({ ...prev, password: e.target.value }))}
                className="w-full rounded-lg border border-white/20 bg-black/30 px-3 py-2 outline-none focus:border-orange-400"
              />
            </label>

            <label className="block text-sm">
              <span className="mb-1 block text-white/80">Vendor Type</span>
              <select
                value={form.vendor_type}
                onChange={(e) =>
                  setForm((prev) => ({
                    ...prev,
                    vendor_type: e.target.value as RegisterForm['vendor_type'],
                  }))
                }
                className="w-full rounded-lg border border-white/20 bg-black/30 px-3 py-2 outline-none focus:border-orange-400"
              >
                <option value="food">Food</option>
                <option value="grocery">Grocery</option>
                <option value="pharmacy">Pharmacy</option>
                <option value="laundry">Laundry</option>
                <option value="fashion">Fashion</option>
                <option value="other">Other</option>
              </select>
            </label>

            <label className="block text-sm sm:col-span-2">
              <span className="mb-1 block text-white/80">Address</span>
              <textarea
                required
                rows={3}
                value={form.address}
                onChange={(e) => setForm((prev) => ({ ...prev, address: e.target.value }))}
                className="w-full rounded-lg border border-white/20 bg-black/30 px-3 py-2 outline-none focus:border-orange-400"
              />
            </label>

            <label className="block text-sm">
              <span className="mb-1 block text-white/80">Delivery Fee (NGN)</span>
              <input
                type="number"
                min={0}
                step="0.01"
                value={form.delivery_fee}
                onChange={(e) => setForm((prev) => ({ ...prev, delivery_fee: e.target.value }))}
                className="w-full rounded-lg border border-white/20 bg-black/30 px-3 py-2 outline-none focus:border-orange-400"
              />
            </label>

            <label className="block text-sm">
              <span className="mb-1 block text-white/80">Description (optional)</span>
              <input
                value={form.description}
                onChange={(e) => setForm((prev) => ({ ...prev, description: e.target.value }))}
                className="w-full rounded-lg border border-white/20 bg-black/30 px-3 py-2 outline-none focus:border-orange-400"
              />
            </label>

            {error ? <p className="text-sm text-red-300 sm:col-span-2">{error}</p> : null}
            {success ? <p className="text-sm text-emerald-300 sm:col-span-2">{success}</p> : null}

            <button
              disabled={submitting}
              className="sm:col-span-2 rounded-lg bg-orange-500 py-2.5 font-semibold hover:bg-orange-400 disabled:opacity-50"
            >
              {submitting ? 'Creating account...' : 'Create Vendor Account'}
            </button>
          </form>
        ) : (
          <form onSubmit={onVerify} className="mt-6 space-y-4">
            <p className="text-sm text-white/70">
              OTP sent to <span className="text-white">{registeredEmail}</span>
            </p>
            <label className="block text-sm">
              <span className="mb-1 block text-white/80">Verification OTP</span>
              <input
                required
                minLength={6}
                maxLength={6}
                value={otp}
                onChange={(e) => setOtp(e.target.value)}
                className="w-full rounded-lg border border-white/20 bg-black/30 px-3 py-2 outline-none focus:border-orange-400"
              />
            </label>

            {error ? <p className="text-sm text-red-300">{error}</p> : null}
            {success ? <p className="text-sm text-emerald-300">{success}</p> : null}

            <button
              disabled={submitting}
              className="w-full rounded-lg bg-orange-500 py-2.5 font-semibold hover:bg-orange-400 disabled:opacity-50"
            >
              {submitting ? 'Verifying...' : 'Verify Email'}
            </button>

            <Link href="/vendor/login" className="block text-sm text-orange-300 hover:text-orange-200">
              Continue to vendor login
            </Link>
          </form>
        )}
      </div>
    </main>
  );
}
