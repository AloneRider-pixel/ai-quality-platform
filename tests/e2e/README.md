# Browser E2E tests (Playwright)

End-to-end browser tests for the owner's own apps, run against **locally
started instances with deterministic seed data**. This layer fills the gap
named in `requirements.txt` ("UI Testing": playwright) with a real suite.

## What it covers

| Target app | Started as | Flows |
|---|---|---|
| fraud-detection-engine | local uvicorn + model trained from synthetic data (fixed seed) | demo page load, sample scoring, numeric form validation, error banner on rejected score |
| learning-path-lab-yottaflex | local stdlib server, generated starter dataset (fixed seed) | planner load, employee search, plan build, invalid-hours error banner |
| stocksense-ai | local backend (SQLite, CSV provider, seeded demo mode) + built frontend via `vite preview` | landing load, demo sign-in, dashboard symbol list, symbol overview |

Hard rules: no real signups, no account logins, no orders and no writes
against any live or shared system. The StockSense sign-in uses the app's own
seeded demo reviewer account on the local instance only.

## Running locally

```bash
pip install -r requirements.txt
playwright install chromium
scripts/e2e_targets_setup.sh        # clones the pinned target checkouts once
pytest tests/e2e -m "e2e and not live"
```

Target checkouts live in `.e2e-targets/` (git-ignored) and are pinned by SHA
in `tests/e2e/targets.lock.json`. Bump a SHA deliberately, in its own commit.

## Reports and artifacts

`--html=reports/e2e_report.html` (pytest-html) plus JUnit XML, and failure
screenshots/traces under `reports/e2e-artifacts/` via pytest-playwright's
`--screenshot only-on-failure --output`. Target-app server logs land in the
same directory. CI uploads all of `reports/` on every run, pass or fail.

## Quarantine

A flaky test goes into `tests/e2e/quarantine.txt` with a reason:

```
tests/e2e/test_stocksense.py::test_symbol_overview_renders - flakes when the vite preview is slow to serve the bundle
```

Quarantined tests **still run and still appear in the report**; a failure is
recorded as an xfail so one flaky browser test cannot block the gate, and an
unexpected pass shows up as XPASS. A test graduates by removing the entry in
the same PR as its fix. The mechanism itself is unit-tested in
`tests/framework/test_e2e_quarantine.py`.

## Live smoke (read-only, opt-in)

`tests/e2e/live/` holds read-only smoke checks for the public demo
deployments. They run only when `E2E_LIVE=1` is set, which CI does only in
`.github/workflows/e2e-live-smoke.yml`, a scheduled workflow gated on the
`E2E_LIVE_SMOKE_ENABLED` repository variable. Until the owner approves
watching the live demos and sets that variable, the workflow is inert.
Checks are page loads and GETs only, with cold-start waits reported in the
output.
