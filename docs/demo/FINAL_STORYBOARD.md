# Oz AI — Final Demo Storyboard

**Target duration:** 4 minutes · **Maximum:** 5 minutes  
**Format:** 1080p screen recording + voiceover · **Aspect ratio:** 16:9  
**Demo incident:** Suspicious PowerShell Execution

---

## Scene 1 — Introduction

| Field | Detail |
|-------|--------|
| **Timecode** | 0:00–0:20 |
| **Duration** | 20s |
| **Screen** | Dashboard `/` — sidebar, incident count (10), severity cards |
| **Narration** | Oz AI name, Kaggle capstone, SOC problem (alert fatigue, delays, workload), decision-support positioning |
| **Action** | None — static hold 5s, then slow pan across dashboard |
| **Transition** | Cut to architecture |

---

## Scene 2 — Architecture

| Field | Detail |
|-------|--------|
| **Timecode** | 0:20–1:00 |
| **Duration** | 40s |
| **Screen** | Option A: `docs/architecture/architecture.png` full screen. Option B: `/settings` — health, ADK loaded, MCP 5 tools. Option C: repo file `docs/architecture/02_component_diagram.md` |
| **Narration** | Frontend → FastAPI → Coordinator → Agents → Guardian → Timeline → Evaluation → SQLite. ADK, Gemini, MCP, fallbacks |
| **Action** | Scroll diagram or highlight Settings status rows |
| **Transition** | Hard cut to live browser — dashboard |

---

## Scene 3 — Dashboard

| Field | Detail |
|-------|--------|
| **Timecode** | 1:00–1:08 |
| **Duration** | 8s |
| **Screen** | `/` |
| **Narration** | Ten seeded incidents; opening showcase |
| **Action** | Click **Incidents** |
| **Transition** | Page load |

---

## Scene 4 — Incident list

| Field | Detail |
|-------|--------|
| **Timecode** | 1:08–1:14 |
| **Duration** | 6s |
| **Screen** | `/incidents` — **Suspicious PowerShell Execution** row visible (High, Investigating) |
| **Narration** | WINWORD.EXE spawning encoded PowerShell; Defender source |
| **Action** | Click incident row |
| **Transition** | Incident detail loads — Overview tab |

---

## Scene 5 — Investigation Runner

| Field | Detail |
|-------|--------|
| **Timecode** | 1:14–1:26 |
| **Duration** | 12s |
| **Screen** | `/incidents/{id}/investigate` — pipeline steps: Evidence → … → Evaluation |
| **Narration** | Explicit `POST /investigations/run`; stages listed; optional live run |
| **Action** | Click **Run Investigation** (optional — completes quickly offline) OR point at completed stages. Navigate back to incident |
| **Transition** | Return to `/incidents/{id}` |

---

## Scene 6 — Evidence (Overview + Logs)

| Field | Detail |
|-------|--------|
| **Timecode** | 1:26–1:36 |
| **Duration** | 10s |
| **Screen** | Overview tab — description, Evidence Count, investigation status. Optional 2s flash: `/logs` showing three PowerShell log files |
| **Narration** | Evidence Agent — rule-based log normalization; three files; no LLM |
| **Action** | Highlight description text and evidence count |
| **Transition** | Click **Threat Intelligence** tab |

---

## Scene 7 — Threat Intelligence

| Field | Detail |
|-------|--------|
| **Timecode** | 1:36–1:46 |
| **Duration** | 10s |
| **Screen** | Threat Intelligence tab — IOC list, reputation labels |
| **Narration** | IOC extraction; IP 185.234.72.19; Gemini or offline engine |
| **Action** | Scroll to show 2–3 findings |
| **Transition** | Click **MITRE ATT&CK** |

---

## Scene 8 — MITRE ATT&CK

| Field | Detail |
|-------|--------|
| **Timecode** | 1:46–1:56 |
| **Duration** | 10s |
| **Screen** | MITRE tab — T1059.001 and related techniques |
| **Narration** | Local rule matching; confidence scores |
| **Action** | Highlight technique ID column |
| **Transition** | Click **Risk Assessment** |

---

## Scene 9 — Risk Assessment

