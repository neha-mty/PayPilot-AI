/**
 * Budgets Page with Blue, Grey, and Orange design system.
 * Manage spending limits across daily, weekly, monthly periods, and specific categories.
 */
import { useState, useEffect } from 'react';
import { budgetAPI } from '../services/api';

export default function Budgets() {
  const [budgets, setBudgets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState(null);

  // Form fields
  const [period, setPeriod] = useState('daily');
  const [category, setCategory] = useState('');
  const [limitInr, setLimitInr] = useState('500');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    loadBudgets();
  }, []);

  const loadBudgets = async () => {
    try {
      const res = await budgetAPI.list();
      setBudgets(res.data || []);
    } catch (err) {
      setMessage({ type: 'error', text: 'Failed to load budgets.' });
    } finally {
      setLoading(false);
    }
  };

  const handleCreateBudget = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setMessage(null);

    const amountInr = parseFloat(limitInr);
    if (isNaN(amountInr) || amountInr <= 0) {
      setMessage({ type: 'error', text: 'Please enter a valid positive budget amount.' });
      setSubmitting(false);
      return;
    }

    try {
      await budgetAPI.create({
        period,
        category: category.trim() || null,
        limit_amount_paise: Math.round(amountInr * 100),
      });
      setMessage({ type: 'success', text: `New ${period} budget of ₹${amountInr.toFixed(2)} created!` });
      setCategory('');
      await loadBudgets();
    } catch (err) {
      setMessage({ type: 'error', text: err.response?.data?.detail || 'Failed to create budget.' });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 animate-fade-in">
      <div className="pb-6 border-b border-slate-200 mb-8">
        <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-blue-50 border border-blue-200 text-blue-700 text-xs font-semibold mb-2">
          <span>💰 Dynamic Budget Guardrails</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
          Budgets & Spending Limits
        </h1>
        <p className="text-slate-600 text-sm mt-1">
          Define periodic and category-specific budget caps enforced deterministically by the policy engine.
        </p>
      </div>

      {message && (
        <div
          className={`mb-6 p-4 rounded-xl border text-sm flex items-center justify-between ${
            message.type === 'success'
              ? 'bg-emerald-50 border-emerald-300 text-emerald-900'
              : 'bg-red-50 border-red-300 text-red-900'
          }`}
        >
          <span>{message.text}</span>
          <button onClick={() => setMessage(null)} className="text-xs text-slate-400 hover:text-slate-600 border-none bg-transparent cursor-pointer">✕</button>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Create Budget Form */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs h-fit">
          <h2 className="text-base font-bold text-slate-900 mb-4">Set New Spending Limit</h2>
          <form onSubmit={handleCreateBudget} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Time Period</label>
              <select
                value={period}
                onChange={(e) => setPeriod(e.target.value)}
                className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-xs font-medium text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="daily">Daily</option>
                <option value="weekly">Weekly</option>
                <option value="monthly">Monthly</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Category (Optional)</label>
              <input
                type="text"
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                placeholder="e.g. Food, Electronics, Jewellery..."
                className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-xs text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <span className="text-[10px] text-slate-400 mt-1 block">Leave empty to apply universally.</span>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Limit (₹)</label>
              <div className="flex items-center bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 focus-within:ring-2 focus-within:ring-blue-500">
                <span className="text-xs text-slate-400 mr-2">₹</span>
                <input
                  type="number"
                  value={limitInr}
                  onChange={(e) => setLimitInr(e.target.value)}
                  step="10"
                  min="1"
                  required
                  className="w-full bg-transparent text-xs font-bold text-slate-900 focus:outline-none"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={submitting}
              className="w-full py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs rounded-xl shadow-xs transition cursor-pointer disabled:opacity-50"
            >
              {submitting ? 'Creating...' : 'Activate Budget Limit'}
            </button>
          </form>
        </div>

        {/* Active Budgets List */}
        <div className="lg:col-span-2 space-y-4">
          <h2 className="text-base font-bold text-slate-900 mb-2">Active Budget Enforcements</h2>
          {loading ? (
            <div className="text-slate-400 text-xs py-8 text-center">Loading active budgets...</div>
          ) : budgets.length === 0 ? (
            <div className="bg-white border border-slate-200 rounded-2xl p-8 text-center text-slate-400 text-xs shadow-xs">
              No budgets configured yet. Create your first budget limit on the left.
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {budgets.map((b) => (
                <div key={b.id} className="bg-white border border-slate-200 rounded-2xl p-5 shadow-xs flex flex-col justify-between">
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="px-2.5 py-0.5 text-xs font-bold bg-blue-50 text-blue-700 rounded-md uppercase">
                        {b.period}
                      </span>
                      <span className="text-xs text-slate-400 font-medium">
                        {b.category || 'All Categories'}
                      </span>
                    </div>
                    <div className="mt-3">
                      <span className="text-xs text-slate-400 block font-medium">Cap Limit:</span>
                      <span className="text-2xl font-black text-slate-900">
                        ₹{(b.limit_amount_paise / 100).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                      </span>
                    </div>
                  </div>
                  <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-500">
                    <span className="flex items-center gap-1">
                      <span className="w-2 h-2 rounded-full bg-emerald-500"></span> Active Policy Guard
                    </span>
                    <span>Reset: Next {b.period}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
