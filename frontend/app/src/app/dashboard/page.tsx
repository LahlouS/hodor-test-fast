'use client';

import { useEffect, useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '../../hooks/useAuth';
import { useAuthenticatedApi } from '../../hooks/useAuthenticatedApi';
import ProtectedRoute from '../../components/ProtectedRoute';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// ─── Types ────────────────────────────────────────────────────────────────────
interface Agent   { agent_id: string; user_id: string; name: string; is_active: boolean; }
interface Service { service_id: string; name: string; manifest: { routes?: { endpoint: string; permission?: string }[] } | null; }
interface LogEntry { log_id: string; endpoint: string; is_success: boolean; message?: string | null; log_timestamp: string; }

// ─── Copy button ──────────────────────────────────────────────────────────────
function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);
  const copy = () => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };
  return (
    <button onClick={copy} className="shrink-0 text-xs px-3 py-1.5 rounded-lg transition-all"
      style={{ background: 'var(--color-hover-bg)', color: copied ? '#4ade80' : 'var(--color-text-secondary)' }}>
      {copied ? '✓' : 'Copy'}
    </button>
  );
}

// ─── Main content ─────────────────────────────────────────────────────────────
function DashboardContent() {
  const { logout } = useAuth();
  const { authenticatedFetch } = useAuthenticatedApi();
  const router = useRouter();

  const [agents, setAgents]               = useState<Agent[]>([]);
  const [services, setServices]           = useState<Service[]>([]);
  const [selected, setSelected]           = useState<Agent | null>(null);
  const [agentServices, setAgentServices] = useState<Service[]>([]);
  const [logs, setLogs]                   = useState<LogEntry[]>([]);
  const [logsVisible, setLogsVisible]     = useState(false);
  const [loadingLogs, setLoadingLogs]     = useState(false);
  const [newName, setNewName]             = useState('');
  const [creating, setCreating]           = useState(false);
  const [pickService, setPickService]     = useState('');
  const [attaching, setAttaching]         = useState(false);

  const fetchAgents = useCallback(async () => {
    const r = await authenticatedFetch(`${API_URL}/logic/agents`);
    if (r.ok) setAgents(await r.json());
  }, [authenticatedFetch]);

  const fetchServices = useCallback(async () => {
    const r = await authenticatedFetch(`${API_URL}/logic/services`);
    if (r.ok) setServices(await r.json());
  }, [authenticatedFetch]);

  useEffect(() => { fetchAgents(); fetchServices(); }, [fetchAgents, fetchServices]);

  const selectAgent = useCallback(async (agent: Agent) => {
    setSelected(agent);
    setLogsVisible(false);
    setLogs([]);
    const r = await authenticatedFetch(`${API_URL}/logic/agents/${agent.agent_id}/services`);
    if (r.ok) setAgentServices(await r.json());
  }, [authenticatedFetch]);

  const createAgent = async () => {
    if (!newName.trim()) return;
    setCreating(true);
    try {
      const r = await authenticatedFetch(`${API_URL}/logic/agents`, { method: 'POST', body: { name: newName.trim() } });
      if (r.ok) { setNewName(''); await fetchAgents(); }
    } finally { setCreating(false); }
  };

  const attachService = async () => {
    if (!selected || !pickService) return;
    setAttaching(true);
    try {
      const r = await authenticatedFetch(`${API_URL}/logic/agents/services`, {
        method: 'POST',
        body: { agent_id: selected.agent_id, service_id: pickService },
      });
      if (r.ok) {
        setPickService('');
        const r2 = await authenticatedFetch(`${API_URL}/logic/agents/${selected.agent_id}/services`);
        if (r2.ok) setAgentServices(await r2.json());
      }
    } finally { setAttaching(false); }
  };

  const loadLogs = async () => {
    if (!selected) return;
    setLoadingLogs(true);
    setLogsVisible(true);
    try {
      const r = await authenticatedFetch(`${API_URL}/logic/agents/${selected.agent_id}/logs`);
      if (r.ok) setLogs(await r.json());
    } finally { setLoadingLogs(false); }
  };

  const attachedIds = new Set(agentServices.map(s => s.service_id));
  const available   = services.filter(s => !attachedIds.has(s.service_id));

  return (
    <div className="min-h-screen flex flex-col" style={{ height: '100vh' }}>

      {/* Navbar */}
      <nav className="glass-panel flex items-center justify-between px-8 py-4 shrink-0"
        style={{ borderTop: 'none', borderLeft: 'none', borderRight: 'none' }}>
        <span className="font-semibold text-sm" style={{ color: 'var(--color-text-primary)' }}>Hodor</span>
        <button onClick={async () => { await logout(); router.replace('/login'); }}
          className="text-sm px-4 py-2 rounded-xl"
          style={{ background: 'var(--color-hover-bg)', color: 'var(--color-text-secondary)' }}>
          Logout
        </button>
      </nav>

      <div className="flex flex-1 overflow-hidden">

        {/* ── Left sidebar: agent list ── */}
        <aside className="w-64 flex flex-col gap-3 p-5 overflow-y-auto custom-scrollbar shrink-0"
          style={{ borderRight: '1px solid var(--color-card-border)' }}>

          <p className="text-xs font-semibold uppercase tracking-widest mb-1" style={{ color: 'var(--color-text-secondary)' }}>Agents</p>

          {/* Create */}
          <div className="flex flex-col gap-2">
            <input
              value={newName}
              onChange={e => setNewName(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && createAgent()}
              placeholder="Agent name…"
              className="w-full rounded-xl px-3 py-2 text-sm outline-none"
              style={{ background: 'rgba(255,255,255,0.05)', border: '1px solid var(--color-card-border)', color: 'var(--color-text-primary)' }}
            />
            <button onClick={createAgent} disabled={creating || !newName.trim()}
              className="w-full py-2 rounded-xl text-sm font-semibold transition-all disabled:opacity-40"
              style={{ background: 'linear-gradient(135deg, var(--color-accent-purple), var(--color-accent-blue))', color: 'white' }}>
              {creating ? 'Creating…' : '+ Create agent'}
            </button>
          </div>

          {/* List */}
          {agents.length === 0
            ? <p className="text-xs text-center py-6" style={{ color: 'var(--color-text-secondary)' }}>No agents yet</p>
            : agents.map(a => (
              <button key={a.agent_id} onClick={() => selectAgent(a)}
                className="text-left px-4 py-3 rounded-xl transition-all"
                style={{
                  background: selected?.agent_id === a.agent_id ? 'var(--color-active-link-bg)' : 'var(--color-hover-bg)',
                  border: `1px solid ${selected?.agent_id === a.agent_id ? 'rgba(99,102,241,0.3)' : 'transparent'}`,
                }}>
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium truncate" style={{ color: 'var(--color-text-primary)' }}>{a.name}</span>
                  <span className={`w-2 h-2 rounded-full ml-2 shrink-0 ${a.is_active ? 'bg-green-400' : 'bg-gray-500'}`} />
                </div>
              </button>
            ))
          }
        </aside>

        {/* ── Right panel: agent detail ── */}
        <main className="flex-1 overflow-y-auto custom-scrollbar p-8">
          {!selected ? (
            <div className="flex h-full items-center justify-center">
              <p style={{ color: 'var(--color-text-secondary)' }}>Select or create an agent</p>
            </div>
          ) : (
            <div className="max-w-2xl mx-auto space-y-5">

              {/* Agent ID / bearer token */}
              <div className="glass-card rounded-2xl p-6 space-y-3">
                <div className="flex items-center justify-between">
                  <h1 className="font-semibold" style={{ color: 'var(--color-text-primary)' }}>{selected.name}</h1>
                  <span className="text-xs px-2 py-1 rounded-full"
                    style={{ background: selected.is_active ? 'rgba(74,222,128,0.1)' : 'rgba(156,163,175,0.1)', color: selected.is_active ? '#4ade80' : '#9ca3af' }}>
                    {selected.is_active ? 'active' : 'inactive'}
                  </span>
                </div>
                <p className="text-xs" style={{ color: 'var(--color-text-secondary)' }}>Bearer token — use this as <code>Authorization: Bearer &lt;token&gt;</code></p>
                <div className="flex items-center gap-2">
                  <code className="flex-1 rounded-lg px-3 py-2 text-xs font-mono truncate"
                    style={{ background: 'rgba(0,0,0,0.35)', color: 'var(--color-accent-purple)' }}>
                    {selected.agent_id}
                  </code>
                  <CopyButton text={selected.agent_id} />
                </div>
              </div>

              {/* Services + middleware URLs */}
              <div className="glass-card rounded-2xl p-6 space-y-4">
                <h2 className="text-sm font-semibold" style={{ color: 'var(--color-text-primary)' }}>Services</h2>

                {/* Attach service */}
                {available.length > 0 && (
                  <div className="flex gap-2">
                    <select value={pickService} onChange={e => setPickService(e.target.value)}
                      className="flex-1 rounded-xl px-3 py-2 text-sm outline-none"
                      style={{ background: 'rgba(255,255,255,0.05)', border: '1px solid var(--color-card-border)', color: 'var(--color-text-primary)' }}>
                      <option value="" style={{ background: '#1e293b' }}>Attach a service…</option>
                      {available.map(s => <option key={s.service_id} value={s.service_id} style={{ background: '#1e293b' }}>{s.name}</option>)}
                    </select>
                    <button onClick={attachService} disabled={attaching || !pickService}
                      className="px-4 py-2 rounded-xl text-sm font-semibold disabled:opacity-40"
                      style={{ background: 'linear-gradient(135deg, var(--color-accent-purple), var(--color-accent-blue))', color: 'white' }}>
                      Attach
                    </button>
                  </div>
                )}

                {/* Attached services → middleware URLs */}
                {agentServices.length === 0
                  ? <p className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>No services attached yet.</p>
                  : agentServices.map(svc => {
                    const routes = svc.manifest?.routes ?? [];
                    return (
                      <div key={svc.service_id} className="rounded-xl p-4 space-y-3"
                        style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid var(--color-card-border)' }}>
                        <p className="text-sm font-medium" style={{ color: 'var(--color-text-primary)' }}>{svc.name}</p>
                        {routes.length === 0
                          ? <p className="text-xs" style={{ color: 'var(--color-text-secondary)' }}>No routes in manifest.</p>
                          : routes.map(route => {
                            const url = `${API_URL}/middleware/${svc.name}/${route.endpoint}`;
                            return (
                              <div key={route.endpoint} className="space-y-1">
                                <p className="text-xs" style={{ color: 'var(--color-text-secondary)' }}>
                                  <span className="font-mono" style={{ color: 'var(--color-accent-blue)' }}>/{route.endpoint}</span>
                                  {route.permission && <span className="ml-2 opacity-60">({route.permission})</span>}
                                </p>
                                <div className="flex items-center gap-2">
                                  <code className="flex-1 rounded-lg px-3 py-2 text-xs font-mono truncate"
                                    style={{ background: 'rgba(0,0,0,0.35)', color: 'var(--color-text-primary)' }}>
                                    {url}
                                  </code>
                                  <CopyButton text={url} />
                                </div>
                              </div>
                            );
                          })
                        }
                      </div>
                    );
                  })
                }
              </div>

              {/* Logs */}
              <div className="glass-card rounded-2xl p-6 space-y-4">
                <div className="flex items-center justify-between">
                  <h2 className="text-sm font-semibold" style={{ color: 'var(--color-text-primary)' }}>Logs</h2>
                  <button onClick={loadLogs} disabled={loadingLogs}
                    className="text-xs px-3 py-1.5 rounded-lg disabled:opacity-40"
                    style={{ background: 'var(--color-hover-bg)', color: 'var(--color-text-secondary)' }}>
                    {loadingLogs ? 'Loading…' : logsVisible ? 'Refresh' : 'Load logs'}
                  </button>
                </div>

                {logsVisible && (
                  logs.length === 0
                    ? <p className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>No logs yet.</p>
                    : <div className="space-y-1.5 max-h-64 overflow-y-auto custom-scrollbar">
                      {logs.map(log => (
                        <div key={log.log_id} className="flex items-center gap-3 text-xs rounded-lg px-3 py-2"
                          style={{ background: 'rgba(0,0,0,0.25)' }}>
                          <span className={`w-2 h-2 rounded-full shrink-0 ${log.is_success ? 'bg-green-400' : 'bg-red-400'}`} />
                          <span className="font-mono w-32 truncate" style={{ color: 'var(--color-accent-blue)' }}>{log.endpoint}</span>
                          <span className="flex-1 truncate" style={{ color: 'var(--color-text-secondary)' }}>{log.message ?? '—'}</span>
                          <span className="shrink-0" style={{ color: 'var(--color-text-secondary)' }}>
                            {new Date(log.log_timestamp).toLocaleTimeString()}
                          </span>
                        </div>
                      ))}
                    </div>
                )}
              </div>

            </div>
          )}
        </main>
      </div>
    </div>
  );
}

export default function DashboardPage() {
  return (
    <ProtectedRoute>
      <DashboardContent />
    </ProtectedRoute>
  );
}
