/**
 * Main dashboard page.
 * Shows budget summary, pending approvals, recent transactions.
 * All data comes from the backend — no fake metrics.
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

  // Format paise to INR display string
  const formatINR = (paise) => {
    if (paise == null) return '₹0.00';
    return `₹${(paise / 100).toFixed(2)}`;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-6">
      {/* Welcome Section */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-slate-800">Welcome back, {user?.name || 'User'}! 👋</h1>
        <p className="text-slate-500 mt-1">Here's your spending overview</p>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
          {error}
        </div>
      )}

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-5">
          <p className="text-sm text-slate-500">Total Budget</p>
          <p className="text-2xl font-bold text-slate-800 mt-1">
            {formatINR(summary?.total_budget_paise)}
          </p>
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-5">
          <p className="text-sm text-slate-500">Amount Spent</p>
          <p className="text-2xl font-bold text-orange-600 mt-1">
            {formatINR(summary?.total_spent_paise)}
          </p>
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-5">
          <p className="text-sm text-slate-500">Remaining</p>
          <p className="text-2xl font-bold text-green-600 mt-1">
            {formatINR(summary?.remaining_paise)}
          </p>
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-5">
          <p className="text-sm text-slate-500">Pending Approvals</p>
          <p className="text-2xl font-bold text-indigo-600 mt-1">
            {summary?.pending_approvals || 0}
          </p>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <Link
          to="/chat"
          className="flex items-center gap-4 bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded-xl p-6 shadow-md hover:shadow-lg transition no-underline"
        >
          <span className="text-3xl">🤖</span>
          <div>
            <h3 className="text-lg font-semibold">AI Purchasing Assistant</h3>
            <p className="text-indigo-100 text-sm">Tell me what you need — I'll find the best options</p>
          </div>
        </Link>
        <Link
          to="/approvals"
          className="flex items-center gap-4 bg-white border border-slate-200 rounded-xl p-6 shadow-sm hover:shadow-md transition no-underline text-slate-800"
        >
          <span className="text-3xl">✅</span>
          <div>
            <h3 className="text-lg font-semibold">Payment Approvals</h3>
            <p className="text-slate-500 text-sm">
              {summary?.pending_approvals
                ? `${summary.pending_approvals} pending approval(s)`
                : 'No pending approvals'}
            </p>
          </div>
        </Link>
      </div>

      {/* Recent Transactions */}
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-slate-800">Recent Transactions</h2>
          <Link to="/transactions" className="text-sm text-indigo-600 hover:text-indigo-700 font-medium">
            View all →
          </Link>
        </div>
        {summary?.recent_transactions?.length > 0 ? (
          <div className="divide-y divide-slate-100">
            {summary.recent_transactions.map((tx) => (
              <div key={tx.id} className="py-3 flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-slate-800">{tx.description || 'Transaction'}</p>
                  <p className="text-xs text-slate-500">{new Date(tx.created_at).toLocaleDateString()}</p>
                </div>
                <div className="text-right">
                  <p className="text-sm font-semibold text-slate-800">{formatINR(tx.amount_paise)}</p>
                  <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                    tx.status === 'successful' ? 'bg-green-100 text-green-700' :
                    tx.status === 'failed' ? 'bg-red-100 text-red-700' :
                    tx.status === 'pending' ? 'bg-yellow-100 text-yellow-700' :
                    'bg-slate-100 text-slate-600'
                  }`}>
                    {tx.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-slate-400">
            <p className="text-3xl mb-2">📭</p>
            <p>No transactions yet. Start by using the AI Assistant!</p>
          </div>
        )}
      </div>
    </div>
  );
}
