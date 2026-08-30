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

## Local setup (running frontend and backend as two separate dev servers)

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

All routes live under `/api` (e.g. `http://localhost:8000/api/auth/login`).
Interactive docs: `http://localhost:8000/docs`

### Frontend
```bash
cd apps/web
npm install
cp .env.local.example .env.local
npm run dev
```
Visit `http://localhost:3000`. The frontend calls `${NEXT_PUBLIC_API_URL}/api/...`
— leave `NEXT_PUBLIC_API_URL` unset for the combined-deployment case (relative
`/api` calls through nginx), or set it to `http://localhost:8000` for local dev
against a separately-running backend.

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

I can't create a live URL for you from here — deployment needs your own hosting
account, and this environment has no network access to Render/Vercel/etc. But
the repo is now a **single combined deployment**: one Docker image runs the
Next.js frontend, the FastAPI backend, and an nginx reverse proxy together, so
you get **one URL** for the whole app instead of juggling two separate services
and CORS config.

I tested this exact setup end-to-end in the sandbox before shipping it (backend
+ frontend + nginx all running together, verified the compiled frontend bundle
calls `/api/*` same-origin, confirmed login/job-listing/etc. work through the
single proxied port) — so this should deploy clean.

### Deploy to Render (recommended — reads `render.yaml` automatically)
1. Push this repo to GitHub:
   ```bash
   git remote add origin https://github.com/<your-username>/vira.git
   git push -u origin master
   ```
2. In Render: **New → Blueprint**, point it at your repo. It builds the root
   `Dockerfile` (frontend + backend + nginx combined) automatically.
3. Once live, set `FRONTEND_ORIGIN` in the Render dashboard to the same URL
   Render gives you (e.g. `https://vira-app.onrender.com`) — needed for the
   rare cross-origin case (local dev hitting the deployed API directly).
4. That's it — demo data seeds automatically on first boot. Visit the URL and
   log in with the demo accounts printed in the backend logs (or see below).

### Alternative: Railway or Fly.io
Both read a Dockerfile the same way. Point either at this repo's root
`Dockerfile`, set the `PORT` env var if the platform doesn't inject one
automatically (Render/Railway/Fly all do by default), and deploy.

**Free-tier note:** Render's free tier spins down when idle (cold-start delay
on first request after inactivity) and the default SQLite file resets on
redeploy. Fine for a demo/portfolio link. For anything you want to persist,
add a managed PostgreSQL instance and point `DATABASE_URL` at it — no code
changes needed, just the env var.

### If you specifically want the frontend on Vercel
Vercel doesn't run a persistent Python process, so the combined single-service
approach above doesn't fit Vercel directly. If you'd rather use Vercel for the
frontend specifically, deploy the backend separately (Render, using
`apps/api/Dockerfile`) and the frontend on Vercel with `NEXT_PUBLIC_API_URL`
pointing at the backend's URL — this was the two-service setup from an earlier
version of this README, still fully supported, just more moving parts.

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
