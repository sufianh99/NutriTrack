<!-- GSD:project-start source:PROJECT.md -->
## Project

**NutriTrack**

Eine webbasierte Ernährungs-Tracking-Anwendung, die Nutzern hilft, ihren täglichen Energie- und Nährstoffbedarf individuell zu berechnen und ihre Ernährung datenbasiert zu tracken. Zwei Kernmodule: Bedarfsberechnung (Mifflin-St-Jeor) und Ernährungstracking mit Soll/Ist-Vergleich. Richtet sich an Personen, die Kalorienverbrauch und Makronährstoffzufuhr kontrollieren möchten.

**Core Value:** Nutzer können ihren individuellen Tagesbedarf berechnen und ihre tatsächliche Nahrungsaufnahme dagegen tracken — mit sofort sichtbarem Soll/Ist-Vergleich und farblicher Ampel.

### Constraints

- **Tech Stack**: Python/Flask, SQLite, Jinja2, pytest — Projektvorgabe
- **QA Tools**: Black, Ruff, Mypy — müssen in CI-Pipeline integriert sein
- **CI/CD**: GitHub Actions — Pflichtbestandteil der Abgabe
- **Diagramme**: Klassendiagramm + Sequenzdiagramm CI/CD — Pflicht-Nachweis
- **Tests**: Mindestens 5 Unit Tests + Integrationstests — Pflicht
- **Multi User**: Login/Registrierung mit Flask-Login, jeder Nutzer hat eigenes Profil und Tracking-Daten
<!-- GSD:project-end -->

<!-- GSD:stack-start source:research/STACK.md -->
## Technology Stack

