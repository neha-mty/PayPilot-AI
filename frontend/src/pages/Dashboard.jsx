/**
 * Main dashboard page with Blue, Grey, and Orange design system.
 * Shows budget summary, pending approvals, recent transactions, and quick discovery shortcut.
 */
import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { dashboardAPI } from '../services/api';

export default function Dashboard() {
  const { user } = useAuth();
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      const response = await dashboardAPI.summary();
      setSummary(response.data);
    } catch (err) {
      setError('Failed to load dashboard data.');
    } finally {
      setLoading(false);
    }
  };

  const formatINR = (paise) => {
    if (paise == null) return '₹0.00';
    return `₹${(paise / 100).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-4 border-blue-600 border-t-transparent"></div>
      </div>
    );
  }

  const pendingApprovalsCount = summary?.pending_approvals || 0;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 animate-fade-in">
      {/* Welcome Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between pb-6 border-b border-slate-200 gap-4 mb-8">
        <div>
          <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-blue-50 border border-blue-200 text-blue-700 text-xs font-semibold mb-2">
            <span>🛡️ PayPilot AI Autonomous Governance</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
            Welcome back, {user?.name || 'Explorer'}! 👋
          </h1>
          <p className="text-slate-600 text-sm mt-1">
            Real-time policy limits, active multi-provider marketplace discovery, and pending signatures.
          </p>
        </div>
        <Link
          to="/chat"
          className="self-start sm:self-auto px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs rounded-xl shadow-sm transition no-underline flex items-center gap-2"
        >
          <span>🔍 Explore Universal Marketplace</span>
        </Link>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl text-red-700 text-sm">
          {error}
        </div>
      )}

      {/* Key Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {/* Total Budget */}
        <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Total Budget</span>
            <span className="w-7 h-7 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center text-sm font-bold">💰</span>
          </div>
          <p className="text-2xl font-black text-slate-900 mt-2">
            {formatINR(summary?.total_budget_paise)}
          </p>
          <span className="text-[11px] text-slate-400 mt-1 block">Active user allocation</span>
        </div>

        {/* Amount Spent */}
        <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Amount Spent</span>
            <span className="w-7 h-7 rounded-lg bg-slate-100 text-slate-700 flex items-center justify-center text-sm font-bold">📉</span>
          </div>
          <p className="text-2xl font-black text-slate-900 mt-2">
            {formatINR(summary?.total_spent_paise)}
          </p>
          <span className="text-[11px] text-slate-400 mt-1 block">Executed transactions</span>
        </div>

        {/* Remaining Balance */}
        <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Remaining</span>
            <span className="w-7 h-7 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center text-sm font-bold">✅</span>
          </div>
          <p className="text-2xl font-black text-emerald-600 mt-2">
            {formatINR(summary?.remaining_budget_paise)}
          </p>
          <span className="text-[11px] text-emerald-600/80 font-medium mt-1 block">Available within policies</span>
        </div>

        {/* Pending Approvals (Orange Highlight) */}
        <div className={`rounded-2xl border p-5 shadow-xs transition ${
          pendingApprovalsCount > 0 ? 'bg-orange-50/50 border-orange-200' : 'bg-white border-slate-200'
        }`}>
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Pending Approvals</span>
            <span className="w-7 h-7 rounded-lg bg-orange-100 text-orange-600 flex items-center justify-center text-sm font-bold">⏳</span>
          </div>
          <div className="flex items-baseline justify-between mt-2">
            <p className="text-2xl font-black text-orange-600">
              {pendingApprovalsCount}
            </p>
            {pendingApprovalsCount > 0 && (
              <Link
                to="/approvals"
                className="text-xs font-bold text-orange-700 bg-orange-100 hover:bg-orange-200 px-2.5 py-1 rounded-lg transition no-underline"
              >
                Sign Now →
              </Link>
            )}
          </div>
          <span className="text-[11px] text-slate-400 mt-1 block">
            {pendingApprovalsCount > 0 ? 'Requires your authorization' : 'No action needed'}
          </span>
        </div>
      </div>

      {/* Universal Discovery Banner */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-700 rounded-3xl p-6 sm:p-8 text-white shadow-md mb-8 flex flex-col md:flex-row items-center justify-between gap-6">
        <div>
          <span className="bg-white/20 text-white font-bold text-[11px] uppercase tracking-wider px-3 py-1 rounded-full">
            Supported Providers: Lenskart • Croma • Pepperfry • Tanishq • MakeMyTrip • Amazon
          </span>
          <h2 className="text-xl sm:text-2xl font-black mt-3">
            Search Any Category Across 7+ Major Marketplaces
          </h2>
          <p className="text-blue-100 text-xs sm:text-sm mt-1 max-w-xl">
            Ask for sunglasses, ergonomic chairs, gold earrings, laptops, flights from Kolkata to Delhi, or telescopes. The AI identifies the category, retrieves verified options, and enforces deterministic budget policies.
          </p>
        </div>
        <Link
          to="/chat"
          className="px-6 py-3 bg-white text-blue-700 hover:bg-blue-50 font-bold text-sm rounded-xl shadow-md transition no-underline whitespace-nowrap cursor-pointer"
        >
          Start Searching →
        </Link>
      </div>

      {/* Recent Transactions Table */}
      <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-xs">
        <div className="p-5 border-b border-slate-100 flex items-center justify-between">
          <div>
            <h3 className="font-bold text-slate-900 text-base">Recent Transactions</h3>
            <p className="text-xs text-slate-500 mt-0.5">Authoritative audit ledger of approved payments</p>
          </div>
          <Link
            to="/transactions"
            className="text-xs font-semibold text-blue-600 hover:text-blue-700 no-underline"
          >
            View All →
          </Link>
        </div>

        {summary?.recent_transactions?.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-50 text-slate-500 text-xs uppercase font-semibold">
                <tr>
                  <th className="py-3 px-4">Transaction ID</th>
                  <th className="py-3 px-4">Merchant / Provider</th>
                  <th className="py-3 px-4">Amount</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4">Date</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {summary.recent_transactions.map((tx) => (
                  <tr key={tx.id} className="hover:bg-slate-50/70 transition">
                    <td className="py-3 px-4 font-mono text-xs text-slate-500">
                      {tx.id.slice(0, 8)}
                    </td>
                    <td className="py-3 px-4 font-medium text-slate-800">
                      {tx.merchant_name || 'Verified Merchant'}
                    </td>
                    <td className="py-3 px-4 font-bold text-slate-900">
                      {formatINR(tx.amount_paise)}
                    </td>
                    <td className="py-3 px-4">
                      <span className="px-2 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800">
                        {tx.status}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-xs text-slate-400">
                      {new Date(tx.created_at).toLocaleDateString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="p-8 text-center text-slate-400 text-xs">
            No transactions yet. Complete your first purchase via Universal Marketplace!
          </div>
        )}
      </div>
    </div>
  );
}
