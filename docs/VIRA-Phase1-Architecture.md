# VIRA — Phase 1: System Architecture & Product Blueprint

*Virtual Intelligent Recruitment Assistant — "Skills Over Background. Opportunities for Everyone."*

---

## 1. Technology Decisions & Justification

| Layer | Choice | Why |
|---|---|---|
| Frontend | Next.js 14 (App Router) + TypeScript | SSR for fast landing/job pages, file-based routing fits candidate/recruiter/admin sections cleanly, huge ecosystem |
| Styling | Tailwind CSS + shadcn/ui | Fast, consistent design tokens; shadcn gives accessible unstyled primitives we can fully re-skin (avoids "generic AI app" look) |
| Motion | Framer Motion | Used sparingly — orb animation, page transitions, skeletons |
| Backend | FastAPI (Python) | Async, typed, auto OpenAPI docs, natural fit for the AI/ML modules (resume parsing, matching, assessment scoring) |
| DB | PostgreSQL | Relational integrity across Users/Jobs/Assessments/Applications; JSONB columns for flexible AI output (explanations, skill vectors) |
| ORM | SQLAlchemy 2.0 (async) + Alembic | Migrations, typed models |
| Auth | JWT (access + refresh) via FastAPI, bcrypt hashing, RBAC middleware | Stateless, scales across services; roles = candidate / recruiter / admin |
| AI layer | Modular Python services behind interfaces (`ResumeParser`, `MatchEngine`, `AssessmentEngine`, `InterviewAssistant`) | Each has a **mock mode** (deterministic, no key needed) and a **provider mode** (pluggable — e.g., an LLM API for parsing/matching, a speech provider for VIRA CALL) so the app runs fully offline in dev/demo |
| File storage | Local disk in dev behind an abstraction (`StorageService`), swappable for S3-compatible storage in prod | Never blocks local development on cloud credentials |
| Deployment | Frontend → Vercel; Backend → any container host (Render/Fly/Railway) with Docker; DB → managed Postgres | Matches spec, keeps infra vendor-flexible |

**Practical note on this environment:** I can build and preview the **Next.js frontend directly** here. The **FastAPI backend** I'll generate as real, runnable code with instructions to run locally (`uvicorn`) — I can't host a live Postgres/cloud backend for you from this chat. Voice (speech-to-text/text-to-speech) and any external AI matching will ship in **mock mode by default**, with a clearly documented `.env` swap to a real provider.

---

## 2. Folder Structure

```
vira/
├── apps/
│   ├── web/                      # Next.js frontend
│   │   ├── app/
│   │   │   ├── (marketing)/      # landing page, how-it-works, why-vira
│   │   │   ├── (auth)/           # login, register
│   │   │   ├── candidate/        # dashboard, jobs, growth-path, interview room
│   │   │   ├── recruiter/        # dashboard, job wizard, candidate intelligence
│   │   │   └── admin/            # moderation, audit logs, analytics
│   │   ├── components/
│   │   │   ├── ui/                # design system primitives
│   │   │   ├── vira/              # AI orb, VIRA chat, explanation panels
│   │   │   └── charts/
│   │   └── lib/                   # api client, auth helpers, types
│   │
│   └── api/                       # FastAPI backend
│       ├── app/
│       │   ├── core/               # config, security, deps
│       │   ├── models/             # SQLAlchemy models
│       │   ├── schemas/            # Pydantic schemas
│       │   ├── routers/            # auth, resumes, jobs, matching, assessments, vira, admin
│       │   ├── services/
│       │   │   ├── resume_parser/
│       │   │   ├── match_engine/
│       │   │   ├── assessment_engine/
│       │   │   └── interview_assistant/
│       │   └── ai/                 # provider interfaces + mock implementations
│       ├── alembic/
│       └── tests/
│
├── packages/
│   ├── ui/                        # shared design tokens (used by web)
│   └── shared/                    # shared TS types mirroring API schemas
│
├── docs/                          # architecture, API reference, responsible-AI policy
├── docker/
├── docker-compose.yml
└── README.md
```

---

## 3. Database Schema (core entities)

**Identity & orgs**
- `users` (id, email, password_hash, role[candidate|recruiter|admin], created_at)
- `candidate_profiles` (user_id, headline, location, skills_summary, profile_completion)
- `companies` (id, name, verified_status, industry)
- `recruiter_profiles` (user_id, company_id, title)

**Resume & skills**
- `resumes` (id, candidate_id, file_url, parsed_status, raw_text)
- `skills` (id, name, category) — taxonomy table
- `candidate_skills` (candidate_id, skill_id, source[resume|assessment|manual], proficiency)
- `job_skills` (job_id, skill_id, requirement_type[must_have|preferred])

