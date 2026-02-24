# Deployment Runbook (Manual)

## Purpose and scope

This runbook defines the exact **manual** release steps for NewsNexus in two environments:

- **Preprod** (staging-like validation environment).
- **Prod** (customer-facing production environment).

It is intentionally explicit so an engineer, QA lead, or operations owner can execute the same process repeatedly with low ambiguity. It also maps each step to code/config touchpoints in `config.py`, `database/connection.py`, and `app.py` for traceability.

---

## Preprod

### 1) Prerequisites (must be true before any deployment action)

1. You are on the correct branch/tag to promote.
2. You have shell access to the preprod host/container and permission to restart the app process.
3. Python environment dependencies are installed and lock file is in sync (`pyproject.toml` / `uv.lock`).
4. PostgreSQL preprod instance is reachable from the app runtime.
5. A backup/snapshot path exists for preprod data (even if lower criticality than prod).
6. Release notes are reviewed for DB-impacting or integration-impacting changes.

### 2) Required secrets and service environment keys

Set/verify these keys in the preprod runtime environment before starting the app:

**Core app + data path (required)**
- `DATABASE_URL` (primary DB connection key used by `database/connection.py`).
- or PostgreSQL component keys: `PGHOST`, `PGPORT`, `PGDATABASE`, `PGUSER`, `PGPASSWORD` (defined in `config.py` for configuration consistency checks).
- `OPENAI_API_KEY`.

**Business/integration services (required if those features are enabled for preprod test scope)**
- `STRIPE_SECRET_KEY`.
- `STRIPE_WEBHOOK_SECRET`.
- `PAYPAL_CLIENT_ID`.
- `PAYPAL_CLIENT_SECRET`.
- `ZOHO_CLIENT_ID`.
- `ZOHO_CLIENT_SECRET`.
- `GOOGLE_MAPS_API_KEY`.
- `IPINFO_API_KEY`.

**Operational behavior**
- `DEBUG=False` unless intentionally running a controlled debugging session.

### 3) DB readiness checks (manual)

Run these checks from a shell with the preprod environment loaded:

1. Confirm DB target is not accidentally local SQLite fallback:
   ```bash
   python -c "import os; print(os.getenv('DATABASE_URL',''))"
   ```
   - Must be non-empty and must not be `sqlite:///./newsnexus.db` for shared preprod.

2. Connectivity check:
   ```bash
   python -c "from database.connection import engine; conn=engine.connect(); print('db-ok'); conn.close()"
   ```

3. Schema readiness check (ensures table metadata can be applied without crash):
   ```bash
   python -c "from database.connection import init_database; init_database(); print('schema-ok')"
   ```

4. Optional sanity SQL from psql:
   ```bash
   psql "$DATABASE_URL" -c "select now();"
   ```

### 4) App deployment command (manual)

Use this exact sequence:

