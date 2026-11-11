/**
 * Universal Marketplace Discovery, Comparison, and Secure Purchasing Platform.
 * Features:
 * - Prominent Universal Search Bar for any product or service query
 * - Dynamic NLP category & budget intent extraction
 * - Multi-provider comparison matrix (Lenskart, Croma, Pepperfry, Tanishq, MakeMyTrip, Amazon)
 * - Dynamic category navigation pills & filter drawer
 * - Product detail modal with specifications, rating, and secure payment authorization trigger
 * - Integrated policy-engine security notification
 */
import { useState, useEffect, useRef } from 'react';
import { marketplaceAPI, assistantAPI, paymentRequestAPI } from '../services/api';
import { useNavigate } from 'react-router-dom';

const TRENDING_SEARCHES = [
  "Sunglasses from Lenskart under ₹2,000",
  "Comfortable office chair under ₹5,000",
  "Gold earrings under ₹10,000",
  "Laptop for programming under ₹60,000",
  "Cheapest flight from Kolkata to Delhi",
  "Good telescope under ₹10,000",
  "Washing machine under ₹20,000",
  "Pure silk wedding saree under ₹8,000",
  "Vegetarian food thali under ₹200",
];

export default function Chat() {
  const [query, setQuery] = useState('');
  const [categories, setCategories] = useState([]);
  const [providers, setProviders] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [selectedProvider, setSelectedProvider] = useState('');
  const [sortBy, setSortBy] = useState('relevance');
  const [maxPrice, setMaxPrice] = useState('');
  
  const [results, setResults] = useState([]);
  const [detectedIntent, setDetectedIntent] = useState(null);
  const [aiSummary, setAiSummary] = useState('');
  const [loading, setLoading] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [actionNotice, setActionNotice] = useState(null);
  const [recentSearches, setRecentSearches] = useState([
    "Lenskart sunglasses under 2000",
    "Office chair under 5000",
    "Dell laptop under 50000"
  ]);

  const navigate = useNavigate();
  const resultsRef = useRef(null);

  // Load initial categories & providers
  useEffect(() => {
    const fetchMetadata = async () => {
      try {
        const [catRes, provRes] = await Promise.all([
          marketplaceAPI.getCategories(),
          marketplaceAPI.getProviders(),
        ]);
        setCategories(catRes.data || []);
        setProviders(provRes.data || []);
      } catch (err) {
        console.error('Failed to load marketplace metadata:', err);
      }
    };
    fetchMetadata();
    // Execute default search on load
    handleSearch(null, "Lenskart sunglasses under 2000");
  }, []);

  const handleSearch = async (e, customQuery = null) => {
    if (e) e.preventDefault();
    const searchQuery = (customQuery !== null ? customQuery : query).trim();
    if (!searchQuery && selectedCategory === 'All') return;

    setLoading(true);
    setActionNotice(null);

    // Save to recent searches
    if (searchQuery && !recentSearches.includes(searchQuery)) {
      setRecentSearches((prev) => [searchQuery, ...prev.slice(0, 4)]);
    }

    try {
      // 1. Detect dynamic intent & conversational summary via Assistant
      let intent = null;
      if (searchQuery) {
        try {
          const aiRes = await assistantAPI.chat(searchQuery, 'universal');
          if (aiRes.data) {
            setAiSummary(aiRes.data.reply || '');
            intent = aiRes.data.detected_intent;
            setDetectedIntent(intent);
          }
        } catch (aiErr) {
          console.warn('AI summary service fallback:', aiErr);
        }
      }

      // 2. Multi-provider marketplace search
      const params = {
        q: searchQuery || undefined,
        category: selectedCategory !== 'All' ? selectedCategory : (intent?.detected_category || undefined),
        provider: selectedProvider || undefined,
        max_price: maxPrice ? parseFloat(maxPrice) : (intent?.max_price_paise ? intent.max_price_paise / 100 : undefined),
        sort_by: sortBy,
        limit: 24,
      };

      const searchRes = await marketplaceAPI.search(params);
      setResults(searchRes.data || []);

      if (resultsRef.current) {
        resultsRef.current.scrollIntoView({ behavior: 'smooth' });
      }
    } catch (err) {
      console.error('Search failed:', err);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const handleCreatePaymentRequest = async (product) => {
    setLoading(true);
    try {
      const response = await paymentRequestAPI.create({
        product_id: product.id,
        agent_type: 'universal_marketplace',
        idempotency_key: `client_req_${Date.now()}_${product.id}`,
      });
      const req = response.data;

      let noticeText = `Payment authorization request generated for "${product.name}" (₹${product.price_inr.toFixed(2)}).`;
      if (req.policy_decision === 'REQUIRE_APPROVAL') {
        noticeText += ' ⏳ Policy Decision: REQUIRE_APPROVAL. Please review & sign on the Approvals screen.';
      } else if (req.policy_decision === 'ALLOW') {
        noticeText += ' ✅ Policy Decision: ALLOW. Pre-approved under autonomous policy limits.';
      } else if (req.policy_decision === 'BLOCK') {
        noticeText += ` ⛔ Policy Decision: BLOCKED (${req.policy_reason}).`;
      }

      setActionNotice({
        type: req.policy_decision,
        text: noticeText,
        requestId: req.id,
      });

      setSelectedProduct(null);
    } catch (err) {
      setActionNotice({
        type: 'BLOCK',
        text: err.response?.data?.detail || 'Failed to create payment authorization request.',
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50/60 pb-20">
      {/* Hero Universal Search Header */}
      <div className="bg-white border-b border-slate-200 pt-10 pb-8 px-4 sm:px-6 lg:px-8 shadow-xs">
        <div className="max-w-5xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-50 border border-blue-200/80 text-blue-700 text-xs font-semibold uppercase tracking-wider mb-3">
            <span>✨ Universal AI Marketplace Discovery</span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight">
            What are you looking for today?
          </h1>
          <p className="mt-2 text-sm sm:text-base text-slate-600 max-w-2xl mx-auto">
            Search, compare, and discover products and services across supported marketplaces with deterministic spending-policy governance.
          </p>

          {/* Primary Universal Search Bar */}
          <form onSubmit={(e) => handleSearch(e)} className="mt-6 max-w-3xl mx-auto relative">
            <div className="relative flex items-center shadow-md rounded-2xl border-2 border-blue-500/30 focus-within:border-blue-600 focus-within:ring-4 focus-within:ring-blue-100 bg-white transition-all">
              <span className="pl-4 text-slate-400 text-xl">🔍</span>
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search anything — furniture, jewellery, flights, electronics, fashion, telescopes..."
                className="w-full py-4 pl-3 pr-28 text-slate-900 placeholder-slate-400 text-sm sm:text-base bg-transparent border-none focus:outline-none"
              />
              <button
                type="submit"
                disabled={loading}
                className="absolute right-2 px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold text-sm rounded-xl transition cursor-pointer shadow-sm disabled:opacity-50"
              >
                {loading ? 'Searching...' : 'Search'}
              </button>
            </div>
          </form>

          {/* Trending Searches Chips */}
          <div className="mt-4 flex flex-wrap items-center justify-center gap-1.5 text-xs">
            <span className="text-slate-400 font-medium mr-1">Trending:</span>
            {TRENDING_SEARCHES.slice(0, 5).map((term, idx) => (
              <button
                key={idx}
                onClick={() => {
                  setQuery(term);
                  handleSearch(null, term);
                }}
                className="bg-slate-100 hover:bg-blue-50 hover:text-blue-700 text-slate-600 px-2.5 py-1 rounded-full border border-slate-200 transition cursor-pointer"
              >
                {term}
              </button>
            ))}
          </div>

          {/* Recent Searches */}
          {recentSearches.length > 0 && (
            <div className="mt-2 flex items-center justify-center gap-2 text-xs text-slate-500">
              <span className="text-slate-400">Recent:</span>
              {recentSearches.map((r, i) => (
                <button
                  key={i}
                  onClick={() => {
                    setQuery(r);
                    handleSearch(null, r);
                  }}
                  className="hover:text-blue-600 hover:underline cursor-pointer bg-transparent border-none text-slate-500 text-xs"
                >
                  "{r}"
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Dynamic Category Navigation Bar */}
      <div className="bg-white border-b border-slate-200 sticky top-16 z-30 shadow-xs">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-2.5 overflow-x-auto flex items-center gap-2 no-scrollbar">
          <button
            onClick={() => {
              setSelectedCategory('All');
              handleSearch(null, query);
            }}
            className={`px-3.5 py-1.5 rounded-full text-xs font-semibold whitespace-nowrap transition cursor-pointer ${
              selectedCategory === 'All'
                ? 'bg-blue-600 text-white shadow-xs'
                : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
            }`}
          >
            All Categories
          </button>
          {categories.map((cat) => (
            <button
              key={cat.id}
              onClick={() => {
                setSelectedCategory(cat.name);
                handleSearch(null, query);
              }}
              className={`px-3.5 py-1.5 rounded-full text-xs font-medium whitespace-nowrap transition cursor-pointer flex items-center gap-1.5 ${
                selectedCategory === cat.name
                  ? 'bg-blue-600 text-white font-semibold shadow-xs'
                  : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
              }`}
            >
              <span>{cat.icon || '🛍️'}</span>
              <span>{cat.name}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Security Action Notice Banner */}
      {actionNotice && (
        <div className="max-w-7xl mx-auto px-4 mt-6">
          <div
            className={`p-4 rounded-xl border flex items-center justify-between shadow-xs ${
              actionNotice.type === 'REQUIRE_APPROVAL'
                ? 'bg-amber-50 border-amber-300 text-amber-900'
                : actionNotice.type === 'ALLOW'
                ? 'bg-emerald-50 border-emerald-300 text-emerald-900'
                : 'bg-red-50 border-red-300 text-red-900'
            }`}
          >
            <div className="flex items-center gap-3">
              <span className="text-2xl">
                {actionNotice.type === 'REQUIRE_APPROVAL' ? '⏳' : actionNotice.type === 'ALLOW' ? '✅' : '⛔'}
              </span>
              <div>
                <p className="font-semibold text-sm">{actionNotice.text}</p>
                <p className="text-xs opacity-90 mt-0.5">
                  Policy-checked by PayPilot Deterministic Security Engine.
                </p>
              </div>
            </div>
            {actionNotice.requestId && (
              <button
                onClick={() => navigate('/approvals')}
                className="px-4 py-2 bg-orange-500 hover:bg-orange-600 text-white text-xs font-bold rounded-lg shadow-sm transition cursor-pointer whitespace-nowrap"
              >
                Review in Approvals →
              </button>
            )}
          </div>
        </div>
      )}

      {/* AI Intent & Conversational Intelligence Summary */}
      {aiSummary && (
        <div className="max-w-7xl mx-auto px-4 mt-6">
          <div className="bg-gradient-to-r from-blue-50 to-slate-50 border border-blue-200/80 rounded-2xl p-4 sm:p-5 shadow-xs">
            <div className="flex items-start gap-3">
              <div className="w-8 h-8 rounded-lg bg-blue-600 text-white flex items-center justify-center font-bold text-sm shrink-0">
                🤖
              </div>
              <div className="flex-1 text-sm text-slate-700 leading-relaxed">
                <div className="flex items-center gap-2 mb-1">
                  <span className="font-bold text-slate-900">PayPilot AI Market Intelligence</span>
                  {detectedIntent && (
                    <span className="text-[11px] bg-blue-100 text-blue-800 font-semibold px-2 py-0.5 rounded-md">
                      Detected: {detectedIntent.detected_category} {detectedIntent.detected_subcategory ? `› ${detectedIntent.detected_subcategory}` : ''}
                    </span>
                  )}
                  {detectedIntent?.detected_brand && (
                    <span className="text-[11px] bg-purple-100 text-purple-800 font-semibold px-2 py-0.5 rounded-md">
                      Brand: {detectedIntent.detected_brand}
                    </span>
                  )}
                  {detectedIntent?.max_price_paise && (
                    <span className="text-[11px] bg-emerald-100 text-emerald-800 font-semibold px-2 py-0.5 rounded-md">
                      Budget: ≤ ₹{(detectedIntent.max_price_paise / 100).toLocaleString('en-IN')}
                    </span>
                  )}
                </div>
                <p className="whitespace-pre-line text-slate-700 text-xs sm:text-sm mt-1">{aiSummary}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Main Marketplace Content Grid */}
      <div ref={resultsRef} className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-6">
        {/* Controls & Filter Bar */}
        <div className="bg-white border border-slate-200 rounded-xl p-3 sm:p-4 mb-6 flex flex-wrap items-center justify-between gap-3 shadow-xs">
          <div className="flex items-center gap-2 text-xs text-slate-600 font-medium">
            <span>Showing <strong className="text-slate-900">{results.length}</strong> items across marketplaces</span>
          </div>

          <div className="flex flex-wrap items-center gap-2.5">
            {/* Provider Filter */}
            <select
              value={selectedProvider}
              onChange={(e) => {
                setSelectedProvider(e.target.value);
                handleSearch(null, query);
              }}
              className="bg-slate-50 border border-slate-200 text-slate-700 text-xs rounded-lg px-2.5 py-1.5 focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium cursor-pointer"
            >
              <option value="">All Marketplaces</option>
              {providers.map((p) => (
                <option key={p.code} value={p.code}>
                  {p.logo_icon} {p.name}
                </option>
              ))}
            </select>

            {/* Sort Filter */}
            <select
              value={sortBy}
              onChange={(e) => {
                setSortBy(e.target.value);
                handleSearch(null, query);
              }}
              className="bg-slate-50 border border-slate-200 text-slate-700 text-xs rounded-lg px-2.5 py-1.5 focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium cursor-pointer"
            >
              <option value="relevance">Sort: Best Match</option>
              <option value="price_asc">Price: Low to High</option>
              <option value="price_desc">Price: High to Low</option>
              <option value="rating">Highest Rated</option>
              <option value="discount">Biggest Discount</option>
            </select>

            {/* Max Budget Input */}
            <div className="flex items-center gap-1 bg-slate-50 border border-slate-200 rounded-lg px-2 py-1">
              <span className="text-xs text-slate-400">Max ₹</span>
              <input
                type="number"
                value={maxPrice}
                onChange={(e) => setMaxPrice(e.target.value)}
                onBlur={() => handleSearch(null, query)}
                placeholder="Budget"
                className="w-20 bg-transparent text-xs text-slate-800 focus:outline-none"
              />
            </div>
          </div>
        </div>

        {/* Product Cards Grid */}
        {loading ? (
          <div className="text-center py-20">
            <div className="inline-block animate-spin rounded-full h-10 w-10 border-4 border-blue-600 border-t-transparent mb-3"></div>
            <p className="text-sm font-semibold text-slate-700">Querying multi-provider marketplaces in parallel...</p>
            <p className="text-xs text-slate-500 mt-1">Lenskart • Croma • Pepperfry • Tanishq • MakeMyTrip • Retail</p>
          </div>
        ) : results.length === 0 ? (
          <div className="bg-white border border-slate-200 rounded-2xl p-12 text-center shadow-xs">
            <span className="text-4xl">🔍</span>
            <h3 className="text-lg font-bold text-slate-800 mt-3">No matching items found</h3>
            <p className="text-sm text-slate-500 max-w-md mx-auto mt-1">
              Try adjusting your query, raising the budget limit, or clearing marketplace filters.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
            {results.map((product) => (
              <div
                key={product.id}
                className="bg-white border border-slate-200 rounded-2xl overflow-hidden shadow-xs hover:shadow-md hover:border-blue-300 transition-all flex flex-col group"
              >
                {/* Product Image & Badges */}
                <div className="relative h-48 bg-slate-100 overflow-hidden">
                  <img
                    src={product.image_url || 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500&q=80'}
                    alt={product.name}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                    loading="lazy"
                  />
                  {/* Provider & Verification Badge */}
                  <div className="absolute top-2.5 left-2.5 flex items-center gap-1.5">
                    <span className="bg-slate-900/80 backdrop-blur-xs text-white text-[11px] font-semibold px-2 py-0.5 rounded-md shadow-xs">
                      {product.provider}
                    </span>
                    <span className="bg-blue-600/90 text-white text-[10px] font-bold px-1.5 py-0.5 rounded shadow-xs uppercase tracking-wider">
                      {product.data_source_type}
                    </span>
                  </div>

                  {/* Discount / Recommend Tag */}
                  {product.discount_percent && product.discount_percent > 0 && (
                    <div className="absolute top-2.5 right-2.5 bg-orange-500 text-white text-[11px] font-bold px-2 py-0.5 rounded-md shadow-xs">
                      {product.discount_percent}% OFF
                    </div>
                  )}
                </div>

                {/* Product Info */}
                <div className="p-4 flex-1 flex flex-col justify-between">
                  <div>
                    {/* Category & Brand */}
                    <div className="flex items-center justify-between text-[11px] text-slate-500 mb-1">
                      <span className="font-semibold text-blue-700">{product.brand || product.merchant}</span>
                      <span className="truncate max-w-[120px]">{product.subcategory || product.category}</span>
                    </div>

                    {/* Product Title */}
                    <h4 className="font-bold text-slate-900 text-sm line-clamp-2 leading-snug group-hover:text-blue-600 transition">
                      {product.name}
                    </h4>

                    {/* Rating */}
                    <div className="flex items-center gap-1.5 mt-1.5 text-xs text-slate-600">
                      <span className="text-amber-500 font-bold">★ {product.rating?.toFixed(1) || '4.5'}</span>
                      <span className="text-slate-400">({product.rating_count || 120})</span>
                    </div>

                    {/* Price Block */}
                    <div className="mt-3 flex items-baseline gap-2">
                      <span className="text-lg font-extrabold text-slate-900">
                        ₹{product.price_inr.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                      </span>
                      {product.original_price_inr && product.original_price_inr > product.price_inr && (
                        <span className="text-xs text-slate-400 line-through">
                          ₹{product.original_price_inr.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="mt-4 pt-3 border-t border-slate-100 flex items-center gap-2">
                    <button
                      onClick={() => setSelectedProduct(product)}
                      className="flex-1 py-2 text-xs font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-lg transition cursor-pointer"
                    >
                      Details & Specs
                    </button>
                    {product.supports_integrated_checkout ? (
                      <button
                        onClick={() => handleCreatePaymentRequest(product)}
                        className="flex-1 py-2 text-xs font-bold text-white bg-blue-600 hover:bg-blue-700 rounded-lg shadow-xs transition cursor-pointer"
                      >
                        Select & Pay →
                      </button>
                    ) : (
                      <a
                        href={product.product_url || '#'}
                        target="_blank"
                        rel="noreferrer"
                        className="flex-1 py-2 text-xs font-bold text-center text-blue-700 bg-blue-50 hover:bg-blue-100 rounded-lg transition no-underline"
                      >
                        External Link ↗
                      </a>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Product Specification & Detail Modal */}
      {selectedProduct && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs animate-fade-in">
          <div className="bg-white rounded-3xl max-w-2xl w-full max-h-[90vh] overflow-y-auto shadow-2xl border border-slate-200">
            {/* Modal Header */}
            <div className="p-6 border-b border-slate-100 flex items-start justify-between">
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-xs font-semibold text-blue-600 uppercase tracking-wide">
                    {selectedProduct.provider}
                  </span>
                  <span className="text-[10px] bg-slate-100 text-slate-700 font-bold px-1.5 py-0.5 rounded">
                    {selectedProduct.data_source_type}
                  </span>
                </div>
                <h3 className="text-xl font-bold text-slate-900 mt-1">{selectedProduct.name}</h3>
                <p className="text-xs text-slate-500 mt-0.5">Sold & Verified by {selectedProduct.merchant}</p>
              </div>
              <button
                onClick={() => setSelectedProduct(null)}
                className="w-8 h-8 rounded-full bg-slate-100 text-slate-500 hover:bg-slate-200 flex items-center justify-center cursor-pointer border-none"
              >
                ✕
              </button>
            </div>

            {/* Modal Body */}
            <div className="p-6 space-y-5">
              <div className="flex flex-col sm:flex-row gap-5">
                <div className="w-full sm:w-48 h-48 rounded-2xl bg-slate-100 overflow-hidden shrink-0">
                  <img
                    src={selectedProduct.image_url}
                    alt={selectedProduct.name}
                    className="w-full h-full object-cover"
                  />
                </div>
                <div className="flex-1 flex flex-col justify-between">
                  <div>
                    <div className="flex items-baseline gap-2">
                      <span className="text-2xl font-extrabold text-slate-900">
                        ₹{selectedProduct.price_inr.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                      </span>
                      {selectedProduct.original_price_inr && (
                        <span className="text-sm text-slate-400 line-through">
                          ₹{selectedProduct.original_price_inr.toLocaleString('en-IN')}
                        </span>
                      )}
                      {selectedProduct.discount_percent && (
                        <span className="text-xs bg-orange-100 text-orange-700 font-bold px-2 py-0.5 rounded">
                          {selectedProduct.discount_percent}% OFF
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-slate-600 mt-2 leading-relaxed">
                      {selectedProduct.description}
                    </p>
                  </div>

                  {selectedProduct.delivery_info && (
                    <div className="mt-3 bg-slate-50 border border-slate-200/80 rounded-xl p-2.5 text-xs text-slate-700 flex items-center gap-2">
                      <span>🚚</span>
                      <span>{selectedProduct.delivery_info}</span>
                    </div>
                  )}
                </div>
              </div>

              {/* Technical Specifications */}
              {selectedProduct.specifications && Object.keys(selectedProduct.specifications).length > 0 && (
                <div>
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-2">
                    Verified Specifications
                  </h4>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
                    {Object.entries(selectedProduct.specifications).map(([key, val]) => (
                      <div key={key} className="bg-slate-50 p-2.5 rounded-lg border border-slate-100">
                        <span className="text-slate-400 block text-[10px]">{key}</span>
                        <span className="font-semibold text-slate-800">{String(val)}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Security Governance Notice */}
              <div className="bg-blue-50 border border-blue-200/80 rounded-xl p-3.5 text-xs text-blue-900">
                <span className="font-bold flex items-center gap-1.5 mb-1">
                  🛡️ PayPilot AI Policy Engine Guarantee
                </span>
                Selecting this product creates a secure payment request evaluated by your centralized spending rules. No money can be spent without your policy pre-clearance or explicit signature.
              </div>
            </div>

            {/* Modal Footer Actions */}
            <div className="p-6 bg-slate-50 border-t border-slate-100 flex items-center justify-between">
              {selectedProduct.product_url ? (
                <a
                  href={selectedProduct.product_url}
                  target="_blank"
                  rel="noreferrer"
                  className="text-xs font-medium text-slate-600 hover:text-blue-600 hover:underline flex items-center gap-1"
                >
                  View on {selectedProduct.provider} ↗
                </a>
              ) : <div></div>}

              <div className="flex items-center gap-2">
                <button
                  onClick={() => setSelectedProduct(null)}
                  className="px-4 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-200 rounded-xl transition cursor-pointer border-none bg-transparent"
                >
                  Cancel
                </button>
                {selectedProduct.supports_integrated_checkout ? (
                  <button
                    onClick={() => handleCreatePaymentRequest(selectedProduct)}
                    className="px-6 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs rounded-xl shadow-sm transition cursor-pointer"
                  >
                    Authorize via Policy Engine →
                  </button>
                ) : (
                  <a
                    href={selectedProduct.product_url}
                    target="_blank"
                    rel="noreferrer"
                    className="px-6 py-2.5 bg-slate-900 text-white font-bold text-xs rounded-xl transition no-underline"
                  >
                    Visit External Checkout ↗
                  </a>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