| Field | Detail |
|-------|--------|
| **Timecode** | 1:56–2:04 |
| **Duration** | 8s |
| **Screen** | Risk tab — level, score, narrative |
| **Narration** | Enterprise risk scoring |
| **Transition** | Click **Response Plan** |

---

## Scene 10 — Response Plan

| Field | Detail |
|-------|--------|
| **Timecode** | 2:04–2:12 |
| **Duration** | 8s |
| **Screen** | Response tab — containment, eradication, recovery sections |
| **Narration** | Recommendations only; no auto-remediation |
| **Transition** | Click **Executive Report** |

---

## Scene 11 — Executive Report

| Field | Detail |
|-------|--------|
| **Timecode** | 2:12–2:22 |
| **Duration** | 10s |
| **Screen** | Executive Report tab — summary, business impact |
| **Narration** | Leadership-ready output; no raw logs |
| **Action** | Scroll executive summary |
| **Transition** | Click **Guardian Audit** |

---

## Scene 12 — Guardian Audit

| Field | Detail |
|-------|--------|
| **Timecode** | 2:22–2:30 |
| **Duration** | 8s |
| **Screen** | Guardian Audit tab — validation records, statuses |
| **Narration** | Per-stage validation; injection and PII checks |
| **Transition** | Click **Timeline** |

---

## Scene 13 — Timeline

| Field | Detail |
|-------|--------|
| **Timecode** | 2:30–2:40 |
| **Duration** | 10s |
| **Screen** | Timeline tab — chronological events |
| **Narration** | Timeline Engine reconstruction |
| **Action** | Scroll 2–3 events |
| **Transition** | Sidebar → **Evaluation** |

---

## Scene 14 — Evaluation Dashboard

| Field | Detail |
|-------|--------|
| **Timecode** | 2:40–3:00 |
| **Duration** | 20s |
| **Screen** | `/evaluation` — agent health scores. Optional 3s: `/settings` ADK + MCP |
| **Narration** | Health scores; 176 tests; replay transparency |
| **Transition** | Cut to terminal or replay page |

---

## Scene 15 — AI resilience

| Field | Detail |
|-------|--------|
| **Timecode** | 3:00–3:30 |
| **Duration** | 30s |
| **Screen** | Option A: Terminal — `grep GOOGLE_API_KEY .env` showing empty, `python scripts/reset_demo.py`. Option B: `/investigations/{runId}/replay` — Fallback badges on AI-first steps |
| **Narration** | No API key / quota; fallbacks; workflow completes; replay flags |
| **Action** | Never show real API key |
| **Transition** | Cut to closing |

---

## Scene 16 — Closing

| Field | Detail |
|-------|--------|
| **Timecode** | 3:30–4:00 |
| **Duration** | 30s |
| **Screen** | Dashboard or end card: **github.com/Jugnu0707/Kaggle** |
| **Narration** | Multi-agent + Guardian + fallbacks + deployability; roadmap items; thank judges |
| **Transition** | Fade out — hold URL 3s |

---

## Visual reference assets

Pre-generated screenshots in `docs/screenshots/` (for B-roll or backup if live demo fails):

| View | File |
|------|------|
| Dashboard | `dashboard.png` |
| Incident detail | `incident-details.png` |
| Threat Intelligence | `threat-intelligence.png` |
| MITRE | `mitre.png` |
| Risk | `risk-assessment.png` |
| Response | `response-plan.png` |
| Executive Report | `executive-report.png` |
| Guardian | `guardian.png` |
| Timeline | `timeline.png` |
| Evaluation | `evaluation-dashboard.png` |
| Investigation Runner | `investigation-runner.png` |

---

## Tab order reference (actual UI)

Incident detail tabs on `/incidents/{id}`:

1. Overview (evidence context — no separate Evidence tab)
2. Timeline
3. Threat Intelligence
4. MITRE ATT&CK
5. Risk Assessment
6. Response Plan
7. Executive Report
8. Guardian Audit

Investigation Runner: `/incidents/{id}/investigate`  
Investigation Replay: `/investigations/{runId}/replay`

---

## Related documents

- [FINAL_DEMO_SCRIPT.md](FINAL_DEMO_SCRIPT.md)
- [FINAL_RECORDING_GUIDE.md](FINAL_RECORDING_GUIDE.md)
