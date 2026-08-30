# VIRA — Virtual Intelligent Recruitment Assistant

**"Skills Over Background. Opportunities for Everyone."**

An AI-assisted recruitment platform: candidates are matched to roles by demonstrated
skill with a fully transparent, explainable score — and when they're not a fit yet,
VIRA hands them a specific **Growth Path** instead of a bare rejection.

This repo is a working, runnable implementation of Phases 2–8 of the original product
brief (see `docs/VIRA-Phase1-Architecture.md` for the full blueprint). It is a genuine
prototype, not a finished commercial product — see **Scope & Honest Limitations** below.

---

## What's implemented

### Backend (`apps/api`) — FastAPI + SQLAlchemy (async) + SQLite/PostgreSQL
- JWT auth with role-based access (candidate / recruiter / admin)
- Resume upload with skill extraction (mock parser, provider-swappable)
- **Explainable AI job matching engine** — every score ships with a 4-part breakdown
  and a plain-language explanation, never a bare number
- **VIRA Growth Path** — the "second-chance hiring" system: strengths, skills to
  improve, ordered next steps, and match-progress tracking over time
- Adaptive assessment engine (aptitude / technical / scenario rounds) with
  transparent rubric scoring
- **VIRA CALL** — a scripted-but-adaptive AI interview flow with contextual follow-up
  questions and a structured (non-emotion-detecting) summary
- Recruiter job creation with must-have vs. preferred skill weighting
- Admin endpoints: company verification, audit logs, platform analytics
- Full Responsible AI guardrails baked into the schema and every AI response
  (no protected-attribute fields exist on candidate/job models; every recommendation
  carries a human-review disclaimer)
- 5 passing pytest tests covering auth, job creation, and the matching/growth-path flow

### Frontend (`apps/web`) — Next.js 14 (App Router) + TypeScript + Tailwind
- Landing page with a custom design system (see `docs/design-system.md`) and a
  signature visual — **"The Route"** — a topographic path illustrating a candidate's
  journey from current skills to a target role, used instead of a generic AI orb
- Login / register (candidate or recruiter)
- Job listing + job detail with live, explainable match-score breakdown
  ("Why this match score?")
- Candidate dashboard: career overview, applications, resume upload with live
  skill-detection feedback
- Growth Path page: strengths, skills to improve, ordered next steps
- Recruiter dashboard + job creation wizard (must-have vs. preferred skill tagging)
- Builds clean with zero TypeScript errors across all 10 routes

---

## Scope & honest limitations

- **VIRA CALL voice interview** ships with a real question-flow/state-machine and
  backend, but speech-to-text/text-to-speech are mocked — wiring in a real speech
  provider requires your own API key (see `apps/api/.env.example`).
- **Resume parsing** is a deterministic keyword/regex extractor for demo purposes,
  not a production NLP pipeline. `app/ai/resume_parser.py` defines a clean interface
  (`BaseResumeParser`) so a real LLM- or NER-based parser can be dropped in.
  PDF/DOCX files are accepted and stored, but only `.txt` is actually decoded for
  extraction in this build.
- **Deployment**: Dockerfiles and `.env.example` files are provided, but nothing has
  been deployed to a live cloud environment on your behalf — you'll need your own
  Vercel/hosting accounts and a managed Postgres instance for production.
- **Not implemented**: admin frontend UI (backend endpoints exist), notifications
  frontend, candidate comparison view, AI job-description assistant, and a few of
  the more marginal features from the original 38-section brief. The core
  differentiators (explainable matching, growth path, adaptive assessments, VIRA
  CALL, responsible AI guardrails) are all real and working.

---

## Local setup

### Backend
```bash
cd apps/api
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m app.seed        # creates demo accounts + sample jobs
uvicorn app.main:app --reload --port 8000
```
Demo logins (printed by the seed script):
- Candidate: `priya.candidate@viradmo.dev` / `DemoPass123!`
- Recruiter: `arjun.recruiter@northwindanalytics.dev` / `DemoPass123!`

API docs: `http://localhost:8000/docs`

### Frontend
```bash
cd apps/web
npm install
cp .env.local.example .env.local
npm run dev
```
Visit `http://localhost:3000`.

> Note: `app/layout.tsx` uses system font fallbacks rather than `next/font/google`,
> because this sandbox has no outbound access to Google Fonts. If you're deploying
> somewhere with normal internet access, swap back to `next/font/google` for
> Space Grotesk / Inter / IBM Plex Mono for a closer match to the intended design —
> the Tailwind config already references those family names.

### Tests
```bash
cd apps/api
pytest tests/ -v
```

---

## Deploying your own live link

I can't create a live URL for you from here — Vercel deployment needs your own
account, and this environment has no network access to vercel.com. But the repo
is ready for a genuine one-click deploy. Two pieces, deployed separately:

### 1. Frontend → Vercel (~2 minutes)

**Option A — push to GitHub, then import (recommended):**
```bash
# from the unzipped vira/ folder — it's already a git repo with one commit
git remote add origin https://github.com/<your-username>/vira.git
git push -u origin master
```
Then in Vercel: **Add New Project → Import** your `vira` repo →
set **Root Directory** to `apps/web` → deploy.

**Option B — deploy straight from your machine, no GitHub needed:**
```bash
cd apps/web
npx vercel        # first run: log in, link/create project
npx vercel --prod # deploy to production
```

Either way, after the first deploy, add an environment variable in the Vercel
project settings:
```
NEXT_PUBLIC_API_URL = <your backend URL from step 2>
```
then redeploy (Vercel → Deployments → ⋯ → Redeploy) so the frontend picks it up.

### 2. Backend → Render (or Railway / Fly — any Docker host works)

A `render.yaml` blueprint is included at the repo root.
1. Push the same repo to GitHub (see above).
2. In Render: **New → Blueprint**, point it at your repo. It'll read `render.yaml`
   and build `apps/api` from its `Dockerfile` automatically.
3. Once deployed, copy the Render URL (e.g. `https://vira-api.onrender.com`).
4. Set that as `NEXT_PUBLIC_API_URL` in Vercel (step 1), and set `FRONTEND_ORIGIN`
   in Render to your Vercel URL so CORS allows it.
5. SSH/shell into the Render service (or run one-off) to seed demo data:
   `python -m app.seed`.

**Free-tier note:** Render's free tier spins down when idle (cold-start delay on
first request) and its SQLite file resets on redeploy. For anything beyond a demo,
attach a Render PostgreSQL instance and point `DATABASE_URL` at it — no code
changes needed, just the env var.

---

## Repo structure
```
vira/
├── apps/
│   ├── api/     # FastAPI backend
│   └── web/     # Next.js frontend
├── docs/
│   ├── VIRA-Phase1-Architecture.md
│   └── design-system.md
└── README.md
```