```bash
# 1) Update code
cd /path/to/NewsNexus

git fetch --all --tags
git checkout <release-branch-or-tag>
git pull --ff-only

# 2) Sync dependencies
pip install -e .

# 3) Start/restart application
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

If a process manager is used (systemd/supervisor/container orchestration), run the equivalent controlled restart and verify the service returns healthy status.

### 5) Smoke-check checklist (must pass before preprod sign-off)

1. App starts without import/runtime crash (`app.py` executes and calls `init_database()`).
2. Home page renders and navigation tabs load.
3. Authentication flow can be opened (login trigger path reachable).
4. News feed loads at least one category without fatal error.
5. If payments are in scope: payment service initialization does not raise configuration errors.
6. If geo is in scope: location-dependent features render without hard failure.
7. No sensitive values are shown in UI, logs, or traceback messages.

### 6) Rollback actions (preprod)

If smoke checks fail:

1. Stop current app process.
2. Checkout previous known-good tag/commit:
   ```bash
   git checkout <previous-known-good-tag>
   ```
3. Reinstall dependencies if needed:
   ```bash
   pip install -e .
   ```
4. Restart Streamlit service.
5. Re-run minimum smoke checks (app start + homepage + DB connectivity).
6. Record rollback cause in release log and open follow-up bug.

### 7) Post-deploy monitoring checks (first 30–60 minutes)

1. Watch app logs for repeated exceptions/timeouts.
2. Confirm DB connection errors are absent.
3. Verify external API failure rates are within expected test bounds.
4. Spot-check user flow latency (home load, news fetch, profile/settings navigation).
5. Document observations in deployment note with timestamp and owner.

### 8) Sign-off checkpoints (preprod)

- **Engineering sign-off**: deployment + technical smoke checks complete.
- **QA sign-off**: acceptance scenario checklist passed.
- **Operations sign-off**: runtime stability and observability checks complete.

Preprod promotion to prod is blocked until all three sign-offs are recorded.

---

## Prod

### 1) Prerequisites (strict)

1. Preprod sign-offs from Engineering, QA, and Operations are complete.
2. Change window is approved and incident/on-call contacts are active.
3. Production DB backup/snapshot completed and validated.
4. Rollback version/tag is identified before deployment starts.
5. Monitoring dashboards and alert channels are open during deployment.

### 2) Required secrets and service environment keys (production-validated)

Verify all keys below are populated with **production** values (never preprod values):

- `DATABASE_URL` (primary runtime DB key from `database/connection.py`).
- `PGHOST`, `PGPORT`, `PGDATABASE`, `PGUSER`, `PGPASSWORD` (as cross-checks, if used by platform tooling).
- `OPENAI_API_KEY`.
- `STRIPE_SECRET_KEY`.
- `STRIPE_WEBHOOK_SECRET`.
- `PAYPAL_CLIENT_ID`.
- `PAYPAL_CLIENT_SECRET`.
- `ZOHO_CLIENT_ID`.
- `ZOHO_CLIENT_SECRET`.
- `GOOGLE_MAPS_API_KEY`.
- `IPINFO_API_KEY`.
- `DEBUG=False`.

### 3) DB readiness checks (manual, production-safe)

1. Confirm active target DB:
   ```bash
   python -c "import os; print('db-url-set' if os.getenv('DATABASE_URL') else 'db-url-missing')"
   ```
2. Connectivity check from runtime:
   ```bash
   python -c "from database.connection import engine; conn=engine.connect(); print('db-ok'); conn.close()"
   ```
3. Safe schema readiness path:
   ```bash
   python -c "from database.connection import init_database; init_database(); print('schema-ok')"
   ```
4. Confirm critical table visibility:
   ```bash
   psql "$DATABASE_URL" -c "\dt"
   ```

### 4) App deployment command (manual, controlled)

```bash
# 1) Pin to release artifact
cd /path/to/NewsNexus

git fetch --all --tags
git checkout <approved-release-tag>

# 2) Install exact app dependencies
pip install -e .

# 3) Restart the production app process
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

If your platform uses a process manager, use the manager-native restart command with equivalent effect and capture service status after restart.

### 5) Smoke-check checklist (production)

1. Landing page responds over production URL.
2. App startup is clean (no crash loop, no import error).
3. Authentication entry points are reachable.
4. News retrieval works for at least two categories.
5. Database-backed reads execute without visible errors.
6. Payment and subscription-related pages load without key/config exceptions.
7. Logs contain no secret exposure and no sustained error burst.

### 6) Rollback actions (production)

If any critical smoke check fails or major user-facing issue appears:

1. Announce rollback in incident/release channel.
2. Switch code to last known-good release tag:
   ```bash
   git checkout <last-known-good-prod-tag>
   pip install -e .
   ```
3. Restart app process and verify service health.
4. Re-run production smoke checks (minimum critical path: home, login entry, news load, DB read).
5. If schema/data issue exists, execute pre-approved DB rollback/restore playbook.
6. Keep incident open until Engineering + Operations confirm restored steady-state behavior.

### 7) Post-deploy monitoring checks (production)

Monitor at high frequency for at least 60 minutes:

1. Application error rate and exception signatures.
2. DB connection pool/latency symptoms.
3. External dependency health (OpenAI, payment processors, geo providers).
4. User-facing latency on key pages (home, news feed, profile/settings).
5. Business-critical signal checks: subscription flow reachability, affiliate/product views, analytics ingestion.

Record final status with timeline notes and unresolved risks.

### 8) Sign-off checkpoints (production)

- **Engineering sign-off**: production deploy and technical verification complete.
- **QA sign-off**: production smoke checklist executed and passed.
- **Operations sign-off**: monitoring stable, alerting normal, rollback no longer required.

Production deployment is complete only when all three sign-offs are captured.

---

## Code/config touchpoint reference

Use this mapping when validating deployment assumptions:

- `config.py`: source of core environment key names used across app configuration.
- `database/connection.py`: runtime DB URL selection, SQLAlchemy engine creation, and `init_database()` schema bootstrapping.
- `app.py`: primary Streamlit entrypoint and startup behavior (`init_database()` call at startup).
- Service env keys:
  - AI: `OPENAI_API_KEY`.
  - Payments: `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `PAYPAL_CLIENT_ID`, `PAYPAL_CLIENT_SECRET`.
  - CRM/Integrations: `ZOHO_CLIENT_ID`, `ZOHO_CLIENT_SECRET`.
  - Geo: `GOOGLE_MAPS_API_KEY`, `IPINFO_API_KEY`.
