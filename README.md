# Legora Trust-Architect

## Neuro-Symbolic Legal AI Agent (Test it live: [Live Demo](https://legorafrontend.netlify.app/))

Legora Trust-Architect is a legal AI prototype that demonstrates **Neuro-Symbolic Artificial Intelligence** for contract review and validation. It combines Large Language Models (Azure OpenAI GPT-4) with deterministic symbolic logic (Pydantic/Python) to ensure compliance, reduce hallucinations, and provide verifiable legal analysis.

## 🚀 Features

- **Neuro-Symbolic Validation**: AI-generated clauses are cross-checked against symbolic constraints (jurisdiction rules, forbidden clauses, mandatory liability caps).
- **Stateless Session Management**: JWT-based authentication for secure, transparent API interactions.
- **Real-time Agent Visualization**: Watch the agent think as it moves through states: `Retrieving` → `Drafting` → `Validating` → `Correcting`.
- **Dual Design System**:
  - **Landing Page**: Immersive dark mode aesthetic with glassmorphism and motion effects.
  - **Application**: Professional cream theme mimicking high-end legal stationery.

## 🛠️ Tech Stack

### Backend (Python)

- **FastAPI** — High-performance async API framework
- **Azure OpenAI** — Enterprise-grade LLM integration
- **Pydantic** — Data validation and symbolic constraints
- **SlowAPI** — Rate limiting
- **PyJWT** — Token-based authentication

### Frontend (TypeScript)

- **React 19** — Latest React features
- **Vite** — Fast build tool
- **Tailwind CSS v4** — Utility-first styling
- **Framer Motion** — Smooth animations
- **React Router DOM** — Client-side routing

## 📦 Getting Started

### Prerequisites

- Node.js 18+
- Python 3.10+
- Azure OpenAI API Key

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

Create `backend/.env` (see `backend/.env.example`):

```env
AZURE_OPENAI_API_KEY=your_key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
JWT_SECRET=your_secure_random_secret
API_KEY=your_api_key
CORS_ORIGINS=http://localhost:5173
```

```bash
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
```

Create `frontend/.env`:

```env
VITE_API_KEY=your_api_key
```

```bash
npm run dev
```

The frontend dev server proxies `/api` requests to `http://localhost:8000` automatically via Vite.

## 🌍 Deployment

### Backend (Container Platform)

The backend is containerized via Docker. Deploy to any container platform (Render, Railway, DigitalOcean, etc.).

**Required environment variables:**

| Variable | Description |
|---|---|
| `AZURE_OPENAI_API_KEY` | Your Azure OpenAI API key |
| `AZURE_OPENAI_ENDPOINT` | Your Azure OpenAI endpoint URL |
| `AZURE_OPENAI_DEPLOYMENT_NAME` | Model deployment name (e.g., `gpt-4o`) |
| `JWT_SECRET` | A strong random string for signing tokens |
| `API_KEY` | API key for authenticating frontend requests |
| `CORS_ORIGINS` | Allowed origins (e.g., `https://your-frontend.netlify.app`) |

A `render.yaml` blueprint is included for one-click Render deployment.

### Frontend (Static Host)

The frontend is a static React SPA. Deploy to any static host (Netlify, Vercel, Cloudflare Pages, etc.).

A `netlify.toml` is included with build settings and SPA routing rules.

**Required environment variables (set at build time):**

| Variable | Description |
|---|---|
| `VITE_API_URL` | Your deployed backend URL (e.g., `https://your-backend.onrender.com`) |
| `VITE_API_KEY` | The same API key configured on the backend |

## 🛡️ Security

- **Input Validation**: All inputs validated via Pydantic models.
- **Rate Limiting**: Global and per-endpoint limits to prevent abuse.
- **CORS Policy**: Configurable origin allowlist.
- **API Key Auth**: All API routes require `X-API-Key` header.
- **JWT Tokens**: Short-lived access tokens with refresh rotation.
- **Production Safety**: Startup check prevents running with default secrets.
- **Error Handling**: Generic error messages in production — no stack traces leaked.

## 🐳 Local Development (Docker)

```bash
docker compose up --build
```

This starts both the backend (port 8000) and frontend (port 5173) with hot reload.

---

*Built by Vinay for the Agentic AI Future.*
