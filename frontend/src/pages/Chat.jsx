/**
 * AI Purchasing Assistant Chat Page.
 * Allows users to converse with AI agents (Food, Shopping, Electronics),
 * discover products from verified merchant catalogs, and initiate policy-checked payment requests.
 */
import { useState, useRef, useEffect } from 'react';
import { assistantAPI, paymentRequestAPI, paymentAPI } from '../services/api';
import { useNavigate } from 'react-router-dom';

export default function Chat() {
  const [messages, setMessages] = useState([
    {
      sender: 'assistant',
      text: "👋 Hi! I'm your PayPilot AI Purchasing Assistant. Tell me what you'd like to buy — for example:\n\n• *\"Find me a vegetarian lunch under ₹200. Don't make any payment until I approve.\"*\n• *\"Find wireless earbuds under ₹1000 with good battery life.\"*",
      recommendations: [],
    },
  ]);
  const [input, setInput] = useState('');
  const [agentType, setAgentType] = useState('food');
  const [loading, setLoading] = useState(false);
  const [actionNotice, setActionNotice] = useState(null);
  const messagesEndRef = useRef(null);
  const navigate = useNavigate();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleSend = async (e) => {
    e?.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput('');
    setMessages((prev) => [...prev, { sender: 'user', text: userMessage }]);
    setLoading(true);
    setActionNotice(null);

    try {
      const response = await assistantAPI.chat(userMessage, agentType);
      const data = response.data;

      setMessages((prev) => [
        ...prev,
        {
          sender: 'assistant',
          text: data.reply,
          recommendations: data.recommendations || [],
        },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          sender: 'assistant',
          text: '⚠️ An error occurred while communicating with the assistant service.',
          recommendations: [],
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectProduct = async (product) => {
    setLoading(true);
    try {
      const response = await paymentRequestAPI.create({
        product_id: product.id,
        agent_type: agentType,
        idempotency_key: `client_req_${Date.now()}_${product.id}`,
      });
      const req = response.data;

      let noticeText = `Payment Request created for "${product.name}" (₹${(product.price_paise / 100).toFixed(2)}).`;
      if (req.policy_decision === 'REQUIRE_APPROVAL') {
        noticeText += ' ⏳ Policy Decision: REQUIRE_APPROVAL. Please approve on the Approvals screen.';
      } else if (req.policy_decision === 'ALLOW') {
        noticeText += ' ✅ Policy Decision: ALLOW. Pre-approved under active limits.';
      } else if (req.policy_decision === 'BLOCK') {
        noticeText += ` ⛔ Policy Decision: BLOCK (${req.policy_reason}).`;
      }

      setActionNotice({
        type: req.policy_decision,
        text: noticeText,
        requestId: req.id,
      });

      setMessages((prev) => [
        ...prev,
        {
          sender: 'assistant',
          text: `📋 **Payment Request #${req.id.slice(0, 8)} Created**\n\n• **Item:** ${product.name}\n• **Amount:** ₹${(product.price_paise / 100).toFixed(2)}\n• **Policy Engine Decision:** \`${req.policy_decision}\`\n• **Reason:** ${req.policy_reason}\n\n${
            req.policy_decision === 'REQUIRE_APPROVAL'
              ? '👉 **Action Required:** Please review and authorize this on the **Approvals** screen.'
              : req.policy_decision === 'ALLOW'
              ? '👉 This transaction is permissible under your policy rules.'
              : '⛔ Transaction cannot proceed due to policy violation.'
          }`,
          recommendations: [],
        },
      ]);
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to create payment request.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto px-4 py-6">
      {/* Header and Agent Selector */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between pb-4 border-b border-slate-200 mb-4 gap-3">
        <div>
          <h1 className="text-2xl font-bold text-slate-800 flex items-center gap-2">
            <span>🤖</span> AI Purchasing Assistant
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            AI recommends & requests • Deterministic backend policy engine governs • You approve
          </p>
        </div>

        {/* Multi-Agent Role Switcher */}
        <div className="flex items-center gap-2 bg-slate-100 p-1 rounded-xl text-xs font-semibold">
          <button
            onClick={() => setAgentType('food')}
            className={`px-3 py-1.5 rounded-lg transition cursor-pointer border-none ${
              agentType === 'food'
                ? 'bg-white text-indigo-700 shadow-sm'
                : 'text-slate-600 hover:text-slate-900 bg-transparent'
            }`}
          >
            🍔 Food Agent
          </button>
          <button
            onClick={() => setAgentType('shopping')}
            className={`px-3 py-1.5 rounded-lg transition cursor-pointer border-none ${
              agentType === 'shopping'
                ? 'bg-white text-indigo-700 shadow-sm'
                : 'text-slate-600 hover:text-slate-900 bg-transparent'
            }`}
          >
            💻 Electronics & Shopping
          </button>
        </div>
      </div>

      {/* Action Banner */}
      {actionNotice && (
        <div
          className={`mb-4 p-4 rounded-xl flex items-center justify-between text-sm ${
            actionNotice.type === 'REQUIRE_APPROVAL'
              ? 'bg-amber-50 border border-amber-200 text-amber-900'
              : actionNotice.type === 'BLOCK'
              ? 'bg-red-50 border border-red-200 text-red-900'
              : 'bg-green-50 border border-green-200 text-green-900'
          }`}
        >
          <div>{actionNotice.text}</div>
          {actionNotice.type === 'REQUIRE_APPROVAL' && (
            <button
              onClick={() => navigate('/approvals')}
              className="ml-4 px-3 py-1.5 bg-amber-600 hover:bg-amber-700 text-white rounded-lg font-medium text-xs border-none cursor-pointer"
            >
              Go to Approvals →
            </button>
          )}
        </div>
      )}

      {/* Chat Messages Container */}
      <div className="bg-white rounded-2xl shadow-sm border border-slate-200 h-[520px] flex flex-col overflow-hidden">
        <div className="flex-1 p-5 overflow-y-auto space-y-4">
          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={`flex flex-col ${msg.sender === 'user' ? 'items-end' : 'items-start'}`}
            >
              <div
                className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-relaxed whitespace-pre-wrap ${
                  msg.sender === 'user'
                    ? 'bg-indigo-600 text-white rounded-br-sm'
                    : 'bg-slate-100 text-slate-800 rounded-bl-sm border border-slate-200'
                }`}
              >
                {msg.text}
              </div>

              {/* Product Recommendation Cards */}
              {msg.recommendations && msg.recommendations.length > 0 && (
                <div className="mt-3 w-full max-w-2xl grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {msg.recommendations.map((item) => (
                    <div
                      key={item.id}
                      className="bg-white border border-slate-200 rounded-xl p-3 shadow-sm hover:border-indigo-400 transition flex flex-col justify-between"
                    >
                      <div>
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-slate-100 text-slate-700">
                            {item.category}
                          </span>
                          <span className="text-sm font-bold text-indigo-700">
                            ₹{(item.price_paise / 100).toFixed(2)}
                          </span>
                        </div>
                        <h4 className="font-semibold text-slate-900 text-sm mt-1">{item.name}</h4>
                        <p className="text-xs text-slate-500 mt-1 line-clamp-2">{item.description}</p>
                      </div>

                      <button
                        onClick={() => handleSelectProduct(item)}
                        className="mt-3 w-full py-1.5 px-3 bg-indigo-50 hover:bg-indigo-600 text-indigo-700 hover:text-white rounded-lg text-xs font-semibold transition border border-indigo-200 hover:border-transparent cursor-pointer"
                      >
                        Select & Request Purchase
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}

          {loading && (
            <div className="flex items-center gap-2 text-xs text-slate-400">
              <div className="animate-spin rounded-full h-3.5 w-3.5 border-b-2 border-indigo-600"></div>
              <span>PayPilot Agent is analyzing requirements and querying catalog...</span>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Quick Suggestion Chips */}
        <div className="px-4 py-2 bg-slate-50 border-t border-slate-200 flex flex-wrap gap-2 text-xs text-slate-600">
          <span className="font-medium text-slate-400 mr-1">Try:</span>
          <button
            onClick={() => setInput("Find me a vegetarian lunch under ₹200. Don't make any payment until I approve.")}
            className="px-2.5 py-1 bg-white border border-slate-200 rounded-full hover:bg-slate-100 cursor-pointer text-xs"
          >
            🥗 Vegetarian lunch &lt; ₹200
          </button>
          <button
            onClick={() => setInput('Find wireless earbuds under ₹1000 with good battery life.')}
            className="px-2.5 py-1 bg-white border border-slate-200 rounded-full hover:bg-slate-100 cursor-pointer text-xs"
          >
            🎧 Wireless earbuds &lt; ₹1000
          </button>
          <button
            onClick={() => setInput('Find a fast laptop charger under ₹500.')}
            className="px-2.5 py-1 bg-white border border-slate-200 rounded-full hover:bg-slate-100 cursor-pointer text-xs"
          >
            ⚡ Fast charger &lt; ₹500
          </button>
        </div>

        {/* Input Bar */}
        <form onSubmit={handleSend} className="p-3 bg-white border-t border-slate-200 flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={`Ask the ${agentType === 'food' ? 'Food' : 'Shopping'} Agent for purchases, budgets, dietary constraints...`}
            className="flex-1 px-4 py-2.5 text-sm border border-slate-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none"
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-sm font-semibold transition disabled:opacity-50 cursor-pointer border-none"
          >
            Send
          </button>
        </form>
      </div>
    </div>
  );
}
