'use client';

import { useRouter } from 'next/navigation';
import { useAuth } from '../hooks/useAuth';

export default function HomePage() {
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();

  const handleCTA = () => {
    router.push(isAuthenticated ? '/dashboard' : '/login');
  };

  return (
    <div className="relative min-h-screen flex flex-col items-center justify-center overflow-hidden">
      {/* Background blobs */}
      <div
        className="animate-float absolute top-0 left-1/4 w-[500px] h-[500px] rounded-full opacity-10 blur-3xl pointer-events-none"
        style={{ background: 'radial-gradient(circle, var(--color-accent-purple), transparent 70%)' }}
      />
      <div
        className="animate-float-delayed absolute bottom-0 right-1/4 w-[400px] h-[400px] rounded-full opacity-10 blur-3xl pointer-events-none"
        style={{ background: 'radial-gradient(circle, var(--color-accent-blue), transparent 70%)' }}
      />

      <main className="relative z-10 text-center px-8 max-w-2xl">
        {/* Badge */}
        <div className="inline-flex items-center gap-2 text-xs font-medium px-3 py-1.5 rounded-full mb-8"
          style={{ background: 'var(--color-active-link-bg)', border: '1px solid rgba(99,102,241,0.3)', color: 'var(--color-accent-purple)' }}>
          <span className="w-1.5 h-1.5 rounded-full" style={{ background: 'var(--color-accent-purple)' }} />
          Hodor Auth Demo
        </div>

        <h1 className="text-5xl font-bold mb-4 leading-tight" style={{ color: 'var(--color-text-primary)' }}>
          Hold the door.
        </h1>
        <p className="text-lg mb-12" style={{ color: 'var(--color-text-secondary)' }}>
          A minimal auth playground built with Next.js + FastAPI.
        </p>

        <button
          onClick={handleCTA}
          disabled={isLoading}
          className="inline-flex items-center gap-3 px-8 py-4 rounded-2xl text-sm font-semibold transition-all disabled:opacity-50"
          style={{ background: 'linear-gradient(135deg, var(--color-accent-purple), var(--color-accent-blue))', color: 'white' }}
        >
          {isLoading ? 'Loading…' : isAuthenticated ? 'Go to Dashboard →' : 'Sign in →'}
        </button>
      </main>
    </div>
  );
}
