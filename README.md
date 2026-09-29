# Autonomous AI Data Scientist

Agentic AI-powered data analysis, machine learning, and insight-generation platform.
Upload a CSV/Excel dataset and an orchestrated pipeline of specialized agents profiles it,
cleans it, explores it, detects the right ML problem type, trains and compares real
scikit-learn models, explains the results, and generates a downloadable report — all
grounded in actual computed numbers, never fabricated.

---

## 1. Features

- **Dataset upload** — CSV / XLSX / XLS, validated, size-limited, safely stored
- **Dataset Profiler** — schema, dtypes, missing values, duplicates, candidate targets
- **Data Quality center** — quality score, missing-value breakdown, outliers, constant/duplicate columns
- **Data Cleaning** — imputation, dtype correction, duplicate removal — always on a copy, never the original
- **Exploratory Data Analysis** — real distribution stats, correlation analysis, auto-generated findings
- **Visualizations** — histograms, bar charts, correlation heatmap, box plots, scatter plots (computed from real data)
- **ML Lab** — automatic problem detection (classification / regression / clustering), multi-model training,
  leakage-safe pipelines, cross-validation, real metrics, confusion matrix, feature importance
- **AI Data Scientist Chat** — ask questions about your dataset; answers are grounded in computed facts via
  safe tool calls (never arbitrary code execution), with a clear message when there isn't enough evidence
- **Reports** — a 13-section professional report, viewable and downloadable as HTML
- **Unsupervised mode** — no target column? Real KMeans clustering runs instead (k chosen by silhouette score,
  cluster profiles, 2-D projection). A warning is shown before running without a target
- **Downloads** — cleaned dataset (CSV), full analysis export (JSON) and the HTML report
- **ROC curve, confusion matrix and per-model detail view** in the ML Lab
- **ID-like columns** (e.g. `customer_id`) are detected and excluded from modelling automatically
- **Analysis History** — revisit past analyses
- **Works without an LLM key** — profiling, cleaning, EDA, and ML training all work with zero AI configuration;
  only AI-narrated chat/insights require an API key

---

## 2. Architecture

```
Upload → Profiler → Data Quality → Cleaning → Problem Detection → EDA →
Visualization → Model Selection → Training → Evaluation → Explainability →
Insight Generation → Report Generation
```

Each stage is a dedicated **agent** (`backend/app/agents/`) that takes real data and returns a
structured, JSON-serializable result — no hardcoded numbers, no fake metrics. A central
**orchestrator** (`backend/app/orchestrator/pipeline.py`) runs them in sequence and persists real
progress to the database after every stage, so the frontend shows genuine (not simulated) status.

## 3. Technology Stack

| Layer | Technology |
|---|---|
| Frontend | React 18 + Vite + Tailwind CSS |
| Backend | Python 3.10+ + FastAPI |
| Data Science | Pandas, NumPy, Scikit-learn, SciPy, openpyxl |
| AI / LLM | Provider-agnostic abstraction (OpenAI by default), safe tool-calling only |
| Database | SQLite (dev) via SQLAlchemy ORM — swappable to PostgreSQL by changing one env var |
| Model persistence | Joblib |
| Background jobs | FastAPI `BackgroundTasks` (structured so Celery+Redis can replace it later) |

## 4. Folder Structure

```
autonomous-ai-data-scientist/
├── backend/
│   ├── app/
│   │   ├── main.py, config.py, database.py
│   │   ├── models/        # SQLAlchemy ORM models
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── api/           # FastAPI routers
│   │   ├── agents/        # 11 specialized data-science agents
│   │   ├── orchestrator/  # pipeline runner
│   │   ├── llm/           # LLM abstraction + safe chat tools
│   │   ├── core/          # file validation, exceptions, logging
│   │   └── utils/
│   ├── data/{uploads,processed}/
│   ├── models_store/      # saved .joblib models
│   ├── reports_store/     # generated HTML reports
│   ├── tests/             # real pytest suite (15 tests)
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   └── src/{pages,components,api,context,hooks}
└── docs/
```

---

## 5. Installation (Windows)

