/**
 * Approvals Page.
 * Central payment authorization screen. Shows all pending payment requests,
 * exact amount, product, merchant verification status, and policy evaluation reasons.
 * Enables user to Approve, Reject, and proceed to sandbox payment completion.
 */
import { useState, useEffect } from 'react';
import { paymentRequestAPI, paymentAPI, api } from '../services/api';

export default function Approvals() {
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(null);
  const [message, setMessage] = useState(null);
  const [checkoutModal, setCheckoutModal] = useState(null);

  useEffect(() => {
    loadRequests();
  }, []);

  const loadRequests = async () => {
    try {
      const res = await paymentRequestAPI.list();
      setRequests(res.data);
    } catch (err) {
      setMessage({ type: 'error', text: 'Failed to load payment requests.' });
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (requestId) => {
    setActionLoading(requestId);
    setMessage(null);
    try {
      await paymentRequestAPI.approve(requestId);
      setMessage({ type: 'success', text: `Payment request #${requestId.slice(0, 8)} approved!` });
      await loadRequests();
    } catch (err) {
      setMessage({ type: 'error', text: err.response?.data?.detail || 'Approval failed.' });
    } finally {
      setActionLoading(null);
    }
  };

  const handleReject = async (requestId) => {
    setActionLoading(requestId);
    setMessage(null);
    try {
      await paymentRequestAPI.reject(requestId);
      setMessage({ type: 'info', text: `Payment request #${requestId.slice(0, 8)} rejected.` });
      await loadRequests();
    } catch (err) {
      setMessage({ type: 'error', text: err.response?.data?.detail || 'Rejection failed.' });
    } finally {
      setActionLoading(null);
    }
  };

  const handleProceedToPayment = async (request) => {
    setActionLoading(request.id);
    setMessage(null);
    try {
      const res = await paymentAPI.create(request.id);
      const order = res.data;
      setCheckoutModal({
        orderId: order.order_id,
        amountInr: (request.amount_paise / 100).toFixed(2),
        productName: request.product?.name || 'Order',
        providerLabel: order.provider_label || 'Simulated Gateway',
        requestId: request.id,
      });
    } catch (err) {
      setMessage({ type: 'error', text: err.response?.data?.detail || 'Failed to initialize payment gateway order.' });
    } finally {
      setActionLoading(null);
    }
  };

  const handleCompleteSimulatedPayment = async (orderId, outcome) => {
    try {
      // Call backend simulated complete endpoint (which runs full HMAC webhook verification!)
      const res = await api.post(`/payments/simulated-complete?order_id=${orderId}&outcome=${outcome}`);
      setCheckoutModal(null);
      setMessage({
        type: outcome === 'success' ? 'success' : 'error',
        text: outcome === 'success'
          ? `🎉 Test payment confirmed via verified HMAC webhook for order ${orderId.slice(0, 14)}!`
          : `❌ Test payment marked as failed for order ${orderId.slice(0, 14)}.`,
      });
      await loadRequests();
    } catch (err) {
      setMessage({ type: 'error', text: 'Webhook verification or completion failed.' });
    }
  };

  const pendingRequests = requests.filter(
    (r) => r.status === 'policy_evaluated' || r.status === 'approved'
  );
  const historyRequests = requests.filter(
    (r) => r.status !== 'policy_evaluated' && r.status !== 'approved'
  );

  return (
    <div className="max-w-5xl mx-auto px-4 py-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-slate-800 flex items-center gap-2">
          <span>✅</span> Payment Authorization & Approvals
        </h1>
        <p className="text-slate-500 text-sm mt-1">
          Review purchase requests prepared by AI agents. Every approval applies strictly to that specific merchant and exact amount.
        </p>
      </div>

      {message && (
        <div
          className={`mb-6 p-4 rounded-xl text-sm ${
            message.type === 'success'
              ? 'bg-green-50 border border-green-200 text-green-800'
              : message.type === 'error'
              ? 'bg-red-50 border border-red-200 text-red-800'
              : 'bg-slate-100 border border-slate-200 text-slate-800'
          }`}
        >
          {message.text}
        </div>
      )}

      {/* Pending Section */}
      <div className="mb-8">
        <h2 className="text-lg font-semibold text-slate-800 mb-3 flex items-center gap-2">
          <span>⏳</span> Pending Action ({pendingRequests.length})
        </h2>

        {loading ? (
          <div className="p-8 text-center text-slate-400">Loading requests...</div>
        ) : pendingRequests.length === 0 ? (
          <div className="bg-white rounded-2xl border border-slate-200 p-8 text-center text-slate-400">
            <span className="text-3xl block mb-2">🎉</span>
            <p className="font-medium text-slate-600">All caught up! No pending payment authorizations.</p>
            <p className="text-xs text-slate-400 mt-1">
              Ask the AI Assistant to find products, and any approval-requiring purchases will appear here.
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {pendingRequests.map((req) => (
              <div
                key={req.id}
                className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm hover:shadow-md transition"
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-3 border-b border-slate-100 gap-2">
                  <div>
                    <span className="text-xs font-mono text-slate-400">ID: #{req.id.slice(0, 8)}</span>
                    <h3 className="text-base font-bold text-slate-900 mt-0.5">
                      {req.product?.name || req.description}
                    </h3>
                    <p className="text-xs text-slate-500">
                      Merchant: <strong className="text-slate-700">{req.merchant?.name || 'Catalog Merchant'}</strong>{' '}
                      {req.merchant?.is_verified ? (
                        <span className="text-green-600 bg-green-50 px-1.5 py-0.5 rounded text-[11px] font-medium ml-1">
                          ✓ Verified
                        </span>
                      ) : (
                        <span className="text-amber-600 bg-amber-50 px-1.5 py-0.5 rounded text-[11px] font-medium ml-1">
                          ⚠️ Unverified
                        </span>
                      )}
                    </p>
                  </div>

                  <div className="text-right">
                    <span className="text-2xl font-black text-indigo-700">
                      ₹{(req.amount_paise / 100).toFixed(2)}
                    </span>
                    <span className="block text-[11px] text-slate-400 font-mono">
                      {req.currency} ({req.amount_paise} paise)
                    </span>
                  </div>
                </div>

                {/* Policy Decision Summary */}
                <div className="py-3 text-xs bg-slate-50 rounded-xl px-3 my-3 border border-slate-100">
                  <div className="flex items-center gap-2 mb-1">
                    <strong className="text-slate-600">Policy Engine Decision:</strong>
                    <span
                      className={`px-2 py-0.5 rounded-full font-bold uppercase text-[10px] ${
                        req.policy_decision === 'ALLOW'
                          ? 'bg-green-100 text-green-800'
                          : req.policy_decision === 'REQUIRE_APPROVAL'
                          ? 'bg-amber-100 text-amber-800'
                          : 'bg-red-100 text-red-800'
                      }`}
                    >
                      {req.policy_decision}
                    </span>
                  </div>
                  <p className="text-slate-600">{req.policy_reason}</p>
                </div>

                {/* Controls */}
                <div className="flex flex-wrap items-center justify-between gap-3 pt-1">
                  <div className="text-xs text-slate-400">
                    Created {new Date(req.created_at).toLocaleTimeString()}
                  </div>

                  <div className="flex items-center gap-2">
                    {req.status === 'approved' ? (
                      <button
                        onClick={() => handleProceedToPayment(req)}
                        disabled={actionLoading === req.id}
                        className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-semibold shadow-sm transition border-none cursor-pointer flex items-center gap-1.5"
                      >
                        <span>💳</span> Proceed to Test Checkout
                      </button>
                    ) : req.policy_decision !== 'BLOCK' ? (
                      <>
                        <button
                          onClick={() => handleReject(req.id)}
                          disabled={actionLoading === req.id}
                          className="px-4 py-2 bg-slate-100 hover:bg-red-50 text-slate-600 hover:text-red-700 rounded-xl text-xs font-semibold transition border border-slate-200 hover:border-red-200 cursor-pointer"
                        >
                          Reject
                        </button>
                        <button
                          onClick={() => handleApprove(req.id)}
                          disabled={actionLoading === req.id}
                          className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-semibold shadow-sm transition border-none cursor-pointer"
                        >
                          Approve Payment
                        </button>
                      </>
                    ) : (
                      <span className="text-xs font-semibold text-red-600 bg-red-50 px-3 py-1.5 rounded-lg">
                        ⛔ Blocked by Policy
                      </span>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Historical Requests */}
      {historyRequests.length > 0 && (
        <div>
          <h2 className="text-sm font-semibold text-slate-500 mb-3">Past Requests</h2>
          <div className="bg-white rounded-xl border border-slate-200 divide-y divide-slate-100 overflow-hidden text-xs">
            {historyRequests.slice(0, 10).map((r) => (
              <div key={r.id} className="p-3.5 flex items-center justify-between">
                <div>
                  <span className="font-semibold text-slate-800">{r.description}</span>
                  <span className="text-slate-400 ml-2">#{r.id.slice(0, 8)}</span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="font-bold text-slate-700">₹{(r.amount_paise / 100).toFixed(2)}</span>
                  <span
                    className={`px-2 py-0.5 rounded-full font-medium text-[11px] ${
                      r.status === 'completed'
                        ? 'bg-green-100 text-green-700'
                        : r.status === 'rejected'
                        ? 'bg-slate-100 text-slate-600'
                        : 'bg-amber-100 text-amber-700'
                    }`}
                  >
                    {r.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Simulated Checkout Modal */}
      {checkoutModal && (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl shadow-xl max-w-md w-full p-6 border border-slate-200">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100 mb-4">
              <div className="flex items-center gap-2">
                <span className="text-2xl">🛡️</span>
                <div>
                  <h3 className="font-bold text-slate-900 text-base">{checkoutModal.providerLabel}</h3>
                  <p className="text-[11px] text-amber-700 font-medium">DEMO / SANDBOX PAYMENT — NO REAL MONEY</p>
                </div>
              </div>
              <button
                onClick={() => setCheckoutModal(null)}
                className="text-slate-400 hover:text-slate-600 text-lg bg-transparent border-none cursor-pointer"
              >
                ✕
              </button>
            </div>

            <div className="bg-slate-50 rounded-xl p-4 mb-4 text-xs space-y-1.5">
              <div className="flex justify-between">
                <span className="text-slate-500">Order ID:</span>
                <span className="font-mono font-semibold text-slate-700">{checkoutModal.orderId}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Item:</span>
                <span className="font-medium text-slate-700">{checkoutModal.productName}</span>
              </div>
              <div className="flex justify-between text-sm pt-2 border-t border-slate-200 font-bold">
                <span className="text-slate-800">Total Payable:</span>
                <span className="text-indigo-700">₹{checkoutModal.amountInr}</span>
              </div>
            </div>

            <p className="text-xs text-slate-500 mb-4 leading-relaxed">
              In test mode, completing this payment triggers an HMAC-SHA256 signed webhook callback back to the FastAPI backend to verify and update the transaction ledger.
            </p>

            <div className="flex gap-2">
              <button
                onClick={() => handleCompleteSimulatedPayment(checkoutModal.orderId, 'fail')}
                className="flex-1 py-2.5 bg-red-50 hover:bg-red-100 text-red-700 font-semibold rounded-xl text-xs transition border border-red-200 cursor-pointer"
              >
                Simulate Failure
              </button>
              <button
                onClick={() => handleCompleteSimulatedPayment(checkoutModal.orderId, 'success')}
                className="flex-1 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white font-semibold rounded-xl text-xs transition border-none shadow-sm cursor-pointer"
              >
                Complete Payment ✓
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
