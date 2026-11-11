/**
 * Universal Search Engine & Discovery Interface.
 * Exact Palette:
 * Deep Ocean Blue:   #022E51
 * Steel Blue Grey:   #A3B4C8
 * Burnt Orange:      #CC6D3D
 * Deep Burnt Orange: #B74803
 */
import { useState, useEffect, useRef } from 'react';
import { marketplaceAPI, assistantAPI, paymentRequestAPI } from '../services/api';
import { useNavigate } from 'react-router-dom';

const POPULAR_SEARCHES = [
  "Flights from Kolkata to Delhi under ₹6,000",
  "Three-seater sofa under ₹15,000",
  "Gold earrings under ₹10,000",
  "Programming laptop under ₹60,000",
  "Red wedding saree under ₹5,000",
  "Beginner telescope under ₹10,000",
  "Vegetarian lunch under ₹200",
  "Hotel in Darjeeling under ₹3,000",
  "Musical keyboard under ₹8,000",
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
  const [searchTelemetry, setSearchTelemetry] = useState(null);
  const [loading, setLoading] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [actionNotice, setActionNotice] = useState(null);
  const [recentSearches, setRecentSearches] = useState([
    "Flights from Kolkata to Delhi",
    "Three-seater sofa under 15000",
    "Gold earrings under 10000",
  ]);

  const navigate = useNavigate();
  const resultsRef = useRef(null);

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
        console.error('Failed to load search metadata:', err);
      }
    };
    fetchMetadata();
    // Default initial search
    handleSearch(null, "Three-seater sofa under 15000");
  }, []);

  const handleSearch = async (e, customQuery = null) => {
    if (e) e.preventDefault();
    const searchQuery = (customQuery !== null ? customQuery : query).trim();
    if (!searchQuery && selectedCategory === 'All') return;

    setLoading(true);
    setActionNotice(null);

    if (searchQuery && !recentSearches.includes(searchQuery)) {
      setRecentSearches((prev) => [searchQuery, ...prev.slice(0, 4)]);
    }

    const startTime = performance.now();

    try {
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
          console.warn('AI intent fallback:', aiErr);
        }
      }

      const params = {
        q: searchQuery || undefined,
        category: selectedCategory !== 'All' ? selectedCategory : (intent?.detected_category || undefined),
        provider: selectedProvider || undefined,
        max_price: maxPrice ? parseFloat(maxPrice) : (intent?.max_price_paise ? intent.max_price_paise / 100 : undefined),
        sort_by: sortBy,
        limit: 30,
      };

      const searchRes = await marketplaceAPI.search(params);
      const fetched = searchRes.data || [];
      setResults(fetched);

      const durationMs = Math.round(performance.now() - startTime);
      const uniqueSources = Array.from(new Set(fetched.map((p) => p.provider)));

      setSearchTelemetry({
        timeMs: durationMs,
        sourcesCount: uniqueSources.length,
        sourcesList: uniqueSources,
        totalFound: fetched.length,
        liveCount: fetched.filter((p) => p.data_source_type === 'LIVE').length,
      });

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
        agent_type: 'universal_search_engine',
        idempotency_key: `client_req_${Date.now()}_${product.id}`,
      });
      const req = response.data;

      let noticeText = `Payment request generated for "${product.name}" (₹${product.price_inr.toFixed(2)}).`;
      if (req.policy_decision === 'REQUIRE_APPROVAL') {
        noticeText += ' ⏳ Policy Decision: REQUIRE_APPROVAL. Please review and authorize on the Approvals screen.';
      } else if (req.policy_decision === 'ALLOW') {
        noticeText += ' ✅ Policy Decision: ALLOW. Pre-approved under active autonomous limits.';
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
        text: err.response?.data?.detail || 'Failed to generate payment authorization request.',
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#F4F7FA] pb-24">
      {/* Universal Search Hero Section (#022E51 Deep Ocean Blue) */}
      <div className="bg-[#022E51] text-white pt-12 pb-10 px-4 sm:px-6 lg:px-8 border-b border-[#011E36] shadow-sm">
        <div className="max-w-5xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 px-3.5 py-1 rounded-full bg-white/10 border border-white/20 text-[#A3B4C8] text-xs font-bold uppercase tracking-wider mb-3">
            <span>🌐 Universal Internet & Marketplace Search</span>
          </div>
          <h1 className="text-3xl sm:text-5xl font-black text-white tracking-tight">
            Find anything. Search everywhere.
          </h1>
          <p className="mt-2.5 text-sm sm:text-base text-[#A3B4C8] max-w-2xl mx-auto font-medium">
            Discover and compare products and services across connected marketplaces and the wider web.
          </p>

          {/* Primary Universal Search Bar */}
          <form onSubmit={(e) => handleSearch(e)} className="mt-7 max-w-3xl mx-auto relative">
            <div className="relative flex items-center shadow-xl rounded-2xl border-2 border-[#A3B4C8]/40 focus-within:border-[#CC6D3D] focus-within:ring-4 focus-within:ring-[#CC6D3D]/20 bg-white transition-all">
              <span className="pl-4 text-[#5A6D82] text-xl">🔍</span>
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search anything — furniture, jewellery, flights, fashion, electronics, telescopes..."
                className="w-full py-4 pl-3 pr-32 text-[#022E51] placeholder-[#5A6D82] text-sm sm:text-base bg-transparent border-none focus:outline-none font-medium"
              />
              <button
                type="submit"
                disabled={loading}
                className="absolute right-2 px-6 py-2.5 bg-[#CC6D3D] hover:bg-[#B74803] text-white font-extrabold text-xs sm:text-sm rounded-xl transition cursor-pointer shadow-sm disabled:opacity-50"
              >
                {loading ? 'Searching...' : 'Search'}
              </button>
            </div>
          </form>

          {/* Popular Categories & Queries */}
          <div className="mt-5 flex flex-wrap items-center justify-center gap-2 text-xs">
            <span className="text-[#A3B4C8] font-bold mr-1">Trending Searches:</span>
            {POPULAR_SEARCHES.slice(0, 5).map((term, idx) => (
              <button
                key={idx}
                onClick={() => {
                  setQuery(term);
                  handleSearch(null, term);
                }}
                className="bg-white/10 hover:bg-[#CC6D3D] hover:text-white text-[#A3B4C8] px-3 py-1 rounded-full border border-white/10 transition cursor-pointer"
              >
                {term}
              </button>
            ))}
          </div>

          {/* Recent Searches */}
          {recentSearches.length > 0 && (
            <div className="mt-3 flex items-center justify-center gap-2 text-xs text-[#A3B4C8]">
              <span className="opacity-75 font-semibold">Recent:</span>
              {recentSearches.map((r, i) => (
                <button
                  key={i}
                  onClick={() => {
                    setQuery(r);
                    handleSearch(null, r);
                  }}
                  className="hover:text-white hover:underline cursor-pointer bg-transparent border-none text-[#A3B4C8] text-xs"
                >
                  "{r}"
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Dynamic Category Navigation Bar */}
      <div className="bg-white border-b border-[#D2DCE6] sticky top-16 z-30 shadow-xs">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-2.5 overflow-x-auto flex items-center gap-2 no-scrollbar">
          <button
            onClick={() => {
              setSelectedCategory('All');
              handleSearch(null, query);
            }}
            className={`px-3.5 py-1.5 rounded-full text-xs font-bold whitespace-nowrap transition cursor-pointer ${
              selectedCategory === 'All'
                ? 'bg-[#022E51] text-white shadow-xs'
                : 'bg-slate-100 text-[#022E51] hover:bg-slate-200'
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
              className={`px-3.5 py-1.5 rounded-full text-xs font-semibold whitespace-nowrap transition cursor-pointer flex items-center gap-1.5 ${
                selectedCategory === cat.name
                  ? 'bg-[#022E51] text-white shadow-xs'
                  : 'bg-slate-100 text-[#022E51] hover:bg-slate-200'
              }`}
            >
              <span>{cat.icon || '🛍️'}</span>
              <span>{cat.name}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Security Action Banner */}
      {actionNotice && (
        <div className="max-w-7xl mx-auto px-4 mt-6">
          <div
            className={`p-4 rounded-2xl border flex items-center justify-between shadow-xs ${
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
                <p className="font-bold text-sm">{actionNotice.text}</p>
                <p className="text-xs opacity-90 mt-0.5">
                  Governed deterministically by PayPilot Central Policy Engine.
                </p>
              </div>
            </div>
            {actionNotice.requestId && (
              <button
                onClick={() => navigate('/approvals')}
                className="px-4 py-2 bg-[#CC6D3D] hover:bg-[#B74803] text-white text-xs font-bold rounded-xl shadow-xs transition cursor-pointer whitespace-nowrap"
              >
                Sign on Approvals Screen →
              </button>
            )}
          </div>
        </div>
      )}

      {/* Search Transparency & Multi-Source Intelligence Bar */}
      {searchTelemetry && (
        <div className="max-w-7xl mx-auto px-4 mt-6">
          <div className="bg-white border border-[#D2DCE6] rounded-2xl p-4 shadow-xs flex flex-wrap items-center justify-between gap-3 text-xs">
            <div className="flex items-center gap-2">
              <span className="font-bold text-[#022E51]">Search Execution:</span>
              <span className="text-[#5A6D82]">
                Found <strong>{searchTelemetry.totalFound}</strong> results across{' '}
                <strong>{searchTelemetry.sourcesCount} sources</strong> in {searchTelemetry.timeMs}ms
              </span>
            </div>
            <div className="flex items-center gap-2 flex-wrap">
              <span className="text-[#5A6D82] font-semibold">Active Sources:</span>
              {searchTelemetry.sourcesList.map((src, i) => (
                <span key={i} className="bg-[#A3B4C8]/20 text-[#022E51] font-bold px-2 py-0.5 rounded-md text-[11px]">
                  {src}
                </span>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* AI Intent Summary */}
      {aiSummary && (
        <div className="max-w-7xl mx-auto px-4 mt-4">
          <div className="bg-white border border-[#D2DCE6] rounded-2xl p-4 sm:p-5 shadow-xs">
            <div className="flex items-start gap-3">
              <div className="w-8 h-8 rounded-xl bg-[#022E51] text-white flex items-center justify-center font-bold text-sm shrink-0">
                🤖
              </div>
              <div className="flex-1 text-xs sm:text-sm text-[#022E51] leading-relaxed">
                <div className="flex items-center gap-2 mb-1 flex-wrap">
                  <span className="font-extrabold text-[#022E51]">PayPilot Search Intelligence</span>
                  {detectedIntent?.detected_category && (
                    <span className="text-[11px] bg-[#A3B4C8]/20 text-[#022E51] font-bold px-2 py-0.5 rounded-md">
                      Category: {detectedIntent.detected_category} {detectedIntent.detected_subcategory ? `› ${detectedIntent.detected_subcategory}` : ''}
                    </span>
                  )}
                  {detectedIntent?.detected_brand && (
                    <span className="text-[11px] bg-[#CC6D3D]/10 text-[#CC6D3D] font-bold px-2 py-0.5 rounded-md">
                      Brand: {detectedIntent.detected_brand}
                    </span>
                  )}
                  {detectedIntent?.max_price_paise && (
                    <span className="text-[11px] bg-emerald-100 text-emerald-800 font-bold px-2 py-0.5 rounded-md">
                      Max: ≤ ₹{(detectedIntent.max_price_paise / 100).toLocaleString('en-IN')}
                    </span>
                  )}
                </div>
                <p className="whitespace-pre-line text-[#5A6D82] text-xs sm:text-sm mt-1">{aiSummary}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Results Section */}
      <div ref={resultsRef} className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-6">
        {/* Controls & Filter Bar */}
        <div className="bg-white border border-[#D2DCE6] rounded-2xl p-3 sm:p-4 mb-6 flex flex-wrap items-center justify-between gap-3 shadow-xs">
          <span className="text-xs text-[#5A6D82] font-semibold">
            Showing <strong className="text-[#022E51]">{results.length}</strong> items from accessible sources
          </span>

          <div className="flex flex-wrap items-center gap-2.5">
            {/* Provider Filter */}
            <select
              value={selectedProvider}
              onChange={(e) => {
                setSelectedProvider(e.target.value);
                handleSearch(null, query);
              }}
              className="bg-[#F4F7FA] border border-[#D2DCE6] text-[#022E51] text-xs rounded-xl px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-[#CC6D3D] font-bold cursor-pointer"
            >
              <option value="">All Search Providers</option>
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
              className="bg-[#F4F7FA] border border-[#D2DCE6] text-[#022E51] text-xs rounded-xl px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-[#CC6D3D] font-bold cursor-pointer"
            >
              <option value="relevance">Sort: Relevance / Match</option>
              <option value="price_asc">Price: Low to High</option>
              <option value="price_desc">Price: High to Low</option>
              <option value="rating">Highest Rated</option>
              <option value="discount">Biggest Savings</option>
            </select>

            {/* Max Budget Input */}
            <div className="flex items-center gap-1 bg-[#F4F7FA] border border-[#D2DCE6] rounded-xl px-2.5 py-1">
              <span className="text-xs text-[#5A6D82] font-semibold">Max ₹</span>
              <input
                type="number"
                value={maxPrice}
                onChange={(e) => setMaxPrice(e.target.value)}
                onBlur={() => handleSearch(null, query)}
                placeholder="Budget"
                className="w-20 bg-transparent text-xs text-[#022E51] font-bold focus:outline-none"
              />
            </div>
          </div>
        </div>

        {/* Results Cards */}
        {loading ? (
          <div className="text-center py-20">
            <div className="inline-block animate-spin rounded-full h-10 w-10 border-4 border-[#022E51] border-t-[#CC6D3D] mb-3"></div>
            <p className="text-sm font-bold text-[#022E51]">Searching across internet providers and marketplaces...</p>
            <p className="text-xs text-[#5A6D82] mt-1">Lenskart • Croma • Pepperfry • Tanishq • MakeMyTrip • Web</p>
          </div>
        ) : results.length === 0 ? (
          <div className="bg-white border border-[#D2DCE6] rounded-3xl p-12 text-center shadow-xs">
            <span className="text-4xl">🔍</span>
            <h3 className="text-lg font-bold text-[#022E51] mt-3">No matching results found</h3>
            <p className="text-sm text-[#5A6D82] max-w-md mx-auto mt-1">
              Try adjusting your query keywords or expanding the budget filter.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
            {results.map((product) => (
              <div
                key={product.id}
                className="bg-white border border-[#D2DCE6] rounded-2xl overflow-hidden shadow-xs hover:shadow-md hover:border-[#CC6D3D] transition-all flex flex-col justify-between group"
              >
                <div>
                  {/* Product Image */}
                  <div className="relative h-48 bg-slate-100 overflow-hidden">
                    <img
                      src={product.image_url || 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500&q=80'}
                      alt={product.name}
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                      loading="lazy"
                    />
                    {/* Source Badge */}
                    <div className="absolute top-2.5 left-2.5 flex items-center gap-1.5">
                      <span className="bg-[#022E51]/90 backdrop-blur-xs text-white text-[10px] font-bold px-2 py-0.5 rounded shadow-xs">
                        {product.provider}
                      </span>
                      <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded shadow-xs uppercase tracking-wider ${
                        product.data_source_type === 'LIVE' ? 'bg-emerald-600 text-white' : 'bg-slate-700 text-white'
                      }`}>
                        {product.data_source_type}
                      </span>
                    </div>

                    {/* Discount Tag */}
                    {product.discount_percent && product.discount_percent > 0 && (
                      <div className="absolute top-2.5 right-2.5 bg-[#CC6D3D] text-white text-[11px] font-black px-2 py-0.5 rounded shadow-xs">
                        {product.discount_percent}% OFF
                      </div>
                    )}
                  </div>

                  {/* Card Content */}
                  <div className="p-4">
                    <div className="flex items-center justify-between text-[11px] text-[#5A6D82] mb-1">
                      <span className="font-bold text-[#022E51]">{product.brand || product.merchant}</span>
                      <span className="truncate max-w-[120px]">{product.subcategory || product.category}</span>
                    </div>

                    <h4 className="font-extrabold text-[#022E51] text-sm line-clamp-2 leading-snug group-hover:text-[#CC6D3D] transition">
                      {product.name}
                    </h4>

                    {/* Rating & Availability */}
                    <div className="flex items-center gap-2 mt-1.5 text-xs">
                      <span className="text-amber-500 font-bold">★ {product.rating?.toFixed(1) || '4.5'}</span>
                      <span className="text-[#5A6D82]">({product.rating_count || 120})</span>
                      {product.is_available && (
                        <span className="text-emerald-700 font-semibold text-[10px] bg-emerald-50 px-1.5 py-0.2 rounded ml-auto">
                          In Stock
                        </span>
                      )}
                    </div>

                    {/* Price Block */}
                    <div className="mt-3 flex items-baseline gap-2">
                      <span className="text-lg font-black text-[#022E51]">
                        ₹{product.price_inr.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                      </span>
                      {product.original_price_inr && product.original_price_inr > product.price_inr && (
                        <span className="text-xs text-[#5A6D82] line-through">
                          ₹{product.original_price_inr.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                {/* Card Actions */}
                <div className="p-4 pt-0">
                  <div className="pt-3 border-t border-[#D2DCE6] flex items-center gap-2">
                    <button
                      onClick={() => setSelectedProduct(product)}
                      className="flex-1 py-2 text-xs font-bold text-[#022E51] bg-[#F4F7FA] hover:bg-[#A3B4C8]/30 rounded-xl transition cursor-pointer border border-[#D2DCE6]"
                    >
                      Specifications
                    </button>
                    {product.supports_integrated_checkout ? (
                      <button
                        onClick={() => handleCreatePaymentRequest(product)}
                        className="flex-1 py-2 text-xs font-extrabold text-white bg-[#CC6D3D] hover:bg-[#B74803] rounded-xl shadow-xs transition cursor-pointer"
                      >
                        Select & Pay →
                      </button>
                    ) : (
                      <a
                        href={product.product_url || '#'}
                        target="_blank"
                        rel="noreferrer"
                        className="flex-1 py-2 text-xs font-extrabold text-center text-white bg-[#022E51] hover:bg-[#011E36] rounded-xl transition no-underline shadow-xs"
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

      {/* Adaptive Product Detail & Specs Modal */}
      {selectedProduct && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#022E51]/60 backdrop-blur-xs animate-fade-in">
          <div className="bg-white rounded-3xl max-w-2xl w-full max-h-[90vh] overflow-y-auto shadow-2xl border border-[#D2DCE6]">
            {/* Modal Header */}
            <div className="p-6 border-b border-[#D2DCE6] flex items-start justify-between">
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-xs font-bold text-[#022E51] uppercase tracking-wide">
                    {selectedProduct.provider}
                  </span>
                  <span className="text-[10px] bg-[#A3B4C8]/30 text-[#022E51] font-bold px-1.5 py-0.5 rounded">
                    {selectedProduct.data_source_type}
                  </span>
                </div>
                <h3 className="text-xl font-black text-[#022E51] mt-1">{selectedProduct.name}</h3>
                <p className="text-xs text-[#5A6D82] mt-0.5">Sold / Source: {selectedProduct.merchant}</p>
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
                      <span className="text-2xl font-black text-[#022E51]">
                        ₹{selectedProduct.price_inr.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                      </span>
                      {selectedProduct.original_price_inr && (
                        <span className="text-sm text-[#5A6D82] line-through">
                          ₹{selectedProduct.original_price_inr.toLocaleString('en-IN')}
                        </span>
                      )}
                      {selectedProduct.discount_percent && (
                        <span className="text-xs bg-[#CC6D3D]/10 text-[#CC6D3D] font-black px-2 py-0.5 rounded">
                          {selectedProduct.discount_percent}% OFF
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-[#5A6D82] mt-2 leading-relaxed">
                      {selectedProduct.description}
                    </p>
                  </div>

                  {selectedProduct.delivery_info && (
                    <div className="mt-3 bg-[#F4F7FA] border border-[#D2DCE6] rounded-xl p-2.5 text-xs text-[#022E51] flex items-center gap-2">
                      <span>🚚</span>
                      <span className="font-semibold">{selectedProduct.delivery_info}</span>
                    </div>
                  )}
                </div>
              </div>

              {/* Technical Specifications */}
              {selectedProduct.specifications && Object.keys(selectedProduct.specifications).length > 0 && (
                <div>
                  <h4 className="text-xs font-bold uppercase tracking-wider text-[#5A6D82] mb-2">
                    Verified Specifications & Features
                  </h4>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
                    {Object.entries(selectedProduct.specifications).map(([key, val]) => (
                      <div key={key} className="bg-[#F4F7FA] p-2.5 rounded-xl border border-[#D2DCE6]">
                        <span className="text-[#5A6D82] block text-[10px] font-semibold">{key}</span>
                        <span className="font-bold text-[#022E51]">{String(val)}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Security Policy Notice */}
              <div className="bg-[#022E51]/5 border border-[#022E51]/20 rounded-2xl p-4 text-xs text-[#022E51]">
                <span className="font-extrabold flex items-center gap-1.5 mb-1">
                  🛡️ PayPilot AI Deterministic Policy Security
                </span>
                Autonomous authorization requires evaluation against your active budget limits. No funds can move without explicit user authorization or active pre-cleared policy parameters.
              </div>
            </div>

            {/* Modal Actions */}
            <div className="p-6 bg-[#F4F7FA] border-t border-[#D2DCE6] flex items-center justify-between">
              {selectedProduct.product_url ? (
                <a
                  href={selectedProduct.product_url}
                  target="_blank"
                  rel="noreferrer"
                  className="text-xs font-bold text-[#CC6D3D] hover:text-[#B74803] flex items-center gap-1 no-underline"
                >
                  Inspect Original Source ↗
                </a>
              ) : <div></div>}

              <div className="flex items-center gap-2">
                <button
                  onClick={() => setSelectedProduct(null)}
                  className="px-4 py-2 text-xs font-bold text-[#5A6D82] hover:bg-slate-200 rounded-xl transition cursor-pointer border-none bg-transparent"
                >
                  Cancel
                </button>
                {selectedProduct.supports_integrated_checkout ? (
                  <button
                    onClick={() => handleCreatePaymentRequest(selectedProduct)}
                    className="px-6 py-2.5 bg-[#CC6D3D] hover:bg-[#B74803] text-white font-extrabold text-xs rounded-xl shadow-sm transition cursor-pointer"
                  >
                    Authorize via Policy Engine →
                  </button>
                ) : (
                  <a
                    href={selectedProduct.product_url}
                    target="_blank"
                    rel="noreferrer"
                    className="px-6 py-2.5 bg-[#022E51] hover:bg-[#011E36] text-white font-extrabold text-xs rounded-xl transition no-underline shadow-sm"
                  >
                    Visit External Merchant ↗
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
