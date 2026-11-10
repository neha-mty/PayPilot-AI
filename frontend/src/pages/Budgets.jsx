/**
 * Budgets Page.
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
      setBudgets(res.data);
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
    <div className="max-w-5xl mx-auto px-4 py-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-slate-800 flex items-center gap-2">
          <span>💰</span> Budget Manager
        </h1>
        <p className="text-slate-500 text-sm mt-1">
          Configure spending ceilings. The central policy engine will block any AI purchase attempt that would exceed these limits.
        </p>
      </div>

      {message && (
        <div
          className={`mb-6 p-4 rounded-xl text-sm ${
            message.type === 'success'
              ? 'bg-green-50 border border-green-200 text-green-800'
              : 'bg-red-50 border border-red-200 text-red-800'
          }`}
        >
          {message.text}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Left: Active Budgets List */}
        <div className="md:col-span-2 space-y-4">
          <h2 className="text-base font-semibold text-slate-800">Active Budget Limits</h2>

          {loading ? (
            <div className="p-8 text-center text-slate-400">Loading budgets...</div>
          ) : budgets.length === 0 ? (
            <div className="bg-white rounded-2xl border border-slate-200 p-8 text-center text-slate-400">
              <span className="text-3xl block mb-2">📊</span>
              <p className="font-medium text-slate-600">No custom budgets configured yet.</p>
              <p className="text-xs text-slate-400 mt-1">Use the form on the right to set up your first spending limit.</p>
            </div>
          ) : (
            budgets.map((b) => {
              const limitInr = (b.limit_amount_paise / 100).toFixed(2);
              const spentInr = (b.spent_amount_paise / 100).toFixed(2);
              const remainingInr = (b.remaining_paise / 100).toFixed(2);
              const pct = Math.min(100, Math.round((b.spent_amount_paise / b.limit_amount_paise) * 100));

              return (
                <div key={b.id} className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm">
                  <div className="flex items-center justify-between mb-2">
                    <div>
                      <span className="text-xs font-bold uppercase tracking-wider text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded">
                        {b.period}
                      </span>
                      {b.category && (
                        <span className="text-xs text-slate-600 bg-slate-100 px-2 py-0.5 rounded ml-2 font-medium">
                          {b.category}
                        </span>
                      )}
                    </div>
                    <span className="text-sm font-bold text-slate-800">Limit: ₹{limitInr}</span>
                  </div>

                  {/* Progress Bar */}
                  <div className="w-full bg-slate-100 rounded-full h-2.5 my-3 overflow-hidden">
                    <div
                      className={`h-2.5 rounded-full transition-all ${
                        pct > 90 ? 'bg-red-500' : pct > 70 ? 'bg-amber-500' : 'bg-emerald-500'
                      }`}
                      style={{ width: `${pct}%` }}
                    />
                  </div>

                  <div className="flex justify-between text-xs text-slate-500">
                    <span>Spent: ₹{spentInr} ({pct}%)</span>
                    <span className="font-semibold text-slate-700">Remaining: ₹{remainingInr}</span>
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Right: New Budget Form */}
        <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm h-fit">
          <h2 className="text-base font-semibold text-slate-800 mb-4">Set New Spending Limit</h2>

          <form onSubmit={handleCreateBudget} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Period</label>
              <select
                value={period}
                onChange={(e) => setPeriod(e.target.value)}
                className="w-full px-3 py-2 text-sm border border-slate-300 rounded-xl focus:ring-2 focus:ring-indigo-500 outline-none"
              >
                <option value="daily">Daily</option>
                <option value="weekly">Weekly</option>
                <option value="monthly">Monthly</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Category <span className="text-slate-400 font-normal">(optional)</span>
              </label>
              <input
                type="text"
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                placeholder="e.g. Food, Electronics, Shopping"
                className="w-full px-3 py-2 text-sm border border-slate-300 rounded-xl focus:ring-2 focus:ring-indigo-500 outline-none"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Limit (₹ INR)</label>
              <div className="relative">
                <span className="absolute left-3 top-2 text-slate-400 text-sm font-semibold">₹</span>
                <input
                  type="number"
                  step="1"
                  min="1"
                  value={limitInr}
                  onChange={(e) => setLimitInr(e.target.value)}
                  className="w-full pl-7 pr-3 py-2 text-sm border border-slate-300 rounded-xl focus:ring-2 focus:ring-indigo-500 outline-none font-semibold text-slate-800"
                  required
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={submitting}
              className="w-full py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold rounded-xl text-xs transition border-none shadow-sm cursor-pointer disabled:opacity-50"
            >
              {submitting ? 'Saving...' : 'Add Spending Limit'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
