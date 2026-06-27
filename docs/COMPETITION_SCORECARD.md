# Competition Scorecard — Oz AI

**Kaggle AI Agents: Intensive Vibe Coding Capstone · Agents for Business**  
**Date:** 2026-06-27

Scoring: 0 (missing) to 10 (exemplary). **Overall: 84 / 100**

---

## Category scores

| Category | Score (/10) | Rationale |
|----------|-------------|-----------|
| **Innovation** | 8.5 | Eight coordinated specialists with Guardian gates and investigation replay—not a generic chatbot. Offline-first fallbacks uncommon in capstone projects. |
| **AI Architecture** | 8.5 | Clear pipeline, per-agent persistence, explicit orchestration, explainability metadata. Direct service calls vs MCP at runtime is MVP trade-off. |
| **ADK Usage** | 7.5 | Native ADK config for 8 agents, runtime init, registry. Gap: no session checkpointing or `adk eval`. |
| **MCP Usage** | 7.0 | Five operational tools with typed schemas. Gap: domain tools not implemented; agents don't call MCP at runtime. |
| **Security** | 8.5 | Dedicated Guardian layer, injection/PII/schema checks, append-only audits, no auto-remediation. Gap: no API auth or approval UI. |
| **Documentation** | 9.5 | README, 47 docs, kaggle writeup, submission package, diagrams, demo scripts, FAQ. Exemplary for capstone. |
| **Code Quality** | 8.0 | 176 tests, typed Python/TS, repository pattern, Pydantic schemas. Some sprint debt in milestone docs. |
| **UI/UX** | 8.0 | Clean dark dashboard, tabbed incident detail, replay page, evaluation dashboard. Polling not WebSockets. |
| **Demo Quality** | 7.5 | One-command reset, 10 attack scenarios, script ready. Video not yet recorded; styled screenshots. |
| **Deployability** | 8.5 | Docker Compose, offline demo, env template, judge quickstart. Vite dev in Docker not production Nginx. |

**Weighted overall: 84 / 100**

---

## Strengths

1. **End-to-end multi-agent pipeline** with Guardian between every stage
2. **Investigation replay and explainability** (`ai_used`, `fallback_used`, export)
3. **Offline demo capability** — full workflow without API keys
4. **Professional documentation** — submission package, diagrams, judge FAQ
5. **Evaluation framework** with persisted metrics and dashboard
6. **Executive reporting** without raw log exposure
7. **176 automated tests** including e2e, reliability, API inventory
8. **Single-command demo reset** for judges

---

## Weaknesses

1. **No submission notebook or recorded video yet** (packaging gap)
2. **MCP operational only** — agents use services directly
3. **No API authentication** in v0.1.0
4. **SQLite** limits production concurrency narrative
5. **Human approval workflow** documented but not enforced in UI
6. **Styled screenshots** rather than live browser captures
7. **ADK session/eval** not fully leveraged

---

## Known limitations

- SQLite for demo; PostgreSQL for production
- Free Gemini quota affects AI enrichment
- Offline threat intelligence (no VirusTotal live)
- No SIEM integration
- No automatic remediation (by design)
- In-process agent execution
- Empty `datasets/` directory

See `docs/kaggle/limitations.md`.

---

## Recommended improvements (post-competition)

| Priority | Improvement |
|----------|-------------|
| P0 | API authentication and RBAC |
| P0 | Response plan approval workflow |
| P1 | Domain MCP tools + ADK tool wiring |
| P1 | Splunk/Sentinel log connectors |
| P1 | PostgreSQL migration |
| P2 | 30-scenario evaluation library |
| P2 | Production Docker (Nginx, non-root) |
| P2 | WebSocket live investigation updates |
| P3 | VirusTotal/AbuseIPDB adapters |
| P3 | ADK session checkpointing + `adk eval` |

---

## Competition requirement mapping

| Requirement | Met | Score contribution |
|-------------|-----|-------------------|
| Multi-agent | Yes | Innovation, AI Architecture |
| Google ADK | Yes | ADK Usage |
| MCP | Partial | MCP Usage |
| Security | Yes | Security |
| Deployability | Yes | Deployability |
| Documentation | Yes | Documentation |
| Business impact | Yes | Innovation |
| Evaluation | Yes | Code Quality |

---

## Verdict

Oz AI is a **strong capstone submission** for the Agents for Business track. Documentation and demo reproducibility exceed typical submissions. Complete notebook and video to maximize judging score.

**Recommendation:** Submit after recording video and creating notebook.
