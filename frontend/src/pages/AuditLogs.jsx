/**
 * Audit Logs Page with Blue, Grey, and Orange design system.
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
      setLogs(res.data || []);
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
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 animate-fade-in">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between pb-6 border-b border-slate-200 mb-8 gap-4">
        <div>
          <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-blue-50 border border-blue-200 text-blue-700 text-xs font-semibold mb-2">
            <span>🔍 Immutable Audit Trail</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
            Security & Audit Logs
          </h1>
          <p className="text-slate-600 text-sm mt-1">
            Tamper-evident event log recording policy triggers, approvals, and gateway events.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <select
            value={actorFilter}
            onChange={(e) => setActorFilter(e.target.value)}
            className="bg-white border border-slate-200 rounded-xl px-3 py-2 text-xs font-medium text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500 shadow-xs cursor-pointer"
          >
            <option value="">All Actors</option>
            <option value="user">User</option>
            <option value="agent">AI Agent</option>
            <option value="system">Policy Engine System</option>
            <option value="payment_provider">Payment Gateway</option>
          </select>
          <button
            onClick={loadLogs}
            className="px-3.5 py-2 text-xs font-semibold text-slate-700 bg-white border border-slate-200 rounded-xl hover:bg-slate-50 transition cursor-pointer shadow-xs"
          >
            🔄 Refresh
          </button>
        </div>
      </div>

      <div className="bg-white border border-slate-200 rounded-2xl shadow-xs overflow-hidden">
        {loading ? (
          <div className="p-8 text-center text-slate-400 text-xs">Loading audit events...</div>
        ) : logs.length === 0 ? (
          <div className="p-12 text-center text-slate-400 text-xs">
            No audit events found for this filter.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 font-semibold uppercase tracking-wider">
                <tr>
                  <th className="py-3 px-4">Action</th>
                  <th className="py-3 px-4">Actor</th>
                  <th className="py-3 px-4">Payment Request</th>
                  <th className="py-3 px-4">Details & Rationale</th>
                  <th className="py-3 px-4">Timestamp</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {logs.map((log) => (
                  <tr key={log.id} className="hover:bg-slate-50/70 transition">
                    <td className="py-3.5 px-4 font-bold text-slate-900 font-mono">
                      {log.action}
                    </td>
                    <td className="py-3.5 px-4">
                      <span className={`px-2 py-0.5 rounded-md font-semibold text-[11px] ${getActorBadge(log.actor_type)}`}>
                        {log.actor_type}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 font-mono text-slate-500">
                      {log.payment_request_id ? log.payment_request_id.slice(0, 8) : '—'}
                    </td>
                    <td className="py-3.5 px-4 text-slate-600 max-w-md">
                      {log.decision_reason || '—'}
                    </td>
                    <td className="py-3.5 px-4 text-slate-400 whitespace-nowrap">
                      {new Date(log.created_at).toLocaleString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
