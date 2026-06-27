# Oz AI Demo Video — Narration & Speaking Notes

Speaking notes for the official Kaggle demonstration video. Read naturally — do not read verbatim if it sounds stiff. Target pace: ~140 words per minute.

---

## Part 1 — Introduction (~20 seconds · ~45 words)

**Tone:** Confident, clear, professional.

**Key points to land:**
- Project name: **Oz AI**
- Competition: Kaggle AI Agents Intensive Capstone, **Agents for Business**
- Problem: alert volume exceeds analyst capacity
- Solution angle: multi-agent coordination, not a chatbot

**Suggested opening:**

> Hi, I'm [name]. This is Oz AI — an open-source enterprise incident response platform for the Kaggle AI Agents Capstone.
>
> Security teams face thousands of alerts daily. Manual triage is slow and inconsistent. Oz AI coordinates eight specialist agents to structure investigations end to end — while humans stay in control of consequential decisions.

**Pause:** 1 beat before Part 2.

---

## Part 2 — Architecture (~40 seconds · ~95 words)

**Tone:** Technical but accessible — assume smart judges, not SOC veterans.

**Point at / mention on screen:**
- React dashboard (top)
- FastAPI backend
- Coordinator → eight agents
- Guardian between stages
- Timeline + Evaluation at the end
- SQLite persistence

**Technology callouts (don't rush):**
- **Google ADK** — agent configuration and runtime
- **Gemini** — optional enrichment for four agents
- **MCP** — five operational tools registered at startup
- **Rule engine** — offline fallbacks

**Suggested narration:**

> The architecture is layered. React talks to FastAPI. The Coordinator validates context and sequences eight specialist agents — Evidence, Threat Intel, MITRE, Risk, Response, and Executive Report. Guardian validates every output before the next stage runs. Timeline and Evaluation close the loop.
>
> Google ADK configures agents. Gemini enriches AI-first stages when configured. MCP exposes operational tools. And rule-based fallbacks keep the platform running without cloud AI.

**Avoid:** Listing all sixteen database tables or thirty-nine API operations.

---

## Part 3 — Live demo (~2 minutes · ~280 words)

**Tone:** Guided tour — "let me show you" energy.

**Demo incident:** **Suspicious PowerShell Execution** (High severity, 3 logs).

### Dashboard (10s)

> The dashboard shows ten seeded incidents — PowerShell, brute force, ransomware, and more. I'll walk through one investigation.

### Overview / Evidence (15s)

> This incident: PowerShell spawned by WINWORD.EXE with an encoded command on a finance workstation. Three logs uploaded. Evidence Agent parsed and normalized them — entry counts, timestamps, sample lines — using deterministic rules, no LLM.

### Threat Intelligence (10s)

> Threat Intel extracted IOCs — suspicious IP, encoded command patterns — and assigned reputation. With Gemini, you get AI analyst notes; offline, the local engine still labels every indicator.

### MITRE (10s)

> MITRE mapping applied local ATT&CK rules — T1059.001 PowerShell, high confidence, tied to matched log strings.

### Risk (7s)

> Risk Assessment produced an enterprise score and narrative — how this affects the organization.

### Response (7s)

> Response Planning drafted containment and recovery steps. Recommendations only — Oz AI never executes remediation.

### Executive Report (11s)

> The Executive Report gives leadership a plain-language summary — business impact, findings, actions — without exposing raw logs.

### Guardian (8s)

> Guardian audited every stage — injection checks, PII scanning, schema validation. You see approved or warning status per agent.

### Timeline (10s)

> Timeline reconstructed the attack sequence chronologically from all agent outputs.

### Evaluation (22s)

> The Evaluation Dashboard scores agent health after each run. You can also replay investigations step by step — with flags showing AI versus fallback — and export JSON or Markdown for auditors.

**Pacing tip:** Switch tabs as you finish each sentence. Don't narrate over blank loading states.

---

## Part 4 — Fallback (~40 seconds · ~95 words)

**Tone:** Emphasize reliability and judge-friendly offline demo.

**On screen:** Empty API key in terminal (blur key if visible), `reset_demo.py`, populated UI or replay with fallback badges.

**Suggested narration:**

> Reliability matters. Without a Gemini API key — or when quota is exhausted — Oz AI does not crash.
>
> Threat Intelligence, Risk, Response, and Executive Report each have rule-engine fallbacks. I'll reset the demo without an API key and run the workflow.
>
> Investigation completes. Every tab has structured data. Replay shows which steps used fallback. That's essential for demos, air-gapped sites, and judging without API access.

**Do not:** Show or speak your actual API key.

---

## Part 5 — Closing (~40 seconds · ~95 words)

**Tone:** Summarize value for judges; end confidently.

**Suggested narration:**

> Three takeaways.
>
> **Innovation:** eight coordinated agents, Guardian gates, and investigation replay — structured IR, not generic chat.
>
> **Security:** injection detection, PII masking, append-only audits, and human approval for response actions on the roadmap.
>
> **Competition fit:** Google ADK, MCP, multi-agent orchestration, evaluation pipeline, and one-command deployment — `docker compose up` and `python scripts/reset_demo.py`.
>
> Oz AI is open source on GitHub. Thank you for watching.

**End card:** Repository URL for 10 seconds.

---

## Delivery tips

| Tip | Reason |
|-----|--------|
| Record audio separately if needed | Easier to fix mistakes |
| Drink water before Part 3 | Longest uninterrupted section |
| Rehearse tab order once | Avoid hunting for Guardian vs Timeline |
| Say "recommendations only" for Response | Clarifies no auto-remediation |
| Say "Agents for Business" once | Competition track alignment |

---

## Word count estimate

| Part | Words | Duration |
|------|-------|----------|
| 1 | ~45 | 0:20 |
| 2 | ~95 | 0:40 |
| 3 | ~280 | 2:00 |
| 4 | ~95 | 0:40 |
| 5 | ~95 | 0:40 |
| **Total** | **~610** | **~4:20–4:30** |

At 140 WPM, ~610 words ≈ 4 minutes 20 seconds, plus pauses and screen time ≈ **4:30 target**.
