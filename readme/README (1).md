# Clinic Booking System

<div align="center">

**Backend design guide · **

<br/>

![Architecture](https://img.shields.io/badge/Architecture-Modular_Monolith-4C6EF5?style=for-the-badge&labelColor=1a1a2e)
![Database](<https://img.shields.io/badge/Database-PostgreSQL_(Neon)-336791?style=for-the-badge&labelColor=1a1a2e&logo=postgresql&logoColor=white>)
![Async](https://img.shields.io/badge/Async-FastAPI_Background_Tasks-009688?style=for-the-badge&labelColor=1a1a2e&logo=fastapi&logoColor=white)
![Cache](https://img.shields.io/badge/Cache-None-6c757d?style=for-the-badge&labelColor=1a1a2e)

![Frontend](https://img.shields.io/badge/Frontend-React_on_Vercel-000000?style=for-the-badge&labelColor=1a1a2e&logo=vercel&logoColor=white)
![Backend](https://img.shields.io/badge/Backend-Self--Managed_VPS-F39C12?style=for-the-badge&labelColor=1a1a2e)
![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub_Actions-2088FF?style=for-the-badge&labelColor=1a1a2e&logo=githubactions&logoColor=white)

</div>

<br/>

frontend url: https://clinic-booking-system-jade.vercel.app/
backend url : https://ilya-test-api.pesagrid.co.ke/health (health check)

|                    |                                                                                                                                                                              |
| ------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Scenario**       | Small clinic, 5 doctors, 30-minute appointment slots                                                                                                                         |
| **Core guarantee** | A slot can never be double-booked, even under concurrent requests                                                                                                            |
| **Stack**          | FastAPI · PostgreSQL (Neon) · React (Vite)                                                                                                                                   |
| **Deployment**     | Backend on a self-managed VPS · Frontend on Vercel · CI/CD via GitHub Actions using subdomain from previous project for ssl-cert fro backend & backup gmail account for smtp |

##

**major tradeoff implemented was a loginless booking(idea was patients rarely book a lot of times and it a ux friction to create an account so at to just book and appointment- similar to how ticketing systems works)authentication & RBAC has been implemented on the ADMIN & DOCTORS endpoint to have clear enforcement on who has access to patient data ** - explained more in 5. [Key Design Decisions](#5-key-design-decisions)

##

\*\*what i have implemented instead is a magic link-on confirmation of booking the client recieves a link embeded with an access token(long lived till the appointment data and time of which it expires)which they can use to view their booking and manage their booking

---

---

## Table of Contents

1. [System Design](#1-system-design)
2. [Architecture Diagram](#2-architecture-diagram)
3. [Security-Centric Data Flow](#3-security-centric-data-flow)
4. [User Experience Flow](#4-user-experience-flow)
5. [Key Design Decisions](#5-key-design-decisions)
6. [Trade-offs Considered](#6-trade-offs-considered)
7. [Non-Functional Requirements](#7-non-functional-requirements)
8. [Running Locally](#8-running-locally)
9. [CI/CD](#9-cicd)
10. [AI Usage Reflection](#10-ai-usage-reflection)

---

## 1. System Design

SYSTEM ARCHITECTURE-MODULAR MONOLITH

### Models

**Doctor**

- `id`, `full_name`, `speciality`, `work_start`, `work_end`

**DoctorSchedule** _(recurring weekly rule, not physical slots)_

- `id`, `doctor_id`, `day_of_week`, `start_time`, `end_time`, `slot_duration_minutes` (fixed at 30 per the brief)

**DoctorLeave** _(exceptions to the schedule — vacation, sick day, day off)_

- `id`, `doctor_id`, `start_datetime`, `end_datetime`, `reason`

**Patient**

- `id`, `full_name`, `phone`, `email`

**Appointment**

- `id`, `doctor_id`, `patient_id`, `slot_time` (UTC), `status` (`CONFIRMED` / `CANCELLED`), `cancelled_reason`, `rescheduled_from_id`, `created_at`, `updated_at`

### Core Approach: Insert-on-Book, Not Pre-Populated Slots

Rather than pre-generating empty slot rows for every 30-minute increment a doctor might work, the system treats a booking as a **fact that gets inserted**, and computes availability **at read time** by combining:

```
Doctor's working hours  −  Doctor's leave periods  −  Existing CONFIRMED appointments
```

This means:

- No background job is needed to pre-generate future slots.
- A doctor going on leave is a single row in `doctor_leaves` — no need to find and delete/update thousands of pre-populated rows.
- Cancelling an appointment is a status flip (`CONFIRMED` → `CANCELLED`); the slot is automatically available again since the availability query simply stops seeing it.
- Full booking history is preserved — no row is ever destructively overwritten.

### Preventing Double-Booking

Because two patients can request the same slot within milliseconds of each other, availability-check-then-insert is **not** safe on its own — the check and the insert are separate operations with no lock between them.

**Chosen approach:** a database-level unique constraint as the source of truth, backed by row locking at the application layer for a clean user-facing error:

```sql
CREATE UNIQUE INDEX unique_confirmed_slot
ON appointments (doctor_id, slot_time)
WHERE status = 'CONFIRMED';
```

Combined with `SELECT ... FOR UPDATE` on the doctor row inside a transaction when booking, so a losing concurrent request gets a clean "slot no longer available" response instead of a raw DB constraint error.

---

## 2. Architecture Diagram

> ![alt text](<system design.png>)
>
> _Shows: Patient/Doctor clients → API Gateway → Backend Application (Booking Engine, Cancellation Service, Reschedule Service, Leave Service) → PostgreSQL, plus the async path via fastapi background task → Notification Service → Email Provider._

---s

## 3. Security-Centric Data Flow

> ![alt text](<security centric data flow diagram.png>)
>
> _Shows trust boundaries (Public Internet → Edge/Gateway → Trusted Backend → Data Zone → Third-Party Email) and the specific control applied at each boundary crossing._

| Flow                           | Crosses Boundary                   | Sensitive Data     | Control                                                            |
| ------------------------------ | ---------------------------------- | ------------------ | ------------------------------------------------------------------ |
| Patient → booking form         | Public → Gateway                   | name, phone, email | HTTPS, rate-limit by IP, input validation                          |
| Gateway → Backend              | Gateway → App                      | booking payload    | Re-validate server-side, parameterized queries                     |
| Backend → Database             | App → DB                           | PII at rest        | Encryption at rest, least-privilege DB user                        |
| Backend → Email Provider       | App → 3rd party                    | magic-link token   | Token stored as **hash** in DB; plaintext only in the email itself |
| Magic link click → view/cancel | Public → Gateway (2nd entry point) | booking status     | Rate-limit, phone-digit confirmation before cancel                 |
| Doctor login → patient list    | Public → App (authenticated)       | patient PII        | AuthZ scoped to own patients (not just AuthN)                      |

---

## 4. User Experience Flow

> ![alt text](<userflow diagram.png>)
>
> _Shows: General vs. Specialist path → slot selection → guest booking form → confirmation email with magic link → view/cancel/reschedule via link._

---

## 5. Key Design Decisions

- **Login-less (guest) booking via magic link.** Patients provide name/phone/email at booking time and receive an emailed link with a long-lived token (expires on the appointment date) to view/cancel/reschedule — no account required.
- **Fixed 30-minute slots**,.
- **Modular monolith**, not separate microservices. Booking, Cancellation, Reschedule, and Leave logic live as modules within one deployed backend, was avoiding unnecessary network hops between services at this scale.
- **UTC storage for all datetimes**, converted to clinic-local time only at the API/display layer, to avoid timezone ambiguity as the system grows across regions later(it was mentioned looking to scale).
- **Doctor-side requires authentication**; patient-side does not — these are different trust levels (recurring staff user vs. one-off anonymous patient).

---

## 6. Trade-offs Considered

| Decision                                                                | Trade-off Accepted                                                                                                                                | Why                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| ----------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Guest booking (no patient login)                                        | Anyone with the magic link (+ correct phone digits) can view/cancel a booking                                                                     | Booking is infrequent and low-sensitivity (no medical/payment data); friction of forced signup outweighs this risk at current scope                                                                                                                                                                                                                                                                                                     |
| Insert-on-book vs. pre-populated slots                                  | Slightly more complex availability query (computed, not stored)                                                                                   | Far easier to handle schedule changes, leave days, and cancellations without mass row mutation                                                                                                                                                                                                                                                                                                                                          |
| Symptom → speciality matching via static keyword lookup table           | Not as accurate as NLP/triage logic                                                                                                               | Building a classifier here is over-engineering relative to the brief; a lookup table is honest about its limits and easy to extend                                                                                                                                                                                                                                                                                                      |
| Single Postgres instance, no sharding yet                               | Won't scale to multi-region on its own                                                                                                            | Clinic is single-location today; sharding by `clinic_id` is a documented future path, not a present need                                                                                                                                                                                                                                                                                                                                |
| No Kubernetes / single deployment target                                | No auto-scaling or multi-region failover yet                                                                                                      | Traffic at a 5-doctor clinic doesn't justify the operational overhead; can be implemented in the next step if the clinic expands                                                                                                                                                                                                                                                                                                        |
| FastAPI `BackgroundTasks` over RabbitMQ/Redis Pub/Sub for notifications | No retry/replay if the process crashes mid-send; doesn't scale across multiple API instances (each instance only knows its own tasks)             | A message broker is unnecessary infrastructure for a single-instance deployment sending one non-critical confirmation email; `BackgroundTasks` gives the same fire-and-forget async benefit without extra services to deploy, configure, and monitor within the project timeline. Would move to a durable queue (e.g. RabbitMQ, Redis Streams) if scaled to multiple API instances or if notification delivery became business-critical |
| Rate-limiting                                                           | rate limiting by ip on the booking endpoint presents a challange of what if there are multiple people from one single public ip trying to connect | the decision made is to still rate-limit by ip but increase the rate-limit per minute to levels that clearly show its ddos                                                                                                                                                                                                                                                                                                              |
| Using Gmail SMTP over Dedicated email service                           | Using Gmail SMTP with an app password for transactional email                                                                                     | the absence of a verified domainpr, if in production, would use a dedicated provider (SendGrid/Resend) with domain verification for better deliverability and to avoid tying clinic communications to a personal account.                                                                                                                                                                                                               |

---

## 7. Non-Functional Requirements

**Security**

- Rate-limiting on both the booking endpoint and the magic-link view/cancel endpoint (per ip, per-identity).
- PII encrypted at rest (relying on managed database defaults rather than custom encryption).
- Magic-link tokens stored as hashes, never in plaintext, in the database.

**Performance**

- Target: sub-100ms for availability queries.
- Achieved by keeping booking/cancellation/reschedule/leave logic in-process (modular monolith) rather than across multiple network-hopping services.
- Indexed on `(doctor_id, slot_time)` filtered to `CONFIRMED` status to keep the availability query fast as appointment volume grows.

**Scale**

- Designed for a single small clinic today.
- Documented, not built: sharding by `doctor_id`/`clinic_id` and container orchestration (e.g. Kubernetes) as the path forward if the clinic becomes a multi-location chain.

---

## 8. Running Locally

>

```bash
git clone <repo-url>
cd <repo-name>
cp .env.example .env
python -m venv venv (to create the virtual environment for this)
venv\scripts\activate (windows command ) source env/bin/activate (mac or linux command)
pip install -r requirements.txt (to install the dependencies)
alembic upgrade --head #run migrations
python seed_doctors.py # to seed doctors if testing locally
uvicorn main:app --reload(to start the server) or docker compose up --build

and thats how you start locally

```

---

## 9. CI/CD

>

- **Public URL:**
  - Backend: `https://ilya-test-api.pesagrid.co.ke` (health check: `/health`)
  - Frontend: `https://clinic-booking-system-jade.vercel.app/`
- **Pipeline tool:** `GitHub Actions` (CI + backend CD) + `Vercel` (frontend CD)
- **Trigger:** Runs test suite on every pull request to `main`; auto-deploys on merge to `main` — frontend via Vercel's GitHub integration, backend via a GitHub Actions job that SSHes into the VPS and rebuilds/restarts the Docker containers
- **What it does:**
  - **Backend CI/CD**: checks out code, sets up Python 3.12, installs dependencies from `requirements.txt`, runs the test suite with `pytest`, runs a Bandit security scan, then (on merge to `main` only, and only if tests pass) SSHes into the VPS and runs `docker compose up -d --build` to redeploy the updated container.
  - **Frontend CI**: checks out code, sets up Node.js 20, installs dependencies with `npm ci`, runs the linter, builds the app with `npm run build`; Vercel then automatically deploys the built app to production on merge to `main`.

---

## 10. AI Usage Reflection

> 1. What did you use AI for across the four sections?

- Used AI in Section 1 (system design) to think through trade-offs — comparing insert-on-book vs. pre-populated slots, evaluating login-less booking via magic link vs. requiring signup, and reasoning through concurrency/locking strategies before writing any code. Also used it to plan the implementation structure (folder layout, phased build order) . Relied on AI heavily for the frontend as well — design direction, layout, and component structure for the React app.

> 2. One example where an AI suggestion improved your work — what was the prompt?

- Prompted: "is letting people book without login a good decision? or i should have patients sign up first?"
  The response walked through both sides — friction of forced signup for infrequent bookings vs. the benefits of accounts (booking history, stronger security, doctor-side trust) — and framed the real deciding factor as whether the system needed a persistent patient relationship or not. Since patients don't pick a specific doctor and there's no medical history/insurance involved, this confirmed the login-less magic-link design was the right fit rather than something to second-guess.

> 3. One example where AI output was wrong or incomplete — how did you catch it?

- While building the frontend with Claude Code, appointment times displayed on the frontend weren't being converted to UTC correctly when retrieving appointment details — they were shown as-is instead of being converted from the backend's UTC storage to the user's local time. I caught this by manually checking displayed times against the actual stored values and fixed the conversion myself.

> 4. Two decisions you made without AI, and why you trusted your own judgment there.

- **Choosing FastAPI BackgroundTasks over a message broker (RabbitMQ/Redis) for sending confirmation emails.** I made this call myself based on the actual scale of the project — a single clinic, single deployed instance, one non-critical notification — where a full message broker would add operational overhead with no real benefit. I trusted my own judgment here because it came down to matching infrastructure to actual scale, not a technical unknown I needed help reasoning through.
- **Choosing Vite + React for the frontend.** I picked this specifically because I wanted a client-side rendered app that calls the backend API directly, without needing server-side rendering — Vite is a fast, minimal build tool that fits that exactly. Since I already knew what I needed architecturally (a thin client hitting a REST API), this was a straightforward stack decision I was confident making on my own.
