# Legora Trust-Architect

**Neuro-Symbolic Legal AI Agent**

Legora Trust-Architect is a cutting-edge legal AI prototype designed to demonstrate **Neuro-Symbolic Artificial Intelligence** in the context of contract review and validation. Unlike standard LLM chat interfaces, Trust-Architect combines the creative power of Large Language Models (Azure OpenAI GPT-4) with the deterministic rigor of symbolic logic (Pydantic/Python) to ensure compliance, reduce hallucinations, and provide verifiable legal analysis.

![Deep Legal Blue](https://placehold.co/1200x400/06060B/6C8EEF?text=Legora+Trust-Architect)

## 🚀 Features

- **Neuro-Symbolic Validation**: Every AI-generated clause is cross-checked against hard coded constraints (jurisdiction rules, forbidden clauses, mandatory liability caps).
- **Stateless Session Management**: JWT-based authentication for secure, transparent API interactions.
- **Client-Side Routing**: Seamless transition between the high-trust Marketing Landing Page (`/`) and the Agent Dashboard (`/app`).
- **Real-time Agent Visualization**: Watch the agent "think" as it moves through states: `Retrieving` -> `Drafting` -> `Validating` -> `Correcting`.
- **modern Design System**:
  - **Landing Page**: Immersive "Dark Mode" aesthetic with glassmorphism and motion effects.
  - **Application**: Professional "Cream" theme (`#F5F5F0`) mimicking high-end legal stationery.

## 🛠️ Tech Stack

### Backend (Python)

- **FastAPI**: High-performance async API framework.
- **Azure OpenAI**: Enterprise-grade LLM integration.
- **Pydantic**: Data validation and symbolic constraints.
- **SlowAPI**: Rate limiting for security.
- **PyJWT**: Secure token-based authentication.

### Frontend (TypeScript)

- **React 19**: Latest React features.
- **Vite**: Blazing fast build tool.
- **Tailwind CSS v4**: Utility-first styling with a custom design system.
- **Framer Motion**: Smooth, complex animations.
- **React Router DOM**: Client-side routing.

## 📦 Installation

### Prerequisites

- Node.js 18+
- Python 3.10+
- Azure OpenAI Service Key

### Backend Setup

1. Navigate to `backend/`:

   ```bash
   cd backend
   ```

2. Create virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Create `.env` file:

   ```env
   AZURE_OPENAI_API_KEY=your_key
   AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
   AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
   API_V1_STR=/api/v1
   PROJECT_NAME="Legora Trust-Architect"
   CORS_ORIGINS=["http://localhost:5173"]
   JWT_SECRET=your_super_secret_key
   API_KEY=your_client_api_key
   ```

5. Run server:

   ```bash
   uvicorn app.main:app --reload
   ```

### Frontend Setup

1. Navigate to `frontend/`:

   ```bash
   cd frontend
   ```

2. Install dependencies:

   ```bash
   npm install
   ```

3. Create `.env` file:

   ```env
   VITE_API_URL=http://localhost:8000/api/v1
   VITE_API_KEY=your_client_api_key
   ```

4. Run development server:

   ```bash
   npm run dev
   ```

## 🌍 Deployment

### 1. Backend (Container Platform)

The backend requires a Python environment with `faiss-cpu` (vector DB). Deploy the `backend/` folder to a container platform like **Render**, **Railway**, or **DigitalOcean App Platform**.

- **Dockerfile**: Provided in `backend/Dockerfile`.
- **Environment Variables**:
  - `AZURE_OPENAI_API_KEY`: Your key.
  - `AZURE_OPENAI_ENDPOINT`: Your endpoint.
  - `JWT_SECRET`: A strong secret string.
  - `CORS_ORIGINS`: Add your Netlify frontend URL (e.g., `["https://your-site.netlify.app"]`).

### 2. Frontend (Netlify)

The frontend is a static React SPA optimized for Netlify.

1. **Connect to Git**: Import this repository on Netlify.
2. **Build Settings**:
   - **Base directory**: `frontend`
   - **Build command**: `npm run build`
   - **Publish directory**: `dist`
3. **Environment Variables** (Netlify Site Configuration):
   - `VITE_API_URL`: The URL of your deployed backend (e.g., `https://legora-backend.onrender.com/api/v1`).
   - `VITE_API_KEY`: The API key you configured in your backend.

**Note**: The project includes a `netlify.toml` file to automatically handle SPA routing (`/* -> /index.html`).

## 🛡️ Security

- **Input Validation**: All inputs validated via Pydantic models.
- **Rate Limiting**: Global and per-endpoint limits to prevent abuse.
- **CORS Policy**: Strict origin checks.
- **Security Headers**: Helmet functionality for HTTP security.

---
*Built by Vinay for the Agentic AI Future.*
