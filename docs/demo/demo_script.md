# Oz AI — Official Demo Video Script

**Target duration:** 4 minutes 30 seconds  
**Maximum duration:** 5 minutes  
**Demo incident:** Suspicious PowerShell Execution  
**Presenter:** [Your name]  
**Recording date:** [TBD]

---

## Pre-recording setup

```bash
cd Kaggle
python scripts/reset_demo.py
./scripts/dev.sh
# Frontend: http://localhost:5173
# API docs:  http://localhost:8000/docs
```

Confirm `GOOGLE_API_KEY` is set in `.env` for Part 3 (live AI path). For Part 4, unset or comment out the key before re-running `reset_demo.py`.

---

## Part 1 — Introduction (0:00–0:20 · 20 seconds)

**On screen:** Oz AI dashboard (`/`) or title slide with logo, then cut to dashboard.

**Script:**

> Hi, I'm [name], and this is **Oz AI** — an open-source enterprise incident response platform built for the Kaggle AI Agents Intensive Capstone, Agents for Business track.
>
> Security teams drown in alerts. Manual triage is slow, inconsistent, and hard to explain to leadership. Oz AI coordinates eight specialist AI agents to structure investigations — from log evidence to executive reports — while keeping humans in control of every consequential decision.

**Transition:** Fade or cut to architecture diagram (`docs/architecture/architecture.png` or browser tab with diagram).

---

## Part 2 — Architecture (0:20–1:00 · 40 seconds)

**On screen:** Architecture diagram; optionally scroll `docs/architecture/system-architecture.md` or Settings page showing ADK/MCP status.

**Script:**

> Oz AI uses a layered architecture. The **React dashboard** talks to a **FastAPI** backend. The **Coordinator Agent** validates context and drives the pipeline.
>
> Eight specialist agents run in sequence: Evidence, Threat Intelligence, MITRE Mapping, Risk, Response Planning, and Executive Report. The **Guardian Agent** validates every stage — checking for prompt injection, PII, and schema compliance.
>
> After agents complete, the **Timeline Engine** reconstructs events and the **Evaluation Engine** scores performance.
>
> Under the hood: **Google ADK** configures agents, **Google Gemini** enriches AI-first stages when an API key is present, **MCP** registers five operational tools, and a **rule engine** provides deterministic fallbacks so demos work offline without cloud AI.

**Transition:** Cut to live dashboard.

---

## Part 3 — Live demonstration (1:00–3:00 · 2 minutes)

**On screen:** Single incident walkthrough — **Suspicious PowerShell Execution**.

### 3a. Dashboard (1:00–1:10)

> Here's the Oz AI dashboard. We have ten seeded incidents across attack types — PowerShell, brute force, ransomware, and more. I'll open our showcase incident.

**Action:** Click **Incidents** → select **Suspicious PowerShell Execution** (High severity).

### 3b. Incident overview & evidence (1:10–1:25)

> This incident describes PowerShell launched by WINWORD.EXE with an encoded command on a finance workstation. Three log files are attached. The **Evidence Agent** normalized these logs into a structured package — file type, entry count, time range, and sample entries — without any LLM calls.

**Action:** Show **Overview** tab (title, severity, description, log count).

### 3c. Threat intelligence (1:25–1:35)

> **Threat Intelligence** extracted IOCs — the suspicious IP, encoded command patterns — and enriched reputation. With Gemini configured, you get AI-generated analyst notes; otherwise the offline reputation engine labels indicators automatically.

**Action:** Click **Threat Intelligence** tab. Highlight IOCs and reputation badges.

### 3d. MITRE mapping (1:35–1:45)

> **MITRE Mapping** matched local rules to ATT&CK — here, T1059.001 PowerShell and related techniques — with confidence scores tied to matched evidence strings.

**Action:** Click **MITRE** tab. Show technique IDs.

### 3e. Risk assessment (1:45–1:52)

> **Risk Assessment** scores enterprise risk — level, numeric score, and a narrative explaining business exposure.