### Prerequisites
- Python 3.10 or later — [python.org](https://python.org)
- Node.js 18 or later — [nodejs.org](https://nodejs.org)

### Backend setup

Open **Command Prompt** or **PowerShell** in the project folder:

```bat
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Edit `backend\.env` if you want AI chat/insights (optional — see section 8).

### Frontend setup

Open a **second** terminal:

```bat
cd frontend
npm install
```

---

## 6. Running the Application

**Terminal 1 — Backend:**
```bat
cd backend
venv\Scripts\activate
uvicorn app.main:app --reload
```
Backend runs at: **http://localhost:8000**
Interactive API docs: **http://localhost:8000/docs**

**Terminal 2 — Frontend:**
```bat
cd frontend
npm run dev
```
Frontend runs at: **http://localhost:5173**

Open **http://localhost:5173** in your browser.

---

## 7. Using the Application

1. Go to **Datasets** → upload a `.csv`, `.xlsx`, or `.xls` file
2. Review the preview, optionally pick a **target column**
3. Click **Run Autonomous Analysis**
4. Watch the pipeline progress in **ML Lab** (real stage-by-stage status, not simulated)
5. Explore **Data Quality**, **Exploratory Analysis**, and **ML Lab** for full results
6. Ask questions in **AI Data Scientist** chat — answers are grounded in the computed analysis
7. Open **Reports** to view or download the full HTML report
8. Revisit past runs under **Analysis History**

---

## 8. Environment Variables

`backend/.env` (copy from `.env.example`):

```env
APP_ENV=development
DATABASE_URL=sqlite:///./data/app.db

# Optional -- core data analysis works fully without this.
OPENAI_API_KEY=
LLM_MODEL=gpt-4o-mini
LLM_PROVIDER=openai

MAX_UPLOAD_SIZE_MB=50
FRONTEND_ORIGIN=http://localhost:5173
```

**To enable AI chat and AI-narrated insights — free option (Groq):**
1. Create a free key at https://console.groq.com/keys (starts with `gsk_`)
2. In `backend/.env` set:
```env
OPENAI_API_KEY=gsk_your_key_here
LLM_PROVIDER=openai
LLM_BASE_URL=https://api.groq.com/openai/v1
LLM_MODEL=openai/gpt-oss-20b
```
3. Restart the backend. Provider model names change over time — if you get a "model not found"
   error, check the provider's model list and update `LLM_MODEL`.

**Using OpenAI directly (paid):** put your OpenAI key in `OPENAI_API_KEY`, leave `LLM_BASE_URL` empty and
set `LLM_MODEL=gpt-4o-mini`.

Without a key, the app still works fully — profiling, cleaning, EDA, ML training, and the report
all run normally. Chat and insights fall back to a deterministic, clearly-labeled rule-based mode
that reads the same underlying computed facts.

---

## 9. Running Tests

```bat
cd backend
venv\Scripts\activate
pytest tests/ -v
```

The suite includes real unit tests (profiler, cleaning, ML training) and a full end-to-end
integration test that uploads a dataset, runs the entire pipeline, chats with the result, and
downloads the report — all 15 tests pass against the actual code (not mocked).

---

## 10. Troubleshooting

| Problem | Solution |
|---|---|
| `ModuleNotFoundError` on backend start | Make sure the venv is activated (`venv\Scripts\activate`) before `pip install` |
| Frontend can't reach backend / CORS errors | Confirm backend is running on port 8000 and `FRONTEND_ORIGIN` in `.env` matches your frontend URL |
| "Unsupported file type" on upload | Only `.csv`, `.xlsx`, `.xls` are accepted |
| Analysis stuck on a stage | Check the backend terminal for the logged error; the `error_message` field in `/api/analysis/{id}/status` also explains failures |
| AI chat says AI phrasing is unavailable | Expected without `OPENAI_API_KEY` — you're seeing the grounded rule-based fallback, not a bug |
| Port already in use | Stop other processes on 8000/5173, or run `uvicorn app.main:app --reload --port 8001` and update the frontend's `BASE_URL` in `src/api/client.js` |

---

## 11. Deployment

Deployment specifics depend on your target host; the app was built to make this straightforward:

- **Backend**: any host that runs a WSGI/ASGI Python app (Render, Railway, Fly.io, a VPS with
  `uvicorn`/`gunicorn`). Set `DATABASE_URL` to a PostgreSQL connection string for production —
  no code changes needed, only the environment variable.
- **Frontend**: `npm run build` produces a static `dist/` folder deployable to Vercel, Netlify,
  or any static host. Update `BASE_URL` in `frontend/src/api/client.js` to your deployed backend URL.
- **Environment variables**: set `OPENAI_API_KEY`, `DATABASE_URL`, and `FRONTEND_ORIGIN` on your
  hosting platform's environment/secrets configuration — never commit them.
- **File storage**: for production, point `UPLOAD_DIR`/`MODELS_DIR`/`REPORTS_DIR` at a persistent
  volume or object storage, since some hosts have ephemeral filesystems.

---

## 12. Design Notes / Honesty About Scope

This is a genuinely functional full-stack platform — every metric, chart, and report section is
computed from the uploaded data, not hardcoded. To keep it realistically buildable and runnable,
a few pragmatic choices remain versus the most exhaustive possible spec:

- Background jobs use FastAPI's built-in `BackgroundTasks` rather than Celery+Redis (the code is
  structured so that swap is straightforward later).
- The AI chat is grounded via structured tool-calling over stored analysis JSON, not a vector
  database — genuinely accurate for this use case (tabular analysis results are already
  structured), but not a general-purpose document-embedding RAG system.
- No dedicated CI pipeline config (e.g. GitHub Actions) is included, though `pytest` and
  `npm run build` both run cleanly and can be wired into one directly.

**Implemented in this pass, on top of the initial build:**
- **SHAP explainability** for tree-based models (Random Forest, Gradient Boosting,
  HistGradientBoosting, Decision Tree), with an automatic, honestly-labeled fallback to native
  `feature_importances_`/`coef_` for model types SHAP doesn't cover or if SHAP isn't installed
- **Toast notifications** for upload success/failure and analysis completion/failure
- **Mobile sidebar drawer** (hamburger menu on small screens) alongside the desktop sidebar
- **Breadcrumb navigation** in the top bar
- **Docker deployment**: `backend/Dockerfile`, `frontend/Dockerfile` + nginx config,
  root `docker-compose.yml`, and `docs/deployment.md` covering both single-VPS and
  hosted-backend/static-frontend deployment paths
- Frontend API URL is now environment-configurable (`VITE_API_BASE_URL`) instead of hardcoded,
  so the same build works locally and once deployed

Everything else in the original spec (all 11 agents, the full orchestrator, safe tool-calling chat,
quality/EDA/ML pages, dark/light mode, report generation, history) is implemented and tested —
**17/17 backend tests pass** and the frontend builds cleanly with zero errors.
