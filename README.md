# 🚀 PayPilot AI

**Universal AI Marketplace Discovery, Comparison & Secure Policy-Driven Purchasing**

PayPilot AI separates AI purchasing intelligence from financial authority. Users can search for practically **ANY** product or service across multiple configured marketplaces using natural language. PayPilot dynamically identifies the category, queries providers in parallel, compares prices and features, and enforces deterministic spending-policy guardrails before any money can be spent.

---

## 🌟 Major Highlights: Universal Marketplace Architecture

1. **Universal Search Interface**
   - Natural-language query understanding for any category:
     - *"Find sunglasses from Lenskart under ₹2,000"*
     - *"Find a comfortable office chair under ₹5,000"*
     - *"Find gold earrings under ₹10,000"*
     - *"Find a laptop for programming under ₹60,000"*
     - *"Find the cheapest flight from Kolkata to Delhi"*
     - *"Find a hotel in Darjeeling under ₹3,000 per night"*
     - *"Find a good telescope under ₹10,000"*
     - *"Vegetarian food thali under ₹200"*

2. **Extensible 18+ Category & Subcategory Hierarchy**
   - **A. Food and groceries**: Restaurants, vegetarian & non-veg meals, groceries
   - **B. Fashion and clothing**: Sarees, kurtas, western wear, Nike running shoes
   - **C. Jewellery and accessories**: 18KT gold floral earrings, Titan watches, sunglasses
   - **D. Electronics and technology**: Dell laptops, Samsung smartphones, wireless earbuds
   - **E. Furniture and home furnishing**: Ergonomic mesh chairs, Sheesham compact sofas
   - **F. Home appliances**: Smart inverter washing machines, 5-star refrigerators
   - **G. Beauty, cosmetics and personal care**
   - **H. Books, education and stationery**
   - **I. Sports, fitness and outdoor**
   - **J. Automotive and mobility**
   - **K. Travel and accommodation**: Domestic flights, mountain boutique stays
   - **L. Transportation and local services**
   - **M. Entertainment and experiences**
   - **N. Health and wellness products**
   - **O. Pet supplies**
   - **P. Art, hobbies and collectibles**: Astronomical telescopes, musical keyboards
   - **Q. Industrial and professional products**: Automatic sewing machines
   - **R. Services and subscriptions**
   - **S. Specialty & Dynamically Discovered Categories**: Unforeseen items mapped dynamically

3. **Modular Marketplace Provider Registry**
   - `LenskartMarketplaceAdapter` (Eyewear, sunglasses, computer glasses)
   - `FurnitureMarketplaceAdapter` (Pepperfry ergonomic chairs, compact sofas)
   - `ElectronicsMarketplaceAdapter` (Croma computing, laptops, smartphones)
   - `JewelleryMarketplaceAdapter` (Tanishq gold earrings, Titan watches)
   - `TravelMarketplaceAdapter` (MakeMyTrip flights & hotels)
   - `RetailAppliancesMarketplaceAdapter` (Amazon/Myntra fashion, appliances, food)
   - `DynamicCategoryMarketplaceAdapter` (Telescopes, sewing machines, smart security)
   - `InternalCatalogAdapter` (PayPilot authoritative local database)

4. **New Fintech UI Design System**
   - **Primary Blue (`#2563EB`, `#1D4ED8`)**: Navigation, branding, primary actions
   - **Grey Palette (`#F8FAFC`, `#FFFFFF`, `#E2E8F0`, `#64748B`, `#0F172A`)**: Clean cards, borders, typography
   - **Orange Accent (`#F97316`, `#EA580C`)**: High-priority authorization buttons, pending approvals, discounts

5. **Inviolable Security Architecture**
   - Deterministic policy engine: `ALLOW`, `REQUIRE_APPROVAL`, `BLOCK`
   - Exact-transaction binding with user signatures
   - Backend-only payment credentials (HMAC-SHA256 signature verification)
   - Full immutable audit log for college evaluation and compliance

---

## 🏗️ Architecture

```
User → Universal Search Bar (React)
    → Natural-Language Query
    → FastAPI Backend (/api/marketplace/search, /api/assistant/chat)
    → NLP Intent & Category Classifier (Dynamic Category + Subcategory + Budget Extraction)
    → Marketplace Provider Manager (Parallel Asynchronous Querying across Lenskart, Croma, Pepperfry, Tanishq, etc.)
    → Unified Normalized Result Schema (Price, Brand, Specifications, Data Source Type)
    → User Selects Product
    → Deterministic Policy Engine (ALLOW / REQUIRE_APPROVAL / BLOCK)
    → User Signs Authorization (Approvals Screen)
    → Payment Orchestrator (Simulated Sandbox / Razorpay)
    → HMAC-SHA256 Webhook Verification
    → Immutable Audit Log & Transaction Ledger
```

---

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.11+ (Python 3.13 supported)
- Node.js 18+ and npm

### 2. Backend Setup
```bash
cd backend
python -m uvicorn app.main:app --port 8000
```
- API Docs: `http://localhost:8000/docs`
- Health check: `GET http://localhost:8000/health`

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
- Open `http://localhost:5173` in your browser!

### 4. Running Tests
```bash
cd backend
python -m pytest tests/ -v
```
All 15 tests covering auth, policy engine, marketplace search, and e2e scenarios pass cleanly.
