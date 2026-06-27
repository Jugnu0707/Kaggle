# Oz AI Demo Video — Operator Flow

Step-by-step guide for the presenter operating Oz AI during recording. Follow in order. Estimated operator time: 4–5 minutes on camera.

**Demo incident:** Suspicious PowerShell Execution  
**URLs:** Frontend `http://localhost:5173` · Backend `http://localhost:8000`

---

## Phase A — Pre-recording (not on camera)

| Step | Action | Verify |
|------|--------|--------|
| A1 | `cd Kaggle` | In repo root |
| A2 | `cp .env.example .env` if needed | File exists |
| A3 | Set `GOOGLE_API_KEY` in `.env` for AI demo | `curl localhost:8000/api/v1/ai/test` → connected true |
| A4 | `python scripts/reset_demo.py` | 10 incidents, 25 logs, runs complete |
| A5 | `./scripts/dev.sh` or `docker compose up` | Both services running |
| A6 | Open `http://localhost:5173` | Dashboard loads |
| A7 | Complete [recording checklist](recording_checklist.md) | All boxes checked |

---

## Phase B — Part 1: Introduction (on camera · 20s)

```
1. Open Dashboard
   URL: http://localhost:5173/
   Show: incident counts, sidebar, Oz AI branding
```

**Narrate:** Project name, problem, why Oz AI.

---

## Phase C — Part 2: Architecture (on camera · 40s)

```
2. Show architecture diagram
   Option A: Open docs/architecture/architecture.png in Preview/Photos
   Option B: Browser → Settings → http://localhost:5173/settings
            Show: Health, ADK status, MCP tools (5)
   Option C: Split — diagram 20s, Settings 20s
```

**Narrate:** Frontend → FastAPI → Coordinator → Agents → Guardian → Timeline → Evaluation. ADK, MCP, Gemini, rule engine.

```
3. Return to Dashboard
   URL: http://localhost:5173/
```

---

## Phase D — Part 3: Live demonstration (on camera · 2 min)

```
4. Open Incidents
   Click sidebar: Incidents
   URL: http://localhost:5173/incidents

5. Open showcase incident
   Click: "Suspicious PowerShell Execution" (High)
   URL: http://localhost:5173/incidents/{id}

6. Overview tab (default)
   Show: title, High severity, description, log count (3)
   Narrate: Evidence Agent normalized logs

7. Threat Intelligence tab
   Click tab: Threat Intelligence
   Show: IOCs, IP 185.234.72.19, reputation badges
   Pause: 2 seconds on IOC table

8. MITRE tab
   Click tab: MITRE
   Show: T1059.001, tactic, confidence
   Pause: 2 seconds on technique row

9. Risk tab
   Click tab: Risk
   Show: risk level, score, narrative

10. Response tab
    Click tab: Response
    Show: containment, eradication, recovery sections

11. Executive Report tab
    Click tab: Executive Report
    Scroll: executive summary, business impact
    Pause: 3 seconds on summary

12. Guardian Audit tab
    Click tab: Guardian Audit
    Show: per-agent validation records

13. Timeline tab
    Click tab: Timeline
    Show: ordered events with timestamps

14. Evaluation Dashboard
    Click sidebar: Evaluation
    URL: http://localhost:5173/evaluation
    Show: agent health cards, metrics

15. Settings (optional · 10s if time)
    Click sidebar: Settings
    URL: http://localhost:5173/settings
    Show: ADK loaded, MCP 5 tools

16. Investigation Replay (optional · 10s if time)
    Navigate: Incidents → PowerShell → Investigate link
    OR open existing replay URL from a completed run
    Show: step list, AI/Fallback badges, Export button
```

---

## Phase E — Part 4: Fallback engine (on camera · 40s)

**Option 1 — Pre-recorded terminal clip (recommended):**

Record separately before main session:

```
17a. Stop backend
18a. Edit .env — set GOOGLE_API_KEY= (empty)
19a. python scripts/reset_demo.py
20a. Restart backend
21a. Show dashboard — tabs still populated
22a. Open Replay — show fallback_used: true on steps
```

**Option 2 — Live on camera:**

```
17. Switch to terminal (full screen)
18. Show: grep GOOGLE_API_KEY .env (empty value only — blur file if needed)
19. Run: python scripts/reset_demo.py
    Wait: script completes (~30–60s) — narrate during wait
20. Return to browser — refresh incident tabs
21. Show Risk or Response tab with fallback-sourced content
22. Open Replay — highlight fallback badges
```

---

## Phase F — Part 5: Closing (on camera · 40s)

```
23. Show closing visual
    Option A: Architecture diagram
    Option B: GitHub repo page (github.com/Jugnu0707/Kaggle)
    Option C: Dashboard with end card overlay in editor

24. End card (editor or live)
    Text: Oz AI · github.com/Jugnu0707/Kaggle · Kaggle AI Agents Capstone
```

**Narrate:** Innovation, security, roadmap, competition alignment, thank you.

---

## Flow diagram

```text
[Pre-record setup]
        ↓
Dashboard (Intro)
        ↓
Architecture diagram / Settings
        ↓
Dashboard
        ↓
Incidents list
        ↓
Suspicious PowerShell Execution
        ↓
Overview → Threat Intel → MITRE → Risk → Response
        ↓
Executive Report → Guardian → Timeline
        ↓
Evaluation Dashboard → (Settings) → (Replay)
        ↓
Terminal: offline reset OR pre-recorded fallback clip
        ↓
Closing + end card
        ↓
FINISH
```

---

## Timing guardrails

| If running long (>4:30) | Cut |
|-------------------------|-----|
| Over 5:00 total | Skip Settings and Replay in Part 3 |
| Part 3 > 2:15 | Shorten Risk and Response to 5s each |
| Part 4 awkward | Use pre-recorded terminal clip only |

| If running short (<4:00) | Add |
|--------------------------|-----|
| Under 4:00 | Expand Executive Report scroll |
| Under 4:00 | Show Investigation Runner start (don't wait for completion) |
| Under 4:00 | Pause longer on Evaluation metrics |

---

## Post-demo reset

```bash
# Restore AI key for development
# Edit .env — restore GOOGLE_API_KEY
python scripts/reset_demo.py
```

---

## Related documents

- [Demo script](demo_script.md)
- [Storyboard](storyboard.md)
- [Narration](narration.md)
- [Recording checklist](recording_checklist.md)
- [FAQ](faq.md)
