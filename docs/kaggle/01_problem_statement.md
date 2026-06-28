# Problem Statement

**Related:** [02 Solution](02_solution.md) · [11 Competition Mapping](11_competition_mapping.md)

Enterprise security operations centers (SOCs) operate under sustained pressure. Endpoint detection, network monitoring, identity systems, and cloud workloads generate thousands of alerts per day. Each signal may require log correlation, indicator enrichment, framework mapping, risk assessment, response planning, and executive communication — often while an incident is still active.

## SOC challenges

Three structural problems dominate daily operations:

**Alert fatigue.** Analysts review hundreds of low-confidence alerts. True incidents are deprioritized or missed. Triage quality varies by shift, experience, and available time.

**Investigation delays.** Manual response is sequential. Log collection spans multiple consoles. Threat intelligence lookups run indicator-by-indicator. MITRE ATT&CK mapping depends on analyst memory. Risk narratives and response playbooks are assembled from scratch. Executive summaries arrive late, after technical work is complete. These steps compound into extended mean time to respond (MTTR).

**Analyst workload.** Senior analysts become bottlenecks. Junior analysts may skip enrichment steps. Institutional knowledge is not captured in repeatable workflows. Teams spend disproportionate time on documentation and coordination rather than decisive action. Post-incident reporting for compliance, insurance, and executive review adds further demand on the same staff who must also contain active threats.

## Why existing tooling falls short

SIEM platforms detect anomalies but rarely produce structured investigation artifacts. Threat intelligence feeds provide data without investigation context. Ticketing systems track tasks but do not analyze evidence. Executive reporting tools consume analyst time without understanding security semantics. No single tool covers the full lifecycle from log upload to leadership-ready output.

## Why AI agents are appropriate

Incident response decomposes naturally into specialist tasks: evidence normalization, indicator enrichment, ATT&CK mapping, risk scoring, response planning, and executive reporting. A single monolithic model cannot maintain focused schemas, testable outputs, and auditable behavior across all stages.

Multi-agent systems address this by assigning each stage to a specialist agent with defined inputs, outputs, and validation rules. A coordinator ensures correct sequencing. A safety layer validates outputs before analysts consume them. Deterministic fallbacks allow offline operation when cloud AI is unavailable — critical for demos, testing, and quota-constrained environments.

Human analysts remain accountable for consequential decisions. Agents accelerate structured analysis, reduce repetitive work, and produce consistent artifacts. The business case is direct: faster containment reduces breach cost, standardized analysis improves audit readiness, and executive-ready reporting closes the gap between technical findings and leadership action.

Oz AI targets this problem domain — enterprise incident response — where coordinated specialist agents deliver measurable workflow structure without replacing human judgment.
