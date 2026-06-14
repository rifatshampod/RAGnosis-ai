# RAGnosis AI — v2 Product Plan

**From a single-model diagnostic toy to a production multi-device repair platform.**

> Codename: RAGnosis AI
> Version: v2 (Production / Feature-Rich)
> Lens: product architect — every feature described by **what it does for the user**, not how it's built.

---

## Where v1 Stands Today

v1 is a working proof of concept:

- One device (Dell Precision 5560), a handful of hardcoded PDFs.
- Streamlit chat with citations and a strict no-hallucination guardrail.
- Stateless FastAPI — no accounts, no memory, no upload, no admin.
- Knowledge base is frozen at ingest time; adding a manual means a developer re-runs a container.

It proves the core promise — *grounded, cited, deterministic answers*. It does **not** yet feel like a product a team or a business would adopt. v2 closes that gap.

---

## The v2 Vision

Turn RAGnosis from "a chatbot that knows one laptop" into **a self-service repair knowledge platform** where:

- An **admin** owns a growing library of devices and manuals without touching code.
- **End users** (technicians, support agents, owners) get fast, trustworthy, cited answers across many devices.
- Every answer is **traceable, rateable, and improvable** over time.

The north star: *make the right repair step findable in seconds, with proof, for any device the organization supports.*

---

## Feature Catalog

Each feature below lists its **user-facing impact** — the concrete change in what someone can do or feel when using the system.

---

### 1. Modern React Front End

Replace the Streamlit prototype with a dedicated React (Next.js) web app.

**User impact**
- The app feels like real software, not a data-science demo — instant, responsive, mobile-friendly.
- Conversations stay readable on a phone in a repair bay, not just on a laptop.
- Streaming answers appear token-by-token, so the user sees progress instead of staring at a spinner during slow model calls.
- A persistent left rail of past conversations means a technician can return to yesterday's diagnosis without re-typing.
- Citations render as clickable cards that jump to the exact manual page, so trust is one click away.

---

### 2. User Accounts & Authentication

Email/password plus optional SSO (Google) login, with secure sessions.

**User impact**
- Each person has their own private history — diagnoses aren't shared into one global stream.
- Work follows the user across devices: start on a workshop PC, finish on a phone.
- Saved and starred answers become a personal repair playbook.
- Organizations can trust that only their staff see their knowledge base.

---

### 3. Roles & Permissions (Admin / Technician / Viewer)

Tiered access so not everyone can do everything.

**User impact**
- **Admins** manage devices, manuals, and users.
- **Technicians** ask questions, save answers, flag bad responses.
- **Viewers** (e.g. trainees, customers) can read but not modify the library.
- A support manager can onboard a new hire in seconds with the right access — no risk of a junior wiping the manual library.

---

### 4. Admin Panel — Manual & Device Management

A web console where admins upload PDFs, define devices, and manage the knowledge base without a developer.

**User impact**
- Adding support for a new laptop is a drag-and-drop upload, not a code change and container rebuild.
- The admin watches ingestion progress live (uploaded → parsing → chunking → indexed → ready) and knows exactly when a manual is searchable.
- Mistakes are reversible: remove an outdated manual and its answers stop citing it immediately.
- The business can expand its supported-device catalog as fast as it can collect PDFs.

---

### 5. Multi-Device Knowledge Base

Move beyond a single hardcoded model to a library of devices, each with its own manuals.

**User impact**
- One platform answers for the Precision 5560 *and* the XPS 15 *and* a Latitude — pick the device, ask the question.
- Answers never bleed across devices: ask about the 5560 and you won't get an XPS recovery step by mistake.
- A repair shop covering dozens of models has one tool instead of dozens of PDF folders.
- Users can search "all devices" when they're unsure which model they have, then narrow down.

---

### 6. Device-Scoped & Filtered Search

Let users filter retrieval by device, manual type, or section.

**User impact**
- A technician who already knows it's a BIOS issue can scope to the service manual and skip the noise.
- Faster, more precise answers because the system isn't searching irrelevant documents.
- Confidence that the citation comes from the *right* manual for the *right* device.

---

### 7. Persistent Chat History & Sessions

Every conversation is saved, named, searchable, and resumable.

**User impact**
- Re-open the exact diagnosis from a job last week to finish or verify a repair.
- Search past conversations ("that battery swelling issue") instead of re-deriving it.
- A handoff between shifts is just sharing a conversation link.
- Knowledge compounds — the team's solved problems become a living archive.

---

### 8. Answer Feedback & Quality Loop

Thumbs up/down plus "this citation was wrong" flagging on every answer.

**User impact**
- Users feel heard — a bad answer can be reported in one click instead of silently distrusted.
- Admins see which questions the system handles poorly and which manuals need better coverage.
- Over time the system visibly improves because real usage steers what gets fixed.
- Trust grows: people see the platform learning from their corrections.

---

### 9. Source Document Viewer (In-App PDF)

Click a citation and the original manual opens in-app, scrolled to the cited page with the passage highlighted.

