# Threat Model

**Project Name:** Oz AI
**Document Status:** Outline Only — Threat Model Pending Development Phase
**Date:** 2026-06-26
**Methodology:** STRIDE

> This document defines the threat model for the Oz AI platform. The threat model must be completed before security testing begins. The STRIDE methodology (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege) is used as the primary threat classification framework. Section headings are the structural contract.

---

## Table of Contents

1. [Threat Modeling Scope](#1-threat-modeling-scope)
2. [Assets and Trust Boundaries](#2-assets-and-trust-boundaries)
3. [Threat Actors](#3-threat-actors)
4. [STRIDE Analysis](#4-stride-analysis)
5. [Prompt Injection Threat Model](#5-prompt-injection-threat-model)
6. [Audit Trail Integrity Threats](#6-audit-trail-integrity-threats)
7. [Supply Chain Threats](#7-supply-chain-threats)
8. [Residual Risks and Mitigations](#8-residual-risks-and-mitigations)
9. [Security Controls Summary](#9-security-controls-summary)

---

## 1. Threat Modeling Scope

### 1.1 In-Scope Components

*Pending: Define the exact system boundary for this threat model after implementation is complete. Expected in-scope components:*

- FastAPI backend application (all endpoints, middleware, services)
- Agent layer (all eight agents and the ADK runtime)
- MCP tool layer (all ten tools and the permission registry)
- SQLite database and all data at rest
- Frontend React application
- Docker containers and Docker Compose configuration
- Network communication between components
- Environment variable and secret storage

### 1.2 Out-of-Scope Components

*Pending: Define what is explicitly excluded from the threat model scope.*

Expected out of scope for MVP:
- External alert source systems (their security is the responsibility of the integrating organization)
- Kaggle evaluation infrastructure
- GitHub repository security (covered by GitHub's threat model)
- LLM provider infrastructure (Gemini API — Google's responsibility)

### 1.3 Threat Model Assumptions

*Pending: Document the assumptions under which this threat model is valid.*

Expected assumptions:
- The host operating system is trusted (not modeled).
- Physical access to the host is denied to unauthorized parties.
- Docker daemon security is maintained at the host level.
- The network between services in `docker-compose.yml` is treated as trusted for the MVP.

---

## 2. Assets and Trust Boundaries

### 2.1 Asset Inventory

*Pending: A complete list of all assets to be protected, classified by sensitivity.*

| Asset | Sensitivity | Notes |
|---|---|---|
| Gemini API Key | Critical | Allows LLM API access; exposure creates financial risk and allows impersonation |
| Incident Records | High | Contains details of security incidents; sensitive business data |
| Audit Trail | High | Evidence chain for compliance; integrity is paramount |
| Agent Prompts | Medium | Disclosure could enable adversarial prompt crafting |
| Response Plans | High | Contains remediation details; disclosure could reveal security gaps |
| Executive Reports | Medium-High | Business-sensitive; audience-appropriate access controls required |
| API Bearer Token | High | Grants full API access if disclosed |
| Dataset Files | Medium | Knowledge base contents; not directly sensitive but influences agent behavior |

### 2.2 Trust Boundary Diagram

*Pending: A diagram showing trust boundaries between:*

- Public internet (untrusted) → FastAPI ingestion endpoint
- FastAPI → Agent layer (trusted internal)
- Agent layer → MCP tools (trusted internal)
- MCP tools → Dataset files (trusted internal)
- Frontend browser (semi-trusted, authenticated) → FastAPI read/write endpoints
- Docker internal network (trusted between services)

### 2.3 Data Flow Crossing Trust Boundaries

*Pending: A list of every data flow that crosses a trust boundary, to be analyzed for threats.*

---

## 3. Threat Actors

### 3.1 Threat Actor Profiles

*Pending: Define the threat actors relevant to Oz AI.*

| Threat Actor | Motivation | Capability | Likely Attack Vectors |
|---|---|---|---|
| **External Attacker** | Disrupt incident response, exfiltrate incident data | Moderate to high | API exploitation, prompt injection, credential theft |
| **Malicious Alert Source** | Manipulate agent analysis through crafted payloads | Low to moderate | Prompt injection in alert payload, data poisoning |
| **Compromised Analyst Account** | Approve malicious response actions, exfiltrate reports | Low | Legitimate API access with stolen credentials |
| **Supply Chain Attacker** | Compromise dependencies to gain code execution | High | Malicious package in `pyproject.toml` or `package.json` |
| **Insider Threat** | Exfiltrate incident data, tamper with audit trail | Low (for MVP single-tenant) | Direct database access, log manipulation |

---

## 4. STRIDE Analysis

*Pending: A complete STRIDE analysis for each component and data flow in scope. To be completed after implementation.*

### 4.1 Spoofing

*Pending: Analysis of spoofing threats — adversaries impersonating legitimate components or users.*

Categories to analyze:
- API caller spoofing (bypassing bearer token authentication)
- Agent impersonation (one agent calling tools as if it were another)
- Alert source spoofing (crafting alerts that appear to come from trusted internal systems)

### 4.2 Tampering

*Pending: Analysis of tampering threats — unauthorized modification of data.*

Categories to analyze:
- Alert payload tampering in transit
- Database record tampering (especially `AuditEvent`)
- Agent prompt file tampering (on disk)
- Dataset poisoning (knowledge base, threat intel, MITRE data)
- Docker image tampering

### 4.3 Repudiation

*Pending: Analysis of repudiation threats — actors denying their actions.*

Categories to analyze:
- Analyst denying an approval decision (mitigated by immutable audit trail)
- Agent denying a tool call (mitigated by MCP tool audit logging)

### 4.4 Information Disclosure

*Pending: Analysis of information disclosure threats — unauthorized access to sensitive data.*

Categories to analyze:
- API response exposing secrets in error messages
- PII in agent outputs surfaced to the frontend (mitigated by Guardian Agent PII scanner)
- Technical details leaking into executive summary reports
- Secrets in log output
- Incident data accessible without authentication

### 4.5 Denial of Service

*Pending: Analysis of denial of service threats — making the system unavailable.*

Categories to analyze:
- Large alert payload flooding the API
- Slow-loris attack against the FastAPI server
- Agent pipeline exhaustion (submitting many incidents simultaneously)
- SQLite write lock contention

### 4.6 Elevation of Privilege

*Pending: Analysis of elevation of privilege threats — gaining unauthorized permissions.*

Categories to analyze:
- Bypassing the human approval gate via direct database manipulation
- Agent calling tools outside its permitted set
- API endpoint accessible without authentication

---

## 5. Prompt Injection Threat Model

### 5.1 Attack Surface

*Pending: A detailed analysis of all points where user-controlled or external data enters an LLM prompt.*

Expected injection points:
- Raw alert payload body
- Entity names extracted from alert payload (used in tool calls)
- Log event content retrieved by `evidence_collector` (could contain injected instructions)
- Knowledge base search results (if knowledge base is tampered with)
- System topology data (if topology data is externally controlled)

### 5.2 Injection Attack Categories

*Pending: Categorization of prompt injection attack types relevant to Oz AI.*

| Category | Description | Risk Level |
|---|---|---|
| **Direct Injection** | Attacker places instructions in the alert payload | High |
| **Indirect Injection** | Attacker places instructions in log data that the Evidence Agent retrieves | High |
| **Knowledge Base Poisoning** | Attacker modifies knowledge base data to influence agent outputs | Medium |
| **Goal Hijacking** | Injection causes agent to pursue different goal (e.g., approve all actions automatically) | Critical |
| **Data Exfiltration via Tool** | Injection causes agent to call `notification_dispatch` with exfiltrated data | High |

### 5.3 Guardian Agent Injection Defense

*Pending: A detailed description of the Guardian Agent's injection detection mechanism, its known limitations, and its failure modes.*

### 5.4 Residual Injection Risk

*Pending: An honest assessment of the residual injection risk after Guardian Agent mitigations are applied.*

---

## 6. Audit Trail Integrity Threats

### 6.1 Audit Trail Threat Analysis

*Pending: Analysis of threats to the integrity and completeness of the audit trail.*

Threats to analyze:
- Unauthorized deletion of audit records
- Unauthorized modification of audit record content
- Audit record omission (agent action that is not logged)
- Timestamp manipulation
- Injection of false audit records

### 6.2 Technical Controls for Audit Integrity

*Pending: Description of the technical controls that protect audit trail integrity.*

Controls:
- Append-only ORM service pattern (no `update()` or `delete()` methods on `AuditService`)
- Database constraints (if possible with SQLite: triggers or check constraints)
- Post-MVP: cryptographic signing of audit records

---

## 7. Supply Chain Threats

### 7.1 Python Dependency Threats

*Pending: Analysis of the supply chain threat surface for the Python dependency tree.*

### 7.2 Node.js Dependency Threats

*Pending: Analysis of the supply chain threat surface for the frontend npm dependency tree.*

### 7.3 Base Image Threats

*Pending: Analysis of threats from base Docker images.*

### 7.4 Mitigations

*Pending: Description of supply chain security controls.*

Expected controls:
- All dependencies pinned to specific versions in `pyproject.toml` and `package.json`.
- `pip-audit` and `npm audit` run before submission to check for known vulnerabilities.
- Specific (not `:latest`) base image tags in Dockerfiles.

---

## 8. Residual Risks and Mitigations

*Pending: A risk register of all identified threats that are not fully mitigated in the MVP.*

| Threat | STRIDE Category | Risk Level | MVP Mitigation | Residual Risk | Post-MVP Plan |
|---|---|---|---|---|---|
| *(To be populated after STRIDE analysis)* | | | | | |

---

## 9. Security Controls Summary

*Pending: A consolidated summary of all security controls implemented in the MVP, mapped to the threats they address.*

| Control | Threats Addressed | Implementation Location |
|---|---|---|
| Bearer token authentication | Spoofing, Elevation of Privilege | `backend/api/` auth middleware |
| Pydantic input validation | Tampering, DoS (malformed input) | All API request schemas |
| Guardian Agent — injection scan | Prompt Injection | `agents/guardian/` |
| Guardian Agent — PII scan | Information Disclosure | `agents/guardian/` |
| MCP tool permission registry | Elevation of Privilege | `mcp/` permission layer |
| Append-only audit trail | Repudiation, Tampering | `backend/services/audit_service.py` |
| Human approval gate | Elevation of Privilege, Tampering | Guardian Agent + `backend/services/` |
| Secrets via environment variables | Information Disclosure | `backend/core/config.py` |
| CORS configuration | Spoofing | FastAPI middleware |
| Pinned dependencies | Supply Chain | `pyproject.toml`, `package.json` |
