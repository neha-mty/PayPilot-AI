/**
 * Transactions Page with Blue, Grey, and Orange design system.
 * Displays completed, pending, and failed payment records confirmed by the payment gateway.
 */
import { useState, useEffect } from 'react';
import { transactionAPI } from '../services/api';

export default function Transactions() {
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadTransactions();
  }, []);

  const loadTransactions = async () => {
    try {
      const res = await transactionAPI.list();
      setTransactions(res.data || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 animate-fade-in">
      <div className="pb-6 border-b border-slate-200 mb-8">
        <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-blue-50 border border-blue-200 text-blue-700 text-xs font-semibold mb-2">
          <span>📋 Payment Gateway Ledger</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
          Transaction History
        </h1>
        <p className="text-slate-600 text-sm mt-1">
          Cryptographically confirmed payment records verified via backend webhook authentication.
        </p>
      </div>

      <div className="bg-white border border-slate-200 rounded-2xl shadow-xs overflow-hidden">
        {loading ? (
          <div className="p-8 text-center text-slate-400 text-xs">Loading transaction records...</div>
        ) : transactions.length === 0 ? (
          <div className="p-12 text-center text-slate-400">
            <span className="text-3xl block mb-2">📭</span>
            <p className="font-semibold text-slate-700 text-sm">No transactions recorded yet.</p>
            <p className="text-xs text-slate-400 mt-1">Authorized purchases processed via sandbox will appear here.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 font-semibold uppercase tracking-wider">
                <tr>
                  <th className="py-3 px-4">Transaction ID</th>
                  <th className="py-3 px-4">Gateway Order ID</th>
                  <th className="py-3 px-4">Merchant / Partner</th>
                  <th className="py-3 px-4">Amount</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4">Timestamp</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {transactions.map((tx) => (
                  <tr key={tx.id} className="hover:bg-slate-50/70 transition">
                    <td className="py-3.5 px-4 font-mono text-slate-600">{tx.id.slice(0, 10)}...</td>
                    <td className="py-3.5 px-4 font-mono text-slate-500">{tx.gateway_order_id || 'sim_order'}</td>
                    <td className="py-3.5 px-4 font-semibold text-slate-800">{tx.merchant_name || 'Verified Partner'}</td>
                    <td className="py-3.5 px-4 font-extrabold text-slate-900">
                      ₹{(tx.amount_paise / 100).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                    </td>
                    <td className="py-3.5 px-4">
                      <span className="px-2 py-0.5 rounded-full font-bold bg-emerald-100 text-emerald-800">
                        {tx.status}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-slate-400">
                      {new Date(tx.created_at).toLocaleString()}
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
