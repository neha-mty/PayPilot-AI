/**
 * Policy Settings Page.
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
        is_active: true,
      });
      setMessage({ type: 'success', text: 'Security policy settings updated successfully!' });
    } catch (err) {
      setMessage({ type: 'error', text: err.response?.data?.detail || 'Failed to update policy.' });
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-slate-800 flex items-center gap-2">
          <span>🛡️</span> Central Spending-Policy Settings
        </h1>
        <p className="text-slate-500 text-sm mt-1">
          These deterministic rules are executed strictly by the backend engine before any payment can be prepared or dispatched.
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

      {loading ? (
        <div className="p-8 text-center text-slate-400">Loading policy rules...</div>
      ) : (
        <form onSubmit={handleSave} className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm space-y-6">
          {/* Max Transaction Amount */}
          <div className="border-b border-slate-100 pb-5">
            <label className="block text-sm font-bold text-slate-800 mb-1">
              Maximum Single Transaction Amount
            </label>
            <p className="text-xs text-slate-500 mb-3">
              Any AI purchase request exceeding this ceiling will trigger an immediate <code>BLOCK</code> decision.
            </p>
            <div className="relative max-w-xs">
              <span className="absolute left-3 top-2.5 text-slate-400 text-sm font-semibold">₹</span>
              <input
                type="number"
                step="1"
                min="1"
                value={maxTxInr}
                onChange={(e) => setMaxTxInr(e.target.value)}
                className="w-full pl-7 pr-3 py-2 text-sm border border-slate-300 rounded-xl focus:ring-2 focus:ring-indigo-500 outline-none font-bold text-slate-800"
                required
              />
            </div>
          </div>

          {/* User Approval Requirement */}
          <div className="border-b border-slate-100 pb-5 flex items-start justify-between">
            <div>
              <label className="block text-sm font-bold text-slate-800 mb-1">
                Mandatory User Approval Workflow
              </label>
              <p className="text-xs text-slate-500">
                When enabled, every payment request requires your manual consent on the Approvals screen before payment orders can be created.
              </p>
            </div>
            <input
              type="checkbox"
              checked={approvalRequired}
              onChange={(e) => setApprovalRequired(e.target.checked)}
              className="w-5 h-5 accent-indigo-600 rounded cursor-pointer mt-1"
            />
          </div>

          {/* Unknown / Unverified Merchant Action */}
          <div className="border-b border-slate-100 pb-5">
            <label className="block text-sm font-bold text-slate-800 mb-1">
              Unknown / Unverified Merchant Action
            </label>
            <p className="text-xs text-slate-500 mb-3">
              How the policy engine responds when an AI selects a merchant that does not possess verified status (e.g., Urban Store).
            </p>
            <div className="space-y-2 max-w-md">
              <label className="flex items-center gap-3 p-3 border border-slate-200 rounded-xl cursor-pointer hover:bg-slate-50">
                <input
                  type="radio"
                  name="unknown_action"
                  value="require_approval"
                  checked={unknownMerchantAction === 'require_approval'}
                  onChange={(e) => setUnknownMerchantAction(e.target.value)}
                  className="accent-indigo-600"
                />
                <div>
                  <span className="text-xs font-bold text-slate-800 block">Require Explicit Approval (Recommended)</span>
                  <span className="text-[11px] text-slate-500">Flag for manual user inspection before proceeding.</span>
                </div>
              </label>

              <label className="flex items-center gap-3 p-3 border border-slate-200 rounded-xl cursor-pointer hover:bg-slate-50">
                <input
                  type="radio"
                  name="unknown_action"
                  value="block"
                  checked={unknownMerchantAction === 'block'}
                  onChange={(e) => setUnknownMerchantAction(e.target.value)}
                  className="accent-indigo-600"
                />
                <div>
                  <span className="text-xs font-bold text-slate-800 block">Strict Block</span>
                  <span className="text-[11px] text-slate-500">Automatically reject any unverified merchant attempts.</span>
                </div>
              </label>

              <label className="flex items-center gap-3 p-3 border border-slate-200 rounded-xl cursor-pointer hover:bg-slate-50">
                <input
                  type="radio"
                  name="unknown_action"
                  value="allow"
                  checked={unknownMerchantAction === 'allow'}
                  onChange={(e) => setUnknownMerchantAction(e.target.value)}
                  className="accent-indigo-600"
                />
                <div>
                  <span className="text-xs font-bold text-slate-800 block">Allow Unverified</span>
                  <span className="text-[11px] text-slate-500">Permit without merchant verification check.</span>
                </div>
              </label>
            </div>
          </div>

          <div className="flex justify-end pt-2">
            <button
              type="submit"
              disabled={saving}
              className="px-6 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold rounded-xl text-xs transition border-none shadow-sm cursor-pointer disabled:opacity-50"
            >
              {saving ? 'Updating...' : 'Save Policy Settings'}
            </button>
          </div>
        </form>
      )}
    </div>
  );
}
