# Oz AI — Final Demo Video Script

**Target duration:** 4 minutes  
**Maximum duration:** 5 minutes  
**Demo incident:** Suspicious PowerShell Execution  
**Repository:** https://github.com/Jugnu0707/Kaggle

---

## Pre-recording setup

```bash
cd Kaggle
cp .env.example .env          # ensure GOOGLE_API_KEY set for Part 3 (optional)
python scripts/reset_demo.py  # 10 incidents, 25 logs, investigations on showcase cases
./scripts/dev.sh              # or: docker compose up --build
```

| URL | Purpose |
|-----|---------|
| http://localhost:5173 | Dashboard |
| http://localhost:8000/docs | Swagger (optional) |
| http://localhost:8000/api/v1/ai/test | Verify Gemini before recording |

For Part 4 (fallback): comment out `GOOGLE_API_KEY` in `.env`, restart backend, re-run `reset_demo.py`.

---

## Part 1 — Introduction (0:00–0:20 · 20 seconds)

**On screen:** Dashboard at `/` — incident counts and sidebar visible.

**Script:**

> This is **Oz AI** — an open-source enterprise incident response platform for the Kaggle AI Agents Intensive Capstone, Agents for Business track.
>
> Security operations centers face alert fatigue, slow manual triage, and heavy analyst workload. Oz AI coordinates eight specialist agents to structure investigations from uploaded logs to executive reports — while keeping humans accountable for every consequential decision.

**Transition:** Cut to architecture visual.

---

## Part 2 — Architecture (0:20–1:00 · 40 seconds)

**On screen:** `docs/architecture/architecture.png` in a viewer, or Settings page (`/settings`) showing ADK and MCP status, or scroll `docs/architecture/02_component_diagram.md` in the repo.

**Script:**

> Oz AI uses a layered stack. The **React dashboard** calls a **FastAPI** backend with thirty-five API paths. The **Coordinator Agent** validates context, then specialist agents run in sequence: Evidence, Threat Intelligence, MITRE Mapping, Risk, Response Planning, and Executive Report.
>
> The **Guardian Agent** validates every stage — injection detection, PII masking, schema checks. After agents finish, the **Timeline Engine** reconstructs events and the **Evaluation Engine** scores performance. Data persists in **SQLite**.
>
> **Google ADK** configures all eight agents. **Google Gemini** enriches four AI-first stages when an API key is set. **MCP** registers five operational tools for introspection. **Deterministic fallbacks** keep investigations completing when Gemini is unavailable.

**Transition:** Hard cut to live dashboard.

---

## Part 3 — Live demonstration (1:00–3:00 · 2 minutes)

**Incident:** **Suspicious PowerShell Execution** — PowerShell launched by WINWORD.EXE with an encoded command on finance workstation WS-FIN-042. Three log files attached. Pre-seeded by `reset_demo.py`; investigation already run.

### 3a. Dashboard (1:00–1:08)

**On screen:** `/`

> The dashboard shows ten seeded incidents across attack types — PowerShell, brute force, ransomware, and more. I'll walk through our showcase incident.

**Action:** Click **Incidents** in sidebar.

### 3b. Open incident (1:08–1:14)

**On screen:** `/incidents` → click **Suspicious PowerShell Execution** (High severity)

> This incident came from Microsoft Defender. Three logs capture process creation, encoded PowerShell, network connection to 185.234.72.19, and a T1059.001 alert.

**Action:** Land on `/incidents/{id}` — Overview tab.

### 3c. Run investigation (1:14–1:26)

**On screen:** Click **Run Investigation** → `/incidents/{id}/investigate`

> Investigations are explicit analyst actions — creating an incident does not auto-start agents. The Investigation Runner calls `POST /api/v1/investigations/run` and shows each pipeline stage: Evidence, Threat Intelligence, MITRE, Risk, Response, Executive Report, Guardian, Timeline, Evaluation.
>
> With demo data already seeded, stages show completed. A live run finishes in under a second with offline fallbacks.

**Action:** If time permits, click **Run Investigation** once (completes quickly). Otherwise point at completed stage list. Return to incident detail.

### 3d. Evidence (1:26–1:36)

**On screen:** Overview tab — description, Evidence Count (2), investigation metadata

> The **Evidence Agent** normalized three uploaded logs — `.log` and `.txt` formats — into a structured package: line counts, detected log type, sample entries, and timestamps. This is rule-based parsing with no LLM calls.

**Action:** Optionally flash **Logs** page (`/logs`) to show three attached files, then return to incident.

### 3e. Threat Intelligence (1:36–1:46)

**On screen:** **Threat Intelligence** tab

