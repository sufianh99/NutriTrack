---
phase: quick
plan: 260409-sut
subsystem: scripts
tags: [refactor, monitor, ci, beginner-simplification]
dependency_graph:
  requires: []
  provides: [simplified-monitor-script]
  affects: [.github/workflows/ci.yml]
tech_stack:
  added: []
  patterns: [flat-linear-script, string-concatenation, single-try-except]
key_files:
  created: []
  modified:
    - scripts/monitor.py
decisions:
  - "Use string concatenation over f-strings for beginner appearance"
  - "Single try/except catches all exceptions — no retry, no separate ConnectionError/Timeout handling"
metrics:
  duration: "< 5 minutes"
  completed: "2026-04-09"
  tasks: 1
  files: 1
---

# Quick Task 260409-sut: Simplify monitor.py to Beginner Level — Summary

**One-liner:** Rewrote scripts/monitor.py from 87-line professional script to 20-line flat beginner script — removes retry logic, functions, type hints, constants block, and module docstring while preserving CI contract.

---

## What Was Done

Replaced the contents of `scripts/monitor.py` with a simple, flat, top-to-bottom script a Python beginner would write.

**Removed:**
- Module-level docstring (12-line triple-quoted block)
- 5 module-level constants: `PROD_URL`, `HEALTH_ENDPOINT`, `TIMEOUT`, `MAX_RETRIES`, `RETRY_DELAY`
- `check_health()` function with typed dict return (`dict[str, object]`)
- `main()` function and `if __name__ == "__main__": main()` guard
- Retry loop (`for attempt in range(1, MAX_RETRIES + 1)`)
- `time.sleep(RETRY_DELAY)` and `import time`
- All type hints (`-> dict[str, object]`, `-> None`)

**Kept / implemented:**
- `import os`, `import sys`, `import requests`
- `url = os.environ.get("NUTRITRACK_URL", "https://nutritrack.onrender.com")`
- `url = url + "/health"` (builds health endpoint inline)
- Single `try/except Exception` block around one `requests.get(url, timeout=10)` call
- German print output: `"Pruefe " + url + " ..."` / `"Ergebnis: OK"` / `"Ergebnis: FEHLER - " + ...`
- `sys.exit(0)` on HTTP 200, `sys.exit(1)` on non-200 or exception
- `.github/workflows/ci.yml` — untouched

---

## Commits

| Task | Description | Commit |
|------|-------------|--------|
| 1 | Rewrite monitor.py as simple beginner script | 7ab156f |

---

## Deviations from Plan

None — plan executed exactly as written.

---

## Known Stubs

None.

---

## Self-Check: PASSED

- `scripts/monitor.py` exists and is valid Python (syntax check passed)
- All plan assertions passed: no `def`, no `retry`, no `->`, no `dict[`, no `MAX_RETRIES`, has `NUTRITRACK_URL`, has `/health`, has `sys.exit(0)`, has `sys.exit(1)`, no `import time`
- Commit `7ab156f` exists in git log
- `.github/workflows/ci.yml` unchanged
