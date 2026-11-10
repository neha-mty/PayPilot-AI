# 🚀 PayPilot AI

**A Secure, Policy-Driven Payment Authorization Platform for AI Agents**

PayPilot AI separates AI intelligence from financial authority. AI agents can discover, recommend, and request purchases, but a centralized backend policy engine and user authorization workflow control whether money can be spent.

---

## Architecture

```
User → React Frontend → FastAPI Backend → AI Assistant → Product Discovery
                                        → Policy Engine → ALLOW / REQUIRE_APPROVAL / BLOCK
                                        → User Approval → Payment Service → Gateway (Simulated/Razorpay)
                                        → Webhook Verification → Transaction Management → Database
```

### Key Security Principles
- **AI agents never directly execute payments** — they can only recommend and request
- **Deterministic policy engine** — pure Python logic, independent of the LLM
- **Backend-only payment credentials** — frontend never sees payment gateway secrets
- **All money values in paise** — ₹180 = 18000 paise, no floating point
- **Webhook signature verification** — never trust frontend payment status
- **Approval binding** — approvals are tied to exact payment details

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React.js, Vite, Tailwind CSS |
| Backend | Python, FastAPI, Pydantic |
| Database | SQLite (dev) / PostgreSQL (prod), SQLAlchemy ORM |
| AI | Google Gemini API, LangChain |
| Payments | Simulated Provider (default) / Razorpay Sandbox |
| Auth | JWT + Argon2 password hashing |

---

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- npm 9+

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd PayPilot-AI
```

### 2. Backend setup
```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate     # Windows
# source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Create .env file from template
copy .env.example .env    # Windows
# cp .env.example .env    # macOS/Linux

# Edit .env and set your JWT_SECRET_KEY (any random string)
# Optionally add GEMINI_API_KEY for AI assistant

# Run the server (auto-seeds demo data)
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend setup
```bash
cd frontend

# Install dependencies
npm install

# Run the dev server (proxies API to backend)
npm run dev
```

### 4. Open the app
- Frontend: http://localhost:5173
- Backend API docs: http://localhost:8000/docs

---

## Environment Variables

Copy `backend/.env.example` to `backend/.env` and configure:

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | Database connection string (SQLite default) |
| `JWT_SECRET_KEY` | Yes | Secret key for JWT tokens — **change this!** |
| `GEMINI_API_KEY` | No | Google Gemini API key (mock AI if empty) |
| `PAYMENT_PROVIDER` | Yes | `simulated` (default) or `razorpay` |
| `RAZORPAY_KEY_ID` | No | Razorpay test key (only if using Razorpay) |
| `RAZORPAY_KEY_SECRET` | No | Razorpay test secret (only if using Razorpay) |

---

## Demo Data

The database is auto-seeded with sample merchants and products:

| Merchant | Category | Verified | Products |
|----------|----------|----------|----------|
| Green Bowl | Food | ✅ Yes | 5 vegetarian meals (₹70–₹180) |
| Daily Bites | Food | ✅ Yes | 5 mixed meals (₹70–₹250) |
| TechZone | Electronics | ✅ Yes | 5 accessories (₹149–₹899) |
| Urban Store | Shopping | ❌ No | 5 daily-use items (₹180–₹450) |

> ⚠️ All merchants and products are **demo/sample data** and do not represent real businesses.

---

## Demo Scenarios

1. **Normal purchase** — Chat: "Find vegetarian food under ₹200" → select → approve → pay
2. **Spending limit violation** — Set max ₹250, request ₹600 item → BLOCK
3. **User approval** — Set approval_required → purchase triggers approval screen
4. **User rejects payment** — Reject on approval screen → no payment created
5. **Unknown merchant** — Urban Store (unverified) → policy blocks or requires approval
6. **Duplicate payment** — Submit same request twice → second blocked
7. **Multiple agents** — Food agent and Shopping agent share the same policy engine

---

## Project Structure

```
PayPilot-AI/
├── frontend/          # React + Vite + Tailwind CSS
│   └── src/
│       ├── components/   # Reusable UI components
│       ├── pages/        # Page-level components
│       ├── services/     # API client
│       └── context/      # React context (auth state)
│
├── backend/           # FastAPI + SQLAlchemy
│   └── app/
│       ├── models/       # SQLAlchemy ORM models
│       ├── schemas/      # Pydantic request/response schemas
│       ├── routes/       # API route handlers
│       ├── services/     # Business logic
│       └── providers/    # Payment provider implementations
│
└── docs/              # Architecture and API documentation
```

---

## ⚠️ Disclaimer

This is a **college prototype** for educational purposes. It does not process real payments. The simulated payment provider is clearly labelled and does not move real money. Razorpay integration uses the sandbox/test environment only.

---

## License

MIT — See LICENSE for details.