**Action:** Click **Risk** tab.

### 3f. Response plan (1:52–1:59)

> The **Response Planning Agent** drafts containment, eradication, recovery, and monitoring steps. These are recommendations only — Oz AI never executes remediation automatically.

**Action:** Click **Response** tab.

### 3g. Executive report (1:59–2:10)

> The **Executive Report** translates technical findings into leadership language — business impact, key findings, and recommended actions — with Markdown export and no raw logs in the output.

**Action:** Click **Executive Report** tab. Scroll executive summary.

### 3h. Guardian (2:10–2:18)

> Every stage passed through **Guardian** validation. Here you see audit records — approved, warning, or rejected — with injection and PII checks between each agent.

**Action:** Click **Guardian Audit** tab.

### 3i. Timeline (2:18–2:28)

> The **Timeline Engine** reconstructed a chronological sequence from all agent outputs — process creation, network connection, defender alert — in one view.

**Action:** Click **Timeline** tab.

### 3j. Evaluation dashboard (2:28–3:00)

> Finally, the **Evaluation Dashboard** shows per-agent health scores and benchmark metrics persisted after each investigation.
>
> You can also run a new investigation from the Investigation Runner, replay every agent step with AI versus fallback flags, and export the replay as JSON or Markdown.

**Action:** Navigate to **Evaluation** in sidebar. Briefly show Settings (health, ADK, MCP). Optional: flash Investigation Runner or Replay page if time permits.

**Transition:** Cut to terminal or split screen for fallback demo.

---

## Part 4 — Fallback engine (3:00–3:40 · 40 seconds)

**On screen:** Terminal showing empty `GOOGLE_API_KEY`, run `python scripts/reset_demo.py`, then dashboard with populated incident tabs OR Investigation Replay showing `fallback_used: true`.

**Script:**

> Oz AI is designed for reliability. If I remove the Gemini API key — or hit a quota limit — the platform does not fail.
>
> Every AI-first agent — Threat Intelligence, Risk, Response, and Executive Report — falls back to deterministic rule engines and playbooks. I'll reset the demo without an API key and run an investigation.
>
> The workflow completes. Every tab still has structured data. Investigation Replay shows which steps used fallback versus live AI. This offline capability matters for demos, air-gapped environments, and judging environments without API access.

**Action:** Show replay step with fallback badge, or re-open Risk/Response tabs on offline-seeded incident.

**Transition:** Cut to presenter or closing slide.

---

## Part 5 — Closing (3:40–4:20 · 40 seconds)

**On screen:** Architecture diagram, GitHub repo URL, or dashboard.

**Script:**

> Oz AI demonstrates three things that matter for enterprise AI agents.
>
> **Innovation:** eight coordinated specialists with Guardian gates and investigation replay — not a single chatbot.
>
> **Security:** prompt injection detection, PII masking, append-only audits, and human-in-the-loop response approval on the roadmap.
>
> **Competition alignment:** Google ADK, MCP tools, multi-agent orchestration, evaluation pipeline, and one-command deployability with `docker compose up` and `python scripts/reset_demo.py`.
>
> The codebase is open source on GitHub. Thank you for watching Oz AI.

**Transition:** End card with repo URL: `https://github.com/Jugnu0707/Kaggle`

---

## Timing summary

| Part | Content | Duration | Cumulative |
|------|---------|----------|------------|
| 1 | Introduction | 0:20 | 0:20 |
| 2 | Architecture | 0:40 | 1:00 |
| 3 | Live demonstration | 2:00 | 3:00 |
| 4 | Fallback engine | 0:40 | 3:40 |
| 5 | Closing | 0:40 | 4:20 |
| Buffer | Pause / end card | 0:10 | **4:30** |

**Estimated total:** 4 minutes 30 seconds (within 5-minute maximum)

---

## Related documents

- [Storyboard](storyboard.md)
- [Narration notes](narration.md)
- [Demo flow (operator guide)](demo_flow.md)
- [Recording checklist](recording_checklist.md)
- [FAQ](faq.md)
