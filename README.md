# modLRN — AI-powered Adaptive Learning Platform

FastAPI + React + MongoDB with optional Gemini AI and Google OAuth.

---

## Features

- AI question generation (Gemini; graceful fallbacks if not configured)
- JWT auth with optional Google OAuth and face login
- Coding platform: problem generation, submissions, analytics
- Code execution APIs (sandboxed, multi-language)
- MongoDB persistence and health checks

---

## Project Structure

```text
ML_PRJ/
├─ backend/                 # FastAPI backend
│  ├─ main.py               # App entry
│  ├─ database.py           # Mongo connection (Motor)
│  ├─ models/               # Pydantic models & schemas
│  ├─ routers/              # API routers
│  ├─ services/             # Code exec & Gemini helpers
│  ├─ utils/                # Auth helpers
│  └─ requirements.txt
├─ src/                     # React frontend (Vite + TS)
│  ├─ components/ pages/ utils/ ...
├─ public/models/           # Face recognition models
├─ start-backend.bat        # Convenience scripts
├─ start-frontend.bat
└─ README.md
```

---

## Prerequisites

- Python 3.10+ (3.13 supported)
- Node.js 18+
- MongoDB

Optional:
- Gemini API key (question gen, AI feedback)
- Google OAuth credentials

---

## Quick Start

Backend (FastAPI):

```bash
cd backend
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
# source venv/bin/activate

pip install -r requirements.txt

# Create .env in backend/ (see below)
python main.py   # http://localhost:5001
```

Frontend (React + Vite):

```bash
npm install
# Optionally set VITE_API_BASE_URL (defaults to http://localhost:5001)
npm run dev   # http://localhost:5173
```

Windows helpers:

```bash
start-backend.bat    # Starts backend on http://localhost:5001
start-frontend.bat   # Starts frontend on http://localhost:5173
```

---

## Configuration

Environment (.env in `backend/`):

```env
# Database
MONGO_URI=mongodb://localhost:27017
DB_NAME=modlrn

# Auth
SECRET_KEY=change-me-in-production

# Google OAuth (optional)
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GOOGLE_REDIRECT_URI=http://localhost:5001/auth/google/callback

# Gemini (optional)
GEMINI_API_KEY=

# CORS/frontend
FRONTEND_URL=http://localhost:5173
```

---

---

## Key Endpoints

- Auth: `/auth/register`, `/auth/login`, `/auth/google`, `/auth/google/callback`, `/auth/face`, `/auth/register-face`, `/auth/status`
- Questions: `/db/questions` (Gemini gen), `/db/questions/{topic}`
- Coding: `/api/coding/problems*`, `/api/coding/execute`, `/api/coding/submit`, `/api/coding/analytics`
- Code Exec service: `/api/execute/execute`, `/api/execute/test`, `/api/execute/languages`
- Health: `/api/health`, `/api/test-db`

---

## Repo Hygiene

Removed from versioned sources (regenerate locally as needed):
- `node_modules/`
- `backend/venv/`
- Python `__pycache__/`

Also keep secrets local: `.env`, `*.local`, and logs are ignored via `.gitignore`.

Use `npm install` (frontend) and `pip install -r backend/requirements.txt` (backend) to restore dependencies.

---

## Troubleshooting

- Mongo: verify `MONGO_URI`, `DB_NAME`, and MongoDB service.
- 401: ensure `Authorization: Bearer <token>`; login again.
- CORS: update `allow_origins` in `backend/main.py` for your frontend domain.
- Windows C++ execution: ensure build tools; admin rights may be required.

---

## License

MIT

---

## Authors

Rahul V S, Sharvesh Ram K S, Adhithya R, Yukesh D

<p align="center"><b>Made with ❤️ for learners, by learners.</b></p>