**Jobs & applications**
- `jobs` (id, company_id, title, description, responsibilities, status, created_at)
- `applications` (id, job_id, candidate_id, status, match_score, applied_at)

**Assessments**
- `assessments` (id, job_id, round_type[aptitude|technical|scenario], config_json)
- `questions` (id, assessment_id, type, prompt, rubric_json)
- `assessment_attempts` (id, assessment_id, candidate_id, status, started_at, submitted_at)
- `assessment_results` (attempt_id, score, breakdown_json, feedback_text)

**Interviews (VIRA CALL)**
- `interview_sessions` (id, application_id, status, started_at, ended_at)
- `interview_responses` (session_id, question_text, transcript, follow_up_of)

**AI transparency & growth**
- `ai_recommendations` (id, subject_type, subject_id, summary, explanation_json, created_at)
- `skill_gap_reports` (candidate_id, job_id, missing_skills_json, generated_at)
- `growth_plans` (candidate_id, current_match, target_job_id, steps_json, progress)

**System**
- `notifications` (user_id, type, message, read_at)
- `audit_logs` (actor_id, action, entity_type, entity_id, metadata_json, created_at)

All tables: `id` PK (UUID), `created_at`/`updated_at` timestamps, FKs indexed.

---

## 4. API Architecture (representative)

```
POST   /auth/register            /auth/login          /auth/logout
GET    /candidates/me             PATCH /candidates/me
POST   /resumes/upload            GET /resumes/{id}
GET    /jobs                      POST /jobs (recruiter)      GET /jobs/{id}
POST   /applications               GET /applications/{id}
POST   /matching/analyze          GET /matching/{application_id}/explanation
GET    /assessments               POST /assessments/start     POST /assessments/submit
POST   /interviews/start          POST /interviews/{id}/respond   GET /interviews/{id}/summary
POST   /vira/chat                 POST /vira/analyze-resume    POST /vira/interview
GET    /admin/audit-logs          POST /admin/companies/{id}/verify
```
Every response involving an AI judgment includes an `explanation` object — never a bare score.

---

## 5. UI Design System (starting tokens)

- **Palette**: deep indigo (`#1E1B4B`) as primary, warm teal accent (`#0FB5AE`) for "growth/opportunity" moments, soft amber for "in-progress," slate neutrals for text/surfaces. Avoids the default purple-gradient "AI startup" cliché.
- **Type**: a humanist sans (e.g., Inter or General Sans) for UI text, slightly larger line-height for accessibility.
- **Shape language**: 12–16px radii, soft layered shadows, no harsh borders.
- **VIRA presence**: a single recurring abstract orb motif (not a face/avatar) used consistently across chat, interview room, and loading states — calm pulsing, not "sci-fi AI."
- **Core components to build**: Button, Input, Card, Badge, Modal, Dropdown, Tabs, Tooltip, ProgressBar, Skeleton, Toast, EmptyState, ErrorState, ScoreBreakdown, ExplanationPanel.

---

## 6. Implementation Plan (phased, matching your original brief)

| Phase | Deliverable | Runs in this chat? |
|---|---|---|
| 2 | DB schema as SQLAlchemy models + Alembic migration | Yes — real files |
| 3 | Backend auth (register/login/JWT/RBAC) + core routers | Yes — real, runnable FastAPI |
| 4 | Frontend design system + landing page | Yes — previewable Next.js/React |
| 5 | Candidate experience (dashboard, resume upload, growth path) | Yes |
| 6 | Recruiter experience (job wizard, candidate intelligence panel) | Yes |
| 7 | VIRA AI modules (mock-mode resume parsing, matching, explanations) | Yes — mock, with real-provider hook documented |
| 8 | Assessment engine | Yes |
| 9 | VIRA CALL voice interview | Partial — UI/state machine yes; live speech-to-text/text-to-speech needs your own API key at deployment |
| 10 | Tests | Yes — unit/API tests |
| 11 | Deployment config | Yes — Dockerfiles, `.env.example`, Vercel config, docs (I can't actually deploy to your cloud accounts) |

---

## 7. Responsible AI & Security Guardrails (baked in from Phase 2 onward)
- No ranking signal from gender/religion/caste/race/disability/political belief — enforced at the schema level (those fields simply don't exist on candidate/job models).
- Every `ai_recommendations` row carries a human-readable `explanation_json` — no bare scores shipped to the frontend.
- All hiring-stage transitions require a `recruiter_id` actor in `audit_logs` — AI never auto-rejects.
- Passwords bcrypt-hashed, JWT short-lived + refresh rotation, file upload MIME/size validation, rate limiting on auth and upload routes, `.env.example` with no real secrets committed.
