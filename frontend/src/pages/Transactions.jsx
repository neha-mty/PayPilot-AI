/**
 * Transactions Page.
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
      setTransactions(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto px-4 py-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-slate-800 flex items-center gap-2">
          <span>📋</span> Transaction History
        </h1>
        <p className="text-slate-500 text-sm mt-1">
          Immutable payment records confirmed via cryptographic webhook verification from the payment gateway.
        </p>
      </div>

      <div className="bg-white border border-slate-200 rounded-2xl shadow-sm overflow-hidden">
        {loading ? (
          <div className="p-8 text-center text-slate-400">Loading transactions...</div>
        ) : transactions.length === 0 ? (
          <div className="p-8 text-center text-slate-400">
            <span className="text-3xl block mb-2">📭</span>
            <p className="font-medium text-slate-600">No transactions recorded yet.</p>
            <p className="text-xs text-slate-400 mt-1">Completed purchases from the AI assistant will show up here.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 font-semibold uppercase tracking-wider">
                <tr>
                  <th className="py-3 px-4">Date</th>
                  <th className="py-3 px-4">Description</th>
                  <th className="py-3 px-4">Provider / Order ID</th>
                  <th className="py-3 px-4">Payment ID</th>
                  <th className="py-3 px-4 text-right">Amount</th>
                  <th className="py-3 px-4 text-center">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {transactions.map((t) => (
                  <tr key={t.id} className="hover:bg-slate-50/70 transition">
                    <td className="py-3 px-4 text-slate-500 whitespace-nowrap">
                      {new Date(t.created_at).toLocaleString()}
                    </td>
                    <td className="py-3 px-4 font-semibold text-slate-800">
                      {t.description || 'Order Purchase'}
                    </td>
                    <td className="py-3 px-4 font-mono text-slate-600">
                      <span className="text-[11px] text-indigo-600 bg-indigo-50 px-1.5 py-0.5 rounded mr-1">
                        {t.provider}
                      </span>
                      {t.provider_order_id ? `#${t.provider_order_id.slice(0, 16)}` : '—'}
                    </td>
                    <td className="py-3 px-4 font-mono text-slate-500">
                      {t.provider_payment_id || '—'}
                    </td>
                    <td className="py-3 px-4 text-right font-bold text-slate-900 whitespace-nowrap">
                      ₹{(t.amount_paise / 100).toFixed(2)}
                    </td>
                    <td className="py-3 px-4 text-center">
                      <span
                        className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase ${
                          t.status === 'successful'
                            ? 'bg-emerald-100 text-emerald-800'
                            : t.status === 'failed'
                            ? 'bg-red-100 text-red-800'
                            : 'bg-amber-100 text-amber-800'
                        }`}
                      >
                        {t.status}
                      </span>
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