**User impact**
- "Don't trust, verify" becomes effortless — the proof is right there, no separate PDF hunt.
- A skeptical technician can confirm the exact wording before doing irreversible hardware work.
- Training improves: new staff learn where information lives in the manuals.

---

### 10. Saved Answers / Repair Playbooks

Bookmark answers into named collections ("Common 5560 fixes", "BIOS recovery").

**User impact**
- Frequent fixes are one tap away — no re-asking the same question daily.
- A team builds shared, curated repair guides from real answers.
- Onboarding material writes itself from the questions the team actually asks.

---

### 11. Conversational Follow-Ups (Context Memory)

The agent remembers the current conversation, so follow-up questions work naturally.

**User impact**
- Ask "and how do I remove that screw?" without re-stating the whole device and symptom.
- Diagnosis feels like talking to an expert who's been with you the whole time, not a vending machine that forgets each query.
- Fewer words to type, faster to the fix.

---

### 12. Smart Symptom Intake (Guided Diagnosis)

For LED codes, beep patterns, and common symptoms, offer pickers/wizards instead of free text.

**User impact**
- A user who can't describe the problem in words can still get an answer ("2 white, 2 yellow lights" via a visual picker).
- Fewer dead-end "insufficient evidence" replies caused by vague phrasing.
- Faster path from symptom to fix for the most common failure modes.

---

### 13. Usage Analytics Dashboard (Admin)

A dashboard showing top questions, unanswered queries, device coverage, and feedback trends.

**User impact**
- Admins learn what users actually need and where the knowledge base has holes.
- Buying/sourcing decisions get data: "30% of failed queries are about a device we don't have manuals for."
- Proves the platform's value to stakeholders with real numbers.

---

### 14. Export & Share (PDF / Link)

Export any answer or conversation as a clean PDF or shareable link.

**User impact**
- Hand a customer a printed, cited repair summary instead of a screenshot.
- Attach a diagnosis to a support ticket or work order.
- Share a tricky fix with a colleague who isn't logged in (read-only link).

---

### 15. Notifications & Async Ingestion Status

Background processing for large manuals with notification when ready.

**User impact**
- Admins upload a 500-page manual and walk away — they're pinged when it's searchable instead of babysitting a progress bar.
- The app never freezes during heavy ingestion.
- Large knowledge bases scale without the UI feeling slow.

---

### 16. Multilingual Answers (Stretch)

Ask in one language, get cited answers from English manuals translated faithfully.

**User impact**
- Non-English-speaking technicians use the same authoritative manuals.
- Global support teams share one knowledge base across regions.
- Citations stay intact — translation never breaks the proof trail.

---

## Feature Prioritization

Grouped by impact-per-effort to give a build order, framed by user value.

### Phase A — Foundation (makes it a real product)
| Feature | Why first |
|---|---|
| React front end (#1) | Everything else is felt through the UI. |
| User accounts (#2) | Required before history, saved answers, roles. |
| Persistent history (#7) | The first feature users *notice* and miss when gone. |
| Multi-device KB (#5) | The core scope unlock — one device is a demo, many is a product. |

### Phase B — Admin Self-Service (removes the developer bottleneck)
| Feature | Why next |
|---|---|
| Admin panel + upload (#4) | Lets the business grow the KB without code. |
| Roles & permissions (#3) | Safe multi-user operation. |
| Async ingestion status (#15) | Makes upload trustworthy for large manuals. |
| Device-scoped search (#6) | Keeps answers precise as the KB grows. |

### Phase C — Trust & Stickiness (drives daily use)
| Feature | Why |
|---|---|
| Source document viewer (#9) | Verifiable proof = trust. |
| Feedback loop (#8) | Visible improvement = retention. |
| Conversational follow-ups (#11) | Natural, faster interaction. |
| Saved playbooks (#10) | Turns one-off answers into reusable assets. |

### Phase D — Scale & Polish (differentiation)
| Feature | Why |
|---|---|
| Analytics dashboard (#13) | Proves value, guides KB growth. |
| Guided symptom intake (#12) | Wins the hardest-to-phrase queries. |
| Export & share (#14) | Bridges to customers and tickets. |
| Multilingual (#16) | Opens global teams. |

---

## What Stays Non-Negotiable from v1

Production scale must not dilute the original promise:

- **Grounding** — answers come only from indexed manuals.
- **Citations** — every claim still carries manual, section, page.
- **Honest refusal** — insufficient evidence means "I don't know," never a guess.
- **Determinism** — same question, same evidence, same answer.

v2 adds reach and convenience *around* this core. It never relaxes it.

---

## Success Criteria (v2)

- An admin can onboard a brand-new device end-to-end (upload → searchable) without developer help.
- A user can manage their own account, history, and saved answers.
- The platform serves multiple devices with zero cross-device answer leakage.
- Every answer remains cited and verifiable in-app against the source page.
- The team's solved problems accumulate into a reusable, searchable archive.

---

*RAGnosis AI v2 — from a manual you have to read, to a repair expert you can ask.*
