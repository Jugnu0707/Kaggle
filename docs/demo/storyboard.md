# Oz AI Demo Video — Storyboard

**Target duration:** 4:30 · **Maximum:** 5:00  
**Format:** 1080p screen recording + voiceover  
**Aspect ratio:** 16:9

---

## Scene 1 — Cold open

| Field | Detail |
|-------|--------|
| **Duration** | 0:00–0:05 (5s) |
| **Expected screen** | Black or Oz AI title card: "Oz AI — Enterprise Incident Response" |
| **Narration** | *(silent or music only)* |
| **Transition** | Fade to dashboard |

---

## Scene 2 — Introduction

| Field | Detail |
|-------|--------|
| **Duration** | 0:05–0:20 (15s) |
| **Expected screen** | Dashboard (`/`) — incident counts, recent activity, sidebar visible |
| **Narration** | Introduce Oz AI, Kaggle capstone, SOC alert fatigue, why multi-agent IR |
| **Transition** | Mouse move to Incidents; cut at 0:20 |

---

## Scene 3 — Architecture overview

| Field | Detail |
|-------|--------|
| **Duration** | 0:20–1:00 (40s) |
| **Expected screen** | `docs/architecture/architecture.png` in image viewer OR scroll `docs/architecture/system-architecture.md` with Mermaid diagram OR Settings page (`/settings`) showing ADK + MCP status |
| **Narration** | Layer stack: Frontend → FastAPI → Coordinator → Agents → Guardian → Timeline → Evaluation → SQLite. Mention ADK, Gemini, MCP, rule engine |
| **Transition** | Hard cut to live browser dashboard |

---

## Scene 4 — Dashboard pan

| Field | Detail |
|-------|--------|
| **Duration** | 1:00–1:10 (10s) |
| **Expected screen** | Dashboard — highlight incident count (10), severity breakdown |
| **Narration** | Ten seeded incidents; opening showcase incident |
| **Transition** | Click **Incidents** in sidebar |

---

## Scene 5 — Incident list

| Field | Detail |
|-------|--------|
| **Duration** | 1:10–1:15 (5s) |
| **Expected screen** | Incidents page — list with **Suspicious PowerShell Execution** visible (High) |
| **Narration** | Select PowerShell incident |
| **Transition** | Click incident row |

---

## Scene 6 — Overview / Evidence

| Field | Detail |
|-------|--------|
| **Duration** | 1:15–1:25 (10s) |
| **Expected screen** | Incident Detail — **Overview** tab: title, High severity, description, 3 logs |
| **Narration** | WINWORD.EXE → PowerShell encoded command; Evidence Agent normalized logs |
| **Transition** | Click **Threat Intelligence** tab |

---

## Scene 7 — Threat Intelligence

| Field | Detail |
|-------|--------|
| **Duration** | 1:25–1:35 (10s) |
| **Expected screen** | Threat Intelligence tab — IOC table, IP `185.234.72.19`, reputation badges |
| **Narration** | IOC extraction and enrichment; Gemini or offline engine |
| **Transition** | Click **MITRE** tab |

---

## Scene 8 — MITRE Mapping

| Field | Detail |
|-------|--------|
| **Duration** | 1:35–1:45 (10s) |
| **Expected screen** | MITRE tab — T1059.001 PowerShell, tactic Execution, confidence % |
| **Narration** | Local ATT&CK rule matching |
| **Transition** | Click **Risk** tab |

---

## Scene 9 — Risk Assessment

| Field | Detail |
|-------|--------|
| **Duration** | 1:45–1:52 (7s) |
| **Expected screen** | Risk tab — risk level badge, score, narrative text |
| **Narration** | Enterprise risk scoring |
| **Transition** | Click **Response** tab |

---

## Scene 10 — Response Plan

| Field | Detail |
|-------|--------|
| **Duration** | 1:52–1:59 (7s) |
| **Expected screen** | Response tab — containment, eradication, recovery sections |
| **Narration** | Recommendations only; no auto-remediation |
| **Transition** | Click **Executive Report** tab |

---

## Scene 11 — Executive Report

| Field | Detail |
|-------|--------|
| **Duration** | 1:59–2:10 (11s) |
| **Expected screen** | Executive Report tab — executive summary, business impact, scroll slowly |
| **Narration** | Leadership-ready output; no raw logs |
| **Transition** | Click **Guardian Audit** tab |

---

## Scene 12 — Guardian

| Field | Detail |
|-------|--------|
| **Duration** | 2:10–2:18 (8s) |
| **Expected screen** | Guardian Audit tab — list of validations per agent, approved/warning status |
| **Narration** | Safety layer between every stage |
| **Transition** | Click **Timeline** tab |

---

## Scene 13 — Timeline

| Field | Detail |
|-------|--------|
| **Duration** | 2:18–2:28 (10s) |
| **Expected screen** | Timeline tab — ordered events with timestamps |
| **Narration** | Reconstructed chronology from agent outputs |
| **Transition** | Click **Evaluation** in sidebar |

---

## Scene 14 — Evaluation Dashboard

| Field | Detail |
|-------|--------|
| **Duration** | 2:28–2:50 (22s) |
| **Expected screen** | `/evaluation` — agent health cards, metrics table |
| **Narration** | Per-agent scores; benchmarks after each run |
| **Transition** | Optional: click **Settings** briefly (ADK/MCP) |

---

## Scene 15 — Investigation Runner / Replay (optional)

| Field | Detail |
|-------|--------|
| **Duration** | 2:50–3:00 (10s) |
| **Expected screen** | Investigation Replay page — step list, AI/Fallback badges, export button |
| **Narration** | Replay and explainability for auditors |
| **Transition** | Cut to terminal |

---

## Scene 16 — Fallback demonstration

| Field | Detail |
|-------|--------|
| **Duration** | 3:00–3:40 (40s) |
| **Expected screen** | Terminal: show `.env` with empty `GOOGLE_API_KEY` (blur if needed), run `python scripts/reset_demo.py`, return to dashboard with populated tabs OR Replay with `fallback_used: true` |
| **Narration** | Offline reliability; rule engines; workflow never blocks |
| **Transition** | Cut to closing visual |

---

## Scene 17 — Closing

| Field | Detail |
|-------|--------|
| **Duration** | 3:40–4:20 (40s) |
| **Expected screen** | Architecture diagram or GitHub repo page; end card with URL |
| **Narration** | Innovation, security, competition alignment, thank you |
| **Transition** | Fade to end card |

---

## Scene 18 — End card

| Field | Detail |
|-------|--------|
| **Duration** | 4:20–4:30 (10s) |
| **Expected screen** | Static: "Oz AI" · github.com/Jugnu0707/Kaggle · Kaggle AI Agents Capstone |
| **Narration** | *(silent or brief thank you)* |
| **Transition** | Fade out |

---

## Timing rollup

| Scenes | Duration |
|--------|----------|
| 1–2 | 0:20 |
| 3 | 0:40 |
| 4–15 | 2:00 |
| 16 | 0:40 |
| 17–18 | 0:50 |
| **Total** | **4:30** |

---

## Visual guidelines

- Browser zoom: 100–110% for readability
- Hide bookmarks bar; use clean window
- Dark theme (Oz AI default) — consistent throughout
- Cursor: smooth movements; pause 1s on each tab before speaking
- No scrolling faster than narration can follow
