# Solution

**Related:** [01 Problem Statement](01_problem_statement.md) · [03 Architecture](03_architecture.md) · [05 AI Agents](05_ai_agents.md)

## Oz AI

Oz AI is an open-source enterprise incident response platform built for the Kaggle AI Agents Intensive Capstone (Agents for Business track). It combines a React operations dashboard, a FastAPI backend, eight Google ADK specialist agents, a Guardian safety layer, MCP operational tools, and SQLite persistence into a single deployable system.

Oz AI is a **decision-support platform**. It structures investigations, surfaces risk, and drafts response recommendations. It does not execute remediation autonomously.

## How it works

An analyst creates an incident and uploads log files via the dashboard or REST API. The analyst then explicitly triggers an investigation via `POST /api/v1/investigations/run` or the Investigation Runner UI. Creating an incident does not automatically start the agent pipeline.

The **Coordinator Agent** validates incident context and produces an execution plan. The **Investigation Workflow Service** runs specialist agents in sequence:

1. Evidence — normalize uploaded logs
2. Threat Intelligence — extract and enrich IOCs
3. MITRE Mapping — map evidence to ATT&CK techniques
4. Risk Assessment — score enterprise risk
5. Response Planning — draft containment and recovery steps
6. Executive Report — produce JSON and Markdown leadership summaries

The **Guardian Agent** validates every specialist output before the workflow advances. After agent execution, the **Timeline Engine** reconstructs chronological events and the **Evaluation Engine** scores agent performance.

Each agent persists structured output to dedicated database tables. Analysts review results in tabbed Incident Detail views, Investigation Replay, and the Evaluation dashboard.

Replay APIs expose step-level metadata including `ai_used` and `fallback_used` flags, latency, and sanitized summaries.

## Why multiple agents

Incident response involves distinct analytical domains with different schemas, test criteria, and failure modes. Collapsing these into one agent produces broad, hard-to-evaluate outputs.

Oz AI assigns one mission per agent:

| Agent | Mission |
|-------|---------|
| Coordinator | Validate context and plan execution |
| Evidence | Normalize logs without threat analysis |
| Threat Intelligence | IOC extraction and reputation |
| MITRE Mapping | ATT&CK technique mapping |
| Risk Assessment | Enterprise risk scoring |
| Response Planning | Structured response recommendations |
| Executive Report | Leadership-ready summaries |
| Guardian | Safety and schema validation |

This design maps to a real analyst workflow, enables per-agent testing, and demonstrates multi-agent coordination for competition evaluation.

## Why deterministic fallback

Four agents use Gemini when `GOOGLE_API_KEY` is configured: Threat Intelligence, Risk, Response, and Executive Report. When Gemini is unavailable — missing key, quota exceeded, timeout, invalid JSON, or Guardian rejection — each agent falls back to a rule engine, playbook, or template.

Fallbacks serve three purposes:

1. **Offline demos** — `python scripts/reset_demo.py` seeds ten incidents with twenty-five logs and runs full investigations without any API key.
2. **Workflow continuity** — the pipeline never blocks on AI failure.
3. **Evaluator reproducibility** — judges can run the system deterministically without configuring external services.

When Gemini is available, it enriches AI-first agent outputs. Replay steps record whether AI or fallback executed at each stage.

## Deployment

```bash
git clone https://github.com/Jugnu0707/Kaggle.git
cd Kaggle
cp .env.example .env
docker compose up --build
python scripts/reset_demo.py   # optional demo seed
```

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| Swagger docs | http://localhost:8000/docs |

Oz AI demonstrates that multi-agent coordination, Google ADK integration, MCP tooling, and responsible AI guardrails can compose into a deployable incident response workflow — while keeping humans accountable for approval and execution of consequential actions (approval workflow enforcement is documented but not yet implemented in the API).
