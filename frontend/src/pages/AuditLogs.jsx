/**
 * Audit Logs Page.
 * Visual security trail showing all policy decisions, approval actions,
 * price tampering attempts, duplicate detection events, and webhook validations.
 */
import { useState, useEffect } from 'react';
import { auditAPI } from '../services/api';

export default function AuditLogs() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [actorFilter, setActorFilter] = useState('');

  useEffect(() => {
    loadLogs();
  }, [actorFilter]);

  const loadLogs = async () => {
    setLoading(true);
    try {
      const res = await auditAPI.list({
        actor_type: actorFilter || undefined,
        limit: 50,
      });
      setLogs(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const getActorBadge = (actor) => {
    switch (actor) {
      case 'user':
        return 'bg-blue-100 text-blue-800';
      case 'agent':
        return 'bg-purple-100 text-purple-800';
      case 'system':
        return 'bg-slate-100 text-slate-800';
      case 'payment_provider':
        return 'bg-emerald-100 text-emerald-800';
      default:
        return 'bg-slate-100 text-slate-700';
    }
  };

  return (
    <div className="max-w-5xl mx-auto px-4 py-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between pb-4 mb-4 gap-3">
        <div>
          <h1 className="text-2xl font-bold text-slate-800 flex items-center gap-2">
            <span>🔍</span> Security Audit & Event Trail
          </h1>
          <p className="text-slate-500 text-sm mt-0.5">
            Immutable log of all policy evaluations, authorization decisions, and gateway webhook events.
          </p>
        </div>

        {/* Filter */}
        <div className="flex items-center gap-2 text-xs">
          <span className="text-slate-500 font-semibold">Filter Actor:</span>
          <select
            value={actorFilter}
            onChange={(e) => setActorFilter(e.target.value)}
            className="px-3 py-1.5 border border-slate-300 rounded-lg outline-none bg-white font-medium"
          >
            <option value="">All Actors</option>
            <option value="user">User</option>
            <option value="agent">AI Agent</option>
            <option value="system">Policy Engine / System</option>
            <option value="payment_provider">Payment Gateway</option>
          </select>
        </div>
      </div>

      <div className="bg-white border border-slate-200 rounded-2xl shadow-sm overflow-hidden">
        {loading ? (
          <div className="p-8 text-center text-slate-400">Loading audit trail...</div>
        ) : logs.length === 0 ? (
          <div className="p-8 text-center text-slate-400">
            <span className="text-3xl block mb-2">📜</span>
            <p className="font-medium text-slate-600">No audit events recorded yet.</p>
          </div>
        ) : (
          <div className="divide-y divide-slate-100">
            {logs.map((log) => (
              <div key={log.id} className="p-4 hover:bg-slate-50/70 transition flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 text-xs">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className={`px-2 py-0.5 rounded-full font-bold uppercase text-[10px] ${getActorBadge(log.actor_type)}`}>
                      {log.actor_type}
                    </span>
                    <strong className="text-slate-900 font-mono text-[11px]">{log.action}</strong>
                    {log.payment_request_id && (
                      <span className="text-slate-400 font-mono text-[10px]">
                        req:#{log.payment_request_id.slice(0, 8)}
                      </span>
                    )}
                  </div>
                  <p className="text-slate-600 pl-1">{log.decision_reason || '—'}</p>
                </div>

                <div className="text-slate-400 text-[11px] whitespace-nowrap sm:text-right">
                  {new Date(log.created_at).toLocaleString()}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
