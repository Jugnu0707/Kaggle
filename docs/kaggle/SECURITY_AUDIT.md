# Oz AI — Security Audit

**Audit date:** 2026-06-28  
**Scope:** Full repository (tracked and untracked files visible in workspace)  
**Method:** Pattern search, git inventory, config review

---

## Summary

**No committed production secrets were found.** The repository follows standard hygiene: `.env` is gitignored, `.env.example` contains empty placeholders, and Docker Compose sets `GOOGLE_API_KEY: ""`. One synthetic Google API key pattern exists in a unit test fixture only.

**Application security limitations** (unauthenticated API, no RBAC) are architectural gaps documented in `docs/kaggle/limitations.md`, not secret leaks.

---

## Search coverage

| Category | Patterns / paths searched |
|----------|---------------------------|
| Google API keys | `AIza…` pattern |
| OpenAI / generic keys | `sk-…`, `api_key`, `API_KEY` |
| Credentials | `password=`, `secret=`, `token=` |
| Private keys | `BEGIN PRIVATE KEY`, `.pem`, `.key` |
| Environment files | `.env`, `.env.local`, `.env.*` |
| Cloud providers | AWS, Azure, OCI references in config |

---

## Findings

### 1. Synthetic test fixture (informational)

| Item | Detail |
|------|--------|
| **File** | `agents/guardian/tests/test_secret_detector.py` |
| **Content** | `AIzaSyAbcdefghijklmnopqrstuvwxyz123456` |
| **Risk** | **None** — invalid placeholder used to test secret detection |
| **Action** | No removal required |

### 2. Environment template (expected)

| Item | Detail |
|------|--------|
| **File** | `.env.example` (tracked) |
| **Content** | `GOOGLE_API_KEY=` (empty) |
| **Risk** | **None** |
| **Action** | Keep; document for users |

### 3. Gitignored secrets path (expected)

| Item | Detail |
|------|--------|
| **File** | `.env` |
| **Status** | Listed in `.gitignore`; not tracked by git |
| **Risk** | **None in repo** — users must not commit local `.env` |
| **Action** | Verify before every push |

### 4. Docker Compose defaults (expected)

| Item | Detail |
|------|--------|
| **File** | `docker-compose.yml` |
| **Content** | `GOOGLE_API_KEY: ""` |
| **Risk** | **None** |
| **Action** | Users inject key via env override at deploy time |

### 5. Test mocks (expected)

| Item | Detail |
|------|--------|
| **Files** | `tests/test_risk_agent.py`, `tests/test_ai_runtime.py`, etc. |
| **Content** | `mock_provider.get_api_key.return_value = "test-key"` |
| **Risk** | **None** |
| **Action** | No change |

---

## Git tracked sensitive paths

```
.env.example          ← template only (empty key)
agents/guardian/secret_detector.py
agents/guardian/tests/test_secret_detector.py
```

**No `.env`, `.pem`, `.key`, or credential JSON files are tracked.**

---

## Guardian and secret handling (implemented)

| Control | Location |
|---------|----------|
| Secret detection | `agents/guardian/secret_detector.py` |
| PII masking | `agents/guardian/pii_detector.py` |
| Prompt injection checks | `agents/guardian/prompt_injection.py` |
| Config flags | `MASK_SECRETS`, `MASK_PII` in `.env.example` |
| Replay export sanitization | Documented in Guardian / replay services |

---

## Application security posture (not secret-related)

| Control | Status |
|---------|--------|
| API authentication | **Not implemented** |
| RBAC | **Not implemented** |
| Rate limiting | **Not implemented** |
| HTTPS termination | Deployment responsibility |
| Secret storage | Environment variables only |

These are documented limitations, not repository leaks.

---

## Recommendations

1. **Before submission:** Run `git log -p` spot-check for accidental `.env` commits (none found in current tree).
2. **Before demo recording:** Never display real `GOOGLE_API_KEY` on screen (see `docs/demo/recording_checklist.md`).
3. **Optional hardening:** Add GitHub Actions secret scanning and a pre-commit hook blocking `.env` commits.
4. **Do not commit:** `demo/output/`, local SQLite databases, or uploaded logs in `storage/uploads/`.

---

## Verdict

**PASS for submission** — no exposed credentials in the repository. Continue excluding `.env` and local runtime artifacts from version control.
