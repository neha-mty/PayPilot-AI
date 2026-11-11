/**
 * Policy Settings Page with Blue, Grey, and Orange design system.
 * Configure deterministic spending policy rules enforced by the backend engine.
 */
import { useState, useEffect } from 'react';
import { policyAPI } from '../services/api';

export default function Policies() {
  const [maxTxInr, setMaxTxInr] = useState('500');
  const [approvalRequired, setApprovalRequired] = useState(true);
  const [unknownMerchantAction, setUnknownMerchantAction] = useState('require_approval');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState(null);

  useEffect(() => {
    loadPolicy();
  }, []);

  const loadPolicy = async () => {
    try {
      const res = await policyAPI.get();
      const p = res.data;
      setMaxTxInr((p.max_transaction_paise / 100).toString());
      setApprovalRequired(p.approval_required);
      setUnknownMerchantAction(p.unknown_merchant_action);
    } catch (err) {
      setMessage({ type: 'error', text: 'Failed to load policy settings.' });
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    setMessage(null);

    const amount = parseFloat(maxTxInr);
    if (isNaN(amount) || amount <= 0) {
      setMessage({ type: 'error', text: 'Please enter a valid max transaction amount.' });
      setSaving(false);
      return;
    }

    try {
      await policyAPI.update({
        max_transaction_paise: Math.round(amount * 100),
        approval_required: approvalRequired,
        unknown_merchant_action: unknownMerchantAction,
      });
      setMessage({ type: 'success', text: '✅ Security policies updated and active!' });
    } catch (err) {
      setMessage({ type: 'error', text: err.response?.data?.detail || 'Failed to update policies.' });
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-4 border-blue-600 border-t-transparent"></div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 animate-fade-in">
      <div className="pb-6 border-b border-slate-200 mb-8">
        <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-blue-50 border border-blue-200 text-blue-700 text-xs font-semibold mb-2">
          <span>🛡️ Deterministic Backend Rules</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
          Spending Policies & Security Guardrails
        </h1>
        <p className="text-slate-600 text-sm mt-1">
          Configure exact conditions under which AI purchases are Allowed, Require Approval, or are Blocked.
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

      <form onSubmit={handleSave} className="space-y-6">
        {/* Max Single Transaction */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs">
          <label className="block text-sm font-bold text-slate-900 mb-1">
            Max Single Transaction (₹)
          </label>
          <p className="text-xs text-slate-500 mb-3">
            Transactions exceeding this threshold are immediately <strong className="text-red-600">BLOCKED</strong> by the policy engine.
          </p>
          <div className="flex items-center max-w-xs bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 focus-within:ring-2 focus-within:ring-blue-500">
            <span className="text-sm text-slate-400 mr-2">₹</span>
            <input
              type="number"
              value={maxTxInr}
              onChange={(e) => setMaxTxInr(e.target.value)}
              className="w-full bg-transparent text-sm font-bold text-slate-900 focus:outline-none"
              step="1"
              min="1"
              required
            />
          </div>
        </div>

        {/* Universal Approval Requirement */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs flex items-center justify-between gap-4">
          <div>
            <h3 className="text-sm font-bold text-slate-900">Always Require User Approval</h3>
            <p className="text-xs text-slate-500 mt-0.5">
              When enabled, all AI purchases must be manually signed off on the Approvals screen before payment processing.
            </p>
          </div>
          <button
            type="button"
            onClick={() => setApprovalRequired(!approvalRequired)}
            className={`w-14 h-8 rounded-full p-1 transition-colors cursor-pointer border-none ${
              approvalRequired ? 'bg-blue-600' : 'bg-slate-300'
            }`}
          >
            <div
              className={`w-6 h-6 rounded-full bg-white transition-transform ${
                approvalRequired ? 'translate-x-6' : 'translate-x-0'
              }`}
            />
          </button>
        </div>

        {/* Unverified Merchant Action */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs">
          <label className="block text-sm font-bold text-slate-900 mb-1">
            Unverified Merchant Policy
          </label>
          <p className="text-xs text-slate-500 mb-3">
            How should PayPilot handle purchase requests from newly discovered or unverified merchants?
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <label
              className={`p-4 rounded-xl border-2 flex items-center gap-3 cursor-pointer transition ${
                unknownMerchantAction === 'require_approval'
                  ? 'border-blue-600 bg-blue-50/50 text-blue-900 font-semibold'
                  : 'border-slate-200 bg-white text-slate-700 hover:bg-slate-50'
              }`}
            >
              <input
                type="radio"
                name="unknown_action"
                value="require_approval"
                checked={unknownMerchantAction === 'require_approval'}
                onChange={() => setUnknownMerchantAction('require_approval')}
                className="hidden"
              />
              <span className="text-xl">⏳</span>
              <div>
                <p className="text-xs font-bold">Require Approval</p>
                <p className="text-[11px] text-slate-500">Allow user to inspect & authorize manually.</p>
              </div>
            </label>

            <label
              className={`p-4 rounded-xl border-2 flex items-center gap-3 cursor-pointer transition ${
                unknownMerchantAction === 'block'
                  ? 'border-red-600 bg-red-50/50 text-red-900 font-semibold'
                  : 'border-slate-200 bg-white text-slate-700 hover:bg-slate-50'
              }`}
            >
              <input
                type="radio"
                name="unknown_action"
                value="block"
                checked={unknownMerchantAction === 'block'}
                onChange={() => setUnknownMerchantAction('block')}
                className="hidden"
              />
              <span className="text-xl">⛔</span>
              <div>
                <p className="text-xs font-bold">Block Completely</p>
                <p className="text-[11px] text-slate-500">Strictly forbid transactions with unverified sellers.</p>
              </div>
            </label>
          </div>
        </div>

        <div className="pt-2">
          <button
            type="submit"
            disabled={saving}
            className="w-full sm:w-auto px-8 py-3 bg-blue-600 hover:bg-blue-700 text-white font-bold text-sm rounded-xl shadow-sm transition cursor-pointer disabled:opacity-50"
          >
            {saving ? 'Saving Policies...' : 'Save & Enforce Policies'}
          </button>
        </div>
      </form>
    </div>
  );
}
