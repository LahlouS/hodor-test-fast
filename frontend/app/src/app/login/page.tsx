'use client';

import { useState, FormEvent } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '../../hooks/useAuth';
import PublicRoute from '../../components/PublicRoute';

function LoginForm() {
  const { login } = useAuth();
  const router = useRouter();

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setSubmitting(true);
    try {
      await login(username, password);
      router.replace('/dashboard');
    } catch {
      setError('Invalid username or password.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="relative min-h-screen flex items-center justify-center overflow-hidden">
      {/* Background blobs */}
      <div
        className="animate-float absolute -top-32 -left-32 w-96 h-96 rounded-full opacity-20 blur-3xl pointer-events-none"
        style={{ background: 'radial-gradient(circle, var(--color-accent-purple), transparent 70%)' }}
      />
      <div
        className="animate-float-delayed absolute -bottom-32 -right-32 w-96 h-96 rounded-full opacity-20 blur-3xl pointer-events-none"
        style={{ background: 'radial-gradient(circle, var(--color-accent-blue), transparent 70%)' }}
      />

      {/* Card */}
      <div className="glass-panel relative z-10 w-full max-w-md mx-4 rounded-2xl p-10">
        <div className="mb-8 text-center">
          <div
            className="inline-flex items-center justify-center w-14 h-14 rounded-2xl mb-4"
            style={{ background: 'var(--color-active-link-bg)', border: '1px solid rgba(99,102,241,0.3)' }}
          >
            <svg className="w-7 h-7" fill="none" viewBox="0 0 24 24" stroke="currentColor" style={{ color: 'var(--color-accent-purple)' }}>
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
            </svg>
          </div>
          <h1 className="text-2xl font-semibold" style={{ color: 'var(--color-text-primary)' }}>Welcome back</h1>
          <p className="mt-1 text-sm" style={{ color: 'var(--color-text-secondary)' }}>Sign in to your account</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label className="block text-sm font-medium mb-2" style={{ color: 'var(--color-text-secondary)' }}>Username</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              autoComplete="username"
              placeholder="your_username"
              className="w-full rounded-xl px-4 py-3 text-sm outline-none transition-all"
              style={{ background: 'rgba(255,255,255,0.05)', border: '1px solid var(--color-card-border)', color: 'var(--color-text-primary)' }}
              onFocus={(e) => (e.currentTarget.style.borderColor = 'rgba(99,102,241,0.6)')}
              onBlur={(e) => (e.currentTarget.style.borderColor = 'var(--color-card-border)')}
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2" style={{ color: 'var(--color-text-secondary)' }}>Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              autoComplete="current-password"
              placeholder="••••••••"
              className="w-full rounded-xl px-4 py-3 text-sm outline-none transition-all"
              style={{ background: 'rgba(255,255,255,0.05)', border: '1px solid var(--color-card-border)', color: 'var(--color-text-primary)' }}
              onFocus={(e) => (e.currentTarget.style.borderColor = 'rgba(99,102,241,0.6)')}
              onBlur={(e) => (e.currentTarget.style.borderColor = 'var(--color-card-border)')}
            />
          </div>

          {error && (
            <p className="text-sm text-center rounded-xl px-4 py-3" style={{ color: '#f87171', background: 'rgba(248,113,113,0.08)', border: '1px solid rgba(248,113,113,0.2)' }}>
              {error}
            </p>
          )}

          <button
            type="submit"
            disabled={submitting}
            className="w-full rounded-xl py-3 text-sm font-semibold transition-all disabled:opacity-50"
            style={{ background: 'linear-gradient(135deg, var(--color-accent-purple), var(--color-accent-blue))', color: 'white' }}
          >
            {submitting ? 'Signing in…' : 'Sign in'}
          </button>
        </form>
      </div>
    </div>
  );
}

export default function LoginPage() {
  return (
    <PublicRoute>
      <LoginForm />
    </PublicRoute>
  );
}
