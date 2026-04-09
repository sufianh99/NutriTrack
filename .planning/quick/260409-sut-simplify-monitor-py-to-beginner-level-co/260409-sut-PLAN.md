---
phase: quick
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - scripts/monitor.py
autonomous: true
requirements: []
must_haves:
  truths:
    - "monitor.py reads NUTRITRACK_URL from env (with fallback) and requests /health"
    - "Prints German status output and exits 0 on success, 1 on failure"
    - "No retry logic, no constants block, no type hints, no docstring, no dict return"
    - "CI pipeline (ci.yml) continues to work without changes"
  artifacts:
    - path: "scripts/monitor.py"
      provides: "Simplified beginner-level health check script"
  key_links:
    - from: "scripts/monitor.py"
      to: ".github/workflows/ci.yml"
      via: "python scripts/monitor.py invocation with NUTRITRACK_URL env var"
      pattern: "os\\.environ\\.get.*NUTRITRACK_URL"
---

<objective>
Rewrite scripts/monitor.py to look like a beginner wrote it: a simple linear script with no advanced patterns.

Purpose: The current monitor.py uses professional patterns (retry logic, module-level constants, typed dict returns, docstrings, type hints) that are overengineered for what the CI pipeline actually needs. Simplify it to a straightforward script a Python beginner would write.

Output: A simplified scripts/monitor.py that still works in CI (reads NUTRITRACK_URL, hits /health, prints German output, exits 0 or 1).
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@scripts/monitor.py
@.github/workflows/ci.yml (lines 55-73 — the smoke-test job that calls monitor.py)
</context>

<tasks>

<task type="auto">
  <name>Task 1: Rewrite monitor.py as a simple beginner script</name>
  <files>scripts/monitor.py</files>
  <action>
Replace the entire contents of scripts/monitor.py with a simple linear script. Requirements:

REMOVE all of these:
- The module-level docstring (the triple-quoted block at the top)
- The module-level constants (PROD_URL, HEALTH_ENDPOINT, TIMEOUT, MAX_RETRIES, RETRY_DELAY)
- The `check_health()` function and its dict return structure
- The `main()` function wrapper
- All type hints (`: dict[str, object]`, `-> None`, etc.)
- The retry loop (`for attempt in range(...)` and `time.sleep`)
- The `import time` statement
- The `if __name__ == "__main__": main()` guard

KEEP / implement:
- `import os`, `import sys`, `import requests`
- Read URL from env: `url = os.environ.get("NUTRITRACK_URL", "https://nutritrack.onrender.com")`
- Build health URL: `url = url + "/health"`
- Single `try/except` block around one `requests.get(url, timeout=10)` call
- On success (status 200): print "OK" line in German, `sys.exit(0)`
- On non-200: print "FEHLER" line with status code in German, `sys.exit(1)`
- On exception: print "FEHLER" with error message in German, `sys.exit(1)`
- German print output like: `print("Pruefe " + url + " ...")` and `print("Ergebnis: OK")` or `print("Ergebnis: FEHLER - " + str(antwort.status_code))`

The script should be roughly 15-20 lines, flat (no functions), and read top-to-bottom like a beginner's first script. Use simple string concatenation (not f-strings) where it looks more beginner-like, but f-strings are also acceptable — just keep it simple.

Do NOT touch .github/workflows/ci.yml.
  </action>
  <verify>
    <automated>cd C:/Repos/NutriTrack && python -c "import ast; ast.parse(open('scripts/monitor.py').read()); print('Syntax OK')" && python -c "
content = open('scripts/monitor.py').read()
assert 'def ' not in content, 'No functions allowed'
assert 'retry' not in content.lower(), 'No retry logic'
assert '-> ' not in content, 'No return type hints'
assert 'dict[' not in content, 'No typed dicts'
assert 'MAX_RETRIES' not in content, 'No retry constants'
assert 'NUTRITRACK_URL' in content, 'Must read env var'
assert '/health' in content, 'Must hit /health endpoint'
assert 'sys.exit(0)' in content, 'Must exit 0 on success'
assert 'sys.exit(1)' in content, 'Must exit 1 on failure'
assert 'import time' not in content, 'No time import'
print('All checks passed')
"</automated>
  </verify>
  <done>scripts/monitor.py is a simple, flat, beginner-level script (~15-20 lines) with no functions, no retry logic, no type hints, no docstring, no constants block. It reads NUTRITRACK_URL from env, makes one request to /health, prints German output, and exits 0/1. CI pipeline is unchanged.</done>
</task>

</tasks>

<verification>
1. `python -c "import ast; ast.parse(open('scripts/monitor.py').read())"` — valid Python
2. No `def` keyword in file — no functions
3. No `retry`, `MAX_RETRIES`, `RETRY_DELAY` — no retry logic
4. No type hints (`->`, `dict[`)
5. No docstring at module level
6. NUTRITRACK_URL env var still read
7. /health endpoint still targeted
8. sys.exit(0) on success, sys.exit(1) on failure
9. .github/workflows/ci.yml unchanged
</verification>

<success_criteria>
scripts/monitor.py looks like a Python beginner wrote it: flat linear script, no advanced patterns, German output, works in CI pipeline unchanged.
</success_criteria>

<output>
After completion, create `.planning/quick/260409-sut-simplify-monitor-py-to-beginner-level-co/260409-sut-SUMMARY.md`
</output>