## Recommended Stack
### Core Framework
| Technology | Current Version | Latest Stable | Purpose | Why |
|------------|----------------|---------------|---------|-----|
| Flask | 3.1.0 | **3.1.3** | Web framework | Project-constrained. 3.1.x is the active release series; update from 3.1.0 to 3.1.3 for bug fixes. Requires Python 3.9+. |
| Flask-SQLAlchemy | 3.1.1 | **3.1.1** | ORM / DB integration | Project-constrained. 3.1.1 is current; no update needed. Wraps SQLAlchemy 2.x with Flask lifecycle management. |
| Werkzeug | 3.1.3 | 3.x (bundled) | WSGI utilities | Flask dependency; version must track Flask. No direct dependency needed in requirements.txt — managed by Flask. |
| python-dotenv | 1.0.1 | **1.2.2** | Env-var / .env loading | Already in requirements.txt; update to 1.2.2 for Python 3.14 support and symlink fixes. |
### Database
| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| SQLite | stdlib (3.45+) | Persistent storage | Project-constrained. No server, zero ops, single-user app — SQLite is the correct choice. File lives in `instance/nutritrack.db`. |
| SQLAlchemy | 2.x (via Flask-SQLAlchemy 3.1.1) | ORM | Provides type-safe query API, migration path if DB ever changes. Use `db.session.get()` not deprecated `Model.query`. |
### Forms and Validation
| Technology | Current Version | Latest Stable | Purpose | Why |
|------------|----------------|---------------|---------|-----|
| Flask-WTF | 1.2.2 | **1.2.2** | Form classes + CSRF protection | Already in use; keep. CSRF protection matters even in single-user apps (browser-based XSRF). Provides `FlaskForm` base. |
| WTForms | (transitive via Flask-WTF) | — | Validators, field types | Do not import separately — let Flask-WTF manage the dependency. |
### QA Toolchain
| Tool | Latest Stable | Purpose | Why / Config |
|------|---------------|---------|--------------|
| Black | **26.3.1** | Code formatter | Project-constrained. Zero-config formatter; run as `black .` in CI. Add `[tool.black] line-length = 88` to `pyproject.toml`. |
| Ruff | **0.15.7** | Linter (replaces Flake8/isort) | Project-constrained. Written in Rust; 100x faster than Flake8. Covers pycodestyle, pyflakes, isort rules, and more. Configure in `pyproject.toml` under `[tool.ruff]`. |
| Mypy | **1.19.1** | Static type checker | Project-constrained. Use `--strict` is too aggressive for brownfield; start with `--ignore-missing-imports` and `--disallow-untyped-defs`. Add `py.typed` marker if distributing. |
### Testing
| Tool | Latest Stable | Purpose | Why |
|------|---------------|---------|-----|
| pytest | **9.0.2** | Test runner | Project-constrained. De facto standard. Use `conftest.py` with `app` and `client` fixtures. |
| pytest-flask | **1.3.0** | Flask test fixtures | Provides `live_server`, `client`, and `app` fixtures. Version 1.3.0 added Flask 3.0 compatibility (removed deprecated `request_ctx`). Use `@pytest.mark.usefixtures("app")`. |
### Open Food Facts Integration
| Technology | Latest Stable | Purpose | Why |
|------------|---------------|---------|-----|
| openfoodfacts | **5.0.1** | Product search / nutrition lookup | Official Python SDK from the OFF project. Production/Stable as of March 2026. Provides `API.product.text_search(query)` and `API.product.get(barcode)`. Pin exact version. |
| requests | **2.32.5** | HTTP fallback / raw API calls | Only needed if NOT using the `openfoodfacts` SDK. Prefer SDK — it handles rate limiting and response normalization. Keep as transitive dependency. |
# results["products"] → list of dicts with "nutriments" key
# nutriments: {"energy-kcal_100g": ..., "proteins_100g": ..., "fat_100g": ..., "carbohydrates_100g": ...}
### CI/CD
| Technology | Purpose | Why |
|------------|---------|-----|
| GitHub Actions | CI pipeline | Project-constrained. Use `ubuntu-latest` runner. Recommended job order: `black --check .` → `ruff check .` → `mypy app/` → `pytest`. |
## Libraries to REMOVE from This Project
| Library | Reason to Remove | What Replaces It |
|---------|-----------------|------------------|
| Flask-Login 0.6.3 | Auth is explicitly out of scope ("Won't Have"). Removing eliminates `login_required` decorators, `current_user` references, `LoginManager`, and `UserMixin`. | Session variable or `g` object for single-user profile state. |
| `email-validator` (transitive via Flask-WTF Email()) | Only needed for RegistrationForm / LoginForm which are deleted. | Nothing — those forms are removed. |
## Data Model Changes Required
## Mifflin-St-Jeor Implementation Pattern
# app/calculator.py
## Alternatives Considered
| Category | Recommended | Alternative | Why Not |
|----------|-------------|-------------|---------|
| ORM | Flask-SQLAlchemy | Raw SQLite (sqlite3) | SQLAlchemy 2.x Mapped[] types give Mypy compatibility for free; no migration needed as it's already in use |
| Form handling | Flask-WTF | Raw HTML forms + request.form | Flask-WTF CSRF protection is worth the dependency even for single-user; already integrated |
| API client | openfoodfacts SDK | Direct requests to api.openfoodfacts.org | SDK handles response normalization, field naming inconsistencies, and is maintained by OFF team |
| Type checking | Mypy | Pyright | Mypy is the project constraint; Pyright has better IDE integration but Mypy is sufficient for CI |
| Linter | Ruff | Flake8 + isort + pylint | Ruff replaces all three at 100x speed; Flake8 is effectively deprecated for new projects |
## Final requirements.txt (Recommended)
# Runtime
# requirements-dev.txt
## Sources
- Flask PyPI: https://pypi.org/project/Flask/ (verified March 2026, version 3.1.3)
- Flask-SQLAlchemy PyPI: https://pypi.org/project/Flask-SQLAlchemy/ (verified March 2026, version 3.1.1)
- Flask-WTF PyPI: https://pypi.org/project/Flask-WTF/ (verified March 2026, version 1.2.2)
- openfoodfacts PyPI: https://pypi.org/project/openfoodfacts/ (verified March 2026, version 5.0.1)
- openfoodfacts Python SDK usage docs: https://openfoodfacts.github.io/openfoodfacts-python/usage/
- pytest PyPI: https://pypi.org/project/pytest/ (verified March 2026, version 9.0.2)
- pytest-flask PyPI: https://pypi.org/project/pytest-flask/ (verified March 2026, version 1.3.0)
- Black PyPI: https://pypi.org/project/black/ (verified March 2026, version 26.3.1)
- Ruff PyPI: https://pypi.org/project/ruff/ (verified March 2026, version 0.15.7)
- Mypy PyPI: https://pypi.org/project/mypy/ (verified March 2026, version 1.19.1)
- python-dotenv PyPI: https://pypi.org/project/python-dotenv/ (verified March 2026, version 1.2.2)
- Flask official docs — project layout: https://flask.palletsprojects.com/en/stable/tutorial/layout/
- Flask official docs — testing: https://flask.palletsprojects.com/en/stable/testing/
- Ruff FAQ (Black overlap guidance): https://docs.astral.sh/ruff/faq/
<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->
## Conventions

Conventions not yet established. Will populate as patterns emerge during development.
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->
## Architecture

Architecture not yet mapped. Follow existing patterns found in the codebase.
<!-- GSD:architecture-end -->

<!-- GSD:workflow-start source:GSD defaults -->
## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:
- `/gsd:quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd:debug` for investigation and bug fixing
- `/gsd:execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->



<!-- GSD:profile-start -->
## Developer Profile

> Profile not yet configured. Run `/gsd:profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->