> **Threat Intelligence** extracted IOCs — the external IP 185.234.72.19, encoded command patterns — and assigned reputation labels. With Gemini configured, analyst notes are AI-generated; otherwise the offline reputation engine applies local rules.

**Action:** Highlight IOC values and reputation badges.

### 3f. MITRE ATT&CK (1:46–1:56)

**On screen:** **MITRE ATT&CK** tab

> **MITRE Mapping** matched local rules to ATT&CK techniques — here T1059.001 PowerShell — with confidence scores tied to matched evidence strings. No external MITRE API is used.

**Action:** Show technique ID and tactic.

### 3g. Risk Assessment (1:56–2:04)

**On screen:** **Risk Assessment** tab

> **Risk Assessment** produced an enterprise risk level, numeric score, and narrative explaining business exposure on the finance workstation.

### 3h. Response Plan (2:04–2:12)

**On screen:** **Response Plan** tab

> The **Response Planning Agent** drafted containment, eradication, recovery, and monitoring steps. These are recommendations only — Oz AI does not execute remediation.

### 3i. Executive Report (2:12–2:22)

**On screen:** **Executive Report** tab

> The **Executive Report** translates findings into leadership language — business impact, key findings, recommended actions — as JSON and Markdown without raw logs in the output.

**Action:** Scroll executive summary section.

### 3j. Guardian Audit (2:22–2:30)

**On screen:** **Guardian Audit** tab

> Every specialist stage passed through **Guardian** validation. Audit records show approved, warning, or rejected status with injection and PII checks between agents.

### 3k. Timeline (2:30–2:40)

**On screen:** **Timeline** tab

> The **Timeline Engine** reconstructed chronological events — WINWORD spawning PowerShell, network connection, Defender alert — from persisted agent outputs.

### 3l. Evaluation Dashboard (2:40–3:00)

**On screen:** Sidebar → **Evaluation** (`/evaluation`)

> The **Evaluation Dashboard** shows per-agent health scores from availability, reliability, performance, and accuracy metrics. One hundred seventy-six automated tests back the pipeline. Investigation Replay exposes `ai_used` and `fallback_used` on each step for transparency.

**Action:** Briefly show health scores. Optional: flash Settings (`/settings`) for ADK loaded and five MCP tools.

**Transition:** Cut to terminal for fallback segment.

---

## Part 4 — AI resilience (3:00–3:30 · 30 seconds)

**On screen:** Terminal with empty `GOOGLE_API_KEY`, or Investigation Replay (`/investigations/{runId}/replay`) showing `fallback_used: true` on Threat Intelligence, Risk, Response, or Executive Report steps.

**Script:**

> Oz AI is designed for reliability. When Gemini is unavailable — no API key, quota exceeded, or timeout — the workflow does not fail.
>
> Threat Intelligence, Risk, Response, and Executive Report each fall back to rule engines, playbooks, or templates. I'll reset without an API key: `python scripts/reset_demo.py`. Every tab still populates. Replay flags show which steps used fallback versus live AI.

**Action:** Show replay step badges, or re-open Risk tab on offline-seeded incident. Never display a real API key on screen.

**Transition:** Cut to closing slide or dashboard.

---

## Part 5 — Closing (3:30–4:00 · 30 seconds)

**On screen:** Dashboard or title card with repository URL.

**Script:**

> Oz AI delivers three outcomes for enterprise agent systems: structured multi-agent investigations with Guardian safety gates, offline-capable fallbacks for reliable demos, and one-command deployability with Docker Compose and `reset_demo.py`.
>
> API authentication, SIEM connectors, and human approval enforcement are on the roadmap — response plans remain recommendations today.
>
> The codebase is open source at github.com/Jugnu0707/Kaggle. Thank you for reviewing Oz AI.

**Transition:** End card — repository URL, 3 seconds hold.

---

## Timing summary

| Part | Content | Duration | Cumulative |
|------|---------|----------|------------|
| 1 | Introduction | 0:20 | 0:20 |
| 2 | Architecture | 0:40 | 1:00 |
| 3 | Live demonstration | 2:00 | 3:00 |
| 4 | AI resilience | 0:30 | 3:30 |
| 5 | Closing | 0:30 | 4:00 |
| Buffer | End card / pause | 0:00–1:00 | **≤ 5:00 max** |

**Estimated total:** 4 minutes (within 5-minute maximum)

---

## Related documents

- [FINAL_STORYBOARD.md](FINAL_STORYBOARD.md)
- [FINAL_RECORDING_GUIDE.md](FINAL_RECORDING_GUIDE.md)
- [JUDGE_FAQ.md](JUDGE_FAQ.md)
- [CHECKLIST.md](CHECKLIST.md)
