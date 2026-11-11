/**
 * Approvals Page with Blue, Grey, and Orange design system.
 * Central payment authorization screen. Shows all pending payment requests,
 * exact amount, product, merchant verification status, and policy evaluation reasons.
 * Enables user to Approve, Reject, and proceed to sandbox payment completion.
 */
import { useState, useEffect } from 'react';
import { paymentRequestAPI, paymentAPI } from '../services/api';

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
      setRequests(res.data || []);
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
      setMessage({ type: 'success', text: `Payment request #${requestId.slice(0, 8)} successfully authorized!` });
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
      setMessage({ type: 'error', text: err.response?.data?.detail || 'Payment initialization failed.' });
    } finally {
      setActionLoading(null);
    }
  };

  const handleSimulatePaymentSuccess = async () => {
    if (!checkoutModal) return;
    const { orderId, requestId } = checkoutModal;
    try {
      await paymentAPI.verify({
        order_id: orderId,
        payment_id: `sim_pay_${Date.now()}`,
        signature: 'simulated_client_checkout',
      });
      setMessage({ type: 'success', text: '✅ Sandbox payment succeeded! Transaction authorized & completed.' });
      setCheckoutModal(null);
      await loadRequests();
    } catch (err) {
      setMessage({ type: 'error', text: 'Payment verification failed.' });
    }
  };

  const pendingRequests = requests.filter((r) => r.status === 'PENDING_APPROVAL');
  const pastRequests = requests.filter((r) => r.status !== 'PENDING_APPROVAL');

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 animate-fade-in">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between pb-6 border-b border-slate-200 gap-4">
        <div>
          <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-blue-50 border border-blue-200 text-blue-700 text-xs font-semibold mb-2">
            <span>🛡️ Centralized Spending Policy Engine</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
            Payment Authorization & Approvals
          </h1>
          <p className="text-slate-600 text-sm mt-1">
            Deterministic security guardrails: review AI purchase requests before any money moves.
          </p>
        </div>
        <button
          onClick={loadRequests}
          className="self-start sm:self-auto px-4 py-2 text-xs font-semibold text-slate-700 bg-white border border-slate-200 rounded-xl hover:bg-slate-50 transition cursor-pointer shadow-xs"
        >
          🔄 Refresh
        </button>
      </div>

      {/* Status Messages */}
      {message && (
        <div
          className={`mt-4 p-4 rounded-xl border text-sm flex items-center justify-between ${
            message.type === 'success'
              ? 'bg-emerald-50 border-emerald-300 text-emerald-900'
              : message.type === 'error'
              ? 'bg-red-50 border-red-300 text-red-900'
              : 'bg-blue-50 border-blue-300 text-blue-900'
          }`}
        >
          <span>{message.text}</span>
          <button onClick={() => setMessage(null)} className="text-xs font-bold text-slate-400 hover:text-slate-600 cursor-pointer border-none bg-transparent">✕</button>
        </div>
      )}

      {/* Pending Approvals Section (Orange High-Priority) */}
      <div className="mt-8">
        <div className="flex items-center gap-2 mb-4">
          <h2 className="text-lg font-bold text-slate-900">Pending User Approvals</h2>
          {pendingRequests.length > 0 && (
            <span className="px-2 py-0.5 text-xs font-bold bg-orange-500 text-white rounded-full">
              {pendingRequests.length} Required
            </span>
          )}
        </div>

        {loading ? (
          <div className="text-center py-12 text-slate-400 text-sm">Loading approval requests...</div>
        ) : pendingRequests.length === 0 ? (
          <div className="bg-white border border-slate-200 rounded-2xl p-8 text-center shadow-xs">
            <span className="text-3xl">🎉</span>
            <p className="text-slate-700 font-semibold text-sm mt-2">All clear! No pending transactions requiring your approval.</p>
            <p className="text-slate-500 text-xs mt-1">AI agent requests requiring signature will appear here.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {pendingRequests.map((req) => (
              <div
                key={req.id}
                className="bg-white border-2 border-orange-200/90 rounded-2xl p-5 shadow-xs hover:shadow-md transition-all flex flex-col justify-between"
              >
                <div>
                  {/* Header info */}
                  <div className="flex items-start justify-between">
                    <div>
                      <span className="text-[11px] font-mono text-slate-400 block">ID: {req.id.slice(0, 8)}</span>
                      <h3 className="font-bold text-slate-900 text-base mt-0.5">{req.product?.name || 'Item Request'}</h3>
                    </div>
                    <span className="px-2.5 py-1 text-xs font-bold bg-orange-100 text-orange-800 rounded-lg">
                      REQUIRE_APPROVAL
                    </span>
                  </div>

                  {/* Merchant & Verification */}
                  <div className="mt-3 flex items-center gap-2 text-xs">
                    <span className="text-slate-500">Merchant:</span>
                    <strong className="text-slate-800">{req.merchant?.name || 'Verified Merchant'}</strong>
                    {req.merchant?.is_verified ? (
                      <span className="text-emerald-700 bg-emerald-50 px-1.5 py-0.2 rounded text-[10px] font-bold">
                        ✓ Verified
                      </span>
                    ) : (
                      <span className="text-amber-700 bg-amber-50 px-1.5 py-0.2 rounded text-[10px] font-bold">
                        ⚠ Unverified
                      </span>
                    )}
                  </div>

                  {/* Policy Decision Reason */}
                  <div className="mt-2.5 bg-slate-50 p-2.5 rounded-xl border border-slate-100 text-xs text-slate-700">
                    <span className="font-semibold text-slate-900 block text-[11px] mb-0.5">Policy Evaluation:</span>
                    {req.policy_reason || 'Transaction exceeds autonomous threshold. Requires signature.'}
                  </div>

                  {/* Price */}
                  <div className="mt-4 flex items-baseline gap-2">
                    <span className="text-xs text-slate-500 font-medium">Exact Amount:</span>
                    <span className="text-2xl font-black text-slate-900">
                      ₹{(req.amount_paise / 100).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                    </span>
                  </div>
                </div>

                {/* Actions: Selective Orange for the high-priority Authorize button */}
                <div className="mt-5 pt-3 border-t border-slate-100 flex items-center gap-3">
                  <button
                    onClick={() => handleReject(req.id)}
                    disabled={actionLoading === req.id}
                    className="flex-1 py-2.5 text-xs font-semibold text-red-700 bg-red-50 hover:bg-red-100 rounded-xl transition cursor-pointer border-none"
                  >
                    Reject
                  </button>
                  <button
                    onClick={() => handleApprove(req.id)}
                    disabled={actionLoading === req.id}
                    className="flex-2 py-2.5 text-xs font-bold text-white bg-orange-500 hover:bg-orange-600 rounded-xl transition cursor-pointer shadow-sm shadow-orange-500/30"
                  >
                    {actionLoading === req.id ? 'Authorizing...' : 'Approve & Authorize →'}
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Past Requests / Ready for Payment Section */}
      <div className="mt-12">
        <h2 className="text-lg font-bold text-slate-900 mb-4">Authorized & Processed History</h2>
        {pastRequests.length === 0 ? (
          <p className="text-slate-400 text-sm">No historical records yet.</p>
        ) : (
          <div className="bg-white border border-slate-200 rounded-2xl overflow-hidden shadow-xs">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 text-xs uppercase font-semibold">
                <tr>
                  <th className="py-3 px-4">Request</th>
                  <th className="py-3 px-4">Merchant</th>
                  <th className="py-3 px-4">Amount</th>
                  <th className="py-3 px-4">Policy Result</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {pastRequests.map((req) => (
                  <tr key={req.id} className="hover:bg-slate-50/70 transition">
                    <td className="py-3 px-4 font-medium text-slate-900">
                      {req.product?.name || req.id.slice(0, 8)}
                    </td>
                    <td className="py-3 px-4 text-slate-600 text-xs">
                      {req.merchant?.name || 'Verified Merchant'}
                    </td>
                    <td className="py-3 px-4 font-bold text-slate-900">
                      ₹{(req.amount_paise / 100).toFixed(2)}
                    </td>
                    <td className="py-3 px-4">
                      <span
                        className={`text-xs px-2 py-0.5 rounded font-bold ${
                          req.policy_decision === 'ALLOW'
                            ? 'bg-emerald-100 text-emerald-800'
                            : req.policy_decision === 'REQUIRE_APPROVAL'
                            ? 'bg-amber-100 text-amber-800'
                            : 'bg-red-100 text-red-800'
                        }`}
                      >
                        {req.policy_decision}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      <span
                        className={`text-xs font-semibold px-2 py-0.5 rounded-full ${
                          req.status === 'APPROVED'
                            ? 'bg-blue-100 text-blue-800'
                            : req.status === 'COMPLETED'
                            ? 'bg-emerald-100 text-emerald-800'
                            : req.status === 'REJECTED'
                            ? 'bg-slate-100 text-slate-600'
                            : 'bg-red-100 text-red-800'
                        }`}
                      >
                        {req.status}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-right">
                      {req.status === 'APPROVED' && (
                        <button
                          onClick={() => handleProceedToPayment(req)}
                          disabled={actionLoading === req.id}
                          className="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs rounded-lg transition cursor-pointer shadow-xs"
                        >
                          Proceed to Payment →
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Simulated Checkout Modal */}
      {checkoutModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs animate-fade-in">
          <div className="bg-white rounded-3xl max-w-md w-full p-6 shadow-2xl border border-slate-200">
            <div className="flex items-center justify-between pb-4 border-b border-slate-100">
              <div className="flex items-center gap-2">
                <span className="text-xl">💳</span>
                <h3 className="font-bold text-slate-900 text-base">Payment Authorization Gateway</h3>
              </div>
              <button
                onClick={() => setCheckoutModal(null)}
                className="text-slate-400 hover:text-slate-600 border-none bg-transparent cursor-pointer"
              >
                ✕
              </button>
            </div>

            <div className="py-5 space-y-4 text-xs text-slate-600">
              <div className="bg-slate-50 p-4 rounded-xl border border-slate-100">
                <div className="flex justify-between mb-2">
                  <span className="text-slate-500">Item:</span>
                  <strong className="text-slate-800">{checkoutModal.productName}</strong>
                </div>
                <div className="flex justify-between mb-2">
                  <span className="text-slate-500">Order ID:</span>
                  <span className="font-mono text-slate-700">{checkoutModal.orderId}</span>
                </div>
                <div className="flex justify-between text-base font-extrabold text-slate-900 pt-2 border-t border-slate-200">
                  <span>Payable Total:</span>
                  <span>₹{checkoutModal.amountInr}</span>
                </div>
              </div>

              <div className="p-3 rounded-xl bg-blue-50 border border-blue-200 text-blue-900">
                <strong>HMAC-SHA256 Sandbox Verification:</strong> Signature will be cryptographically verified by the backend webhook receiver before balance mutation.
              </div>
            </div>

            <div className="flex items-center gap-3 pt-4 border-t border-slate-100">
              <button
                onClick={() => setCheckoutModal(null)}
                className="flex-1 py-2.5 text-xs font-semibold text-slate-600 bg-slate-100 rounded-xl hover:bg-slate-200 transition cursor-pointer border-none"
              >
                Cancel
              </button>
              <button
                onClick={handleSimulatePaymentSuccess}
                className="flex-2 py-2.5 text-xs font-bold text-white bg-blue-600 hover:bg-blue-700 rounded-xl transition cursor-pointer shadow-sm shadow-blue-500/20"
              >
                Confirm Payment (Sandbox) →
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
