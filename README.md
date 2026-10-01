# 🧪 AI Quality Engineering & API Automation Platform

[![CI](https://github.com/AloneRider-pixel/ai-quality-platform/actions/workflows/ci.yml/badge.svg)](https://github.com/AloneRider-pixel/ai-quality-platform/actions/workflows/ci.yml)
[![CodeQL](https://github.com/AloneRider-pixel/ai-quality-platform/actions/workflows/codeql.yml/badge.svg)](https://github.com/AloneRider-pixel/ai-quality-platform/actions/workflows/codeql.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Test-engineering platform covering API, integration, contract, deterministic LLM-quality, and performance validation.

## Test architecture

```text
Mock APIs / LLM fixtures
          ↓
      Pytest framework
      ├── API tests
      ├── integration tests
      ├── contract tests
      └── LLM regression tests
          ↓
      Locust workloads
          ↓
      GitHub Actions
          ↓
      Reports + quality gates
```

## What it demonstrates

- Reusable fixtures, clients, assertions, and data factories.
- API validation for authentication, CRUD, pagination, and error handling.
- Contract checks for API schemas.
- Deterministic RAG, hallucination, and prompt-regression tests.
- Locust load, stress, spike, and sustained workload scenarios.
- HTML/JUnit reporting plus Prometheus/Grafana instrumentation.
- Fail-closed CI quality gating for required stages.

## Stack

| Layer | Technology |
|---|---|
| Framework | Python 3.11, Pytest, pytest-asyncio |
| API | HTTPX, Requests, Schemathesis |
| AI quality | OpenAI-compatible fixtures, LangChain/RAG tooling |
| Performance | Locust |
| Mocking | FastAPI, Respx |
| Reporting | Pytest-HTML, Allure |
| Observability | Prometheus, Grafana |
| CI | GitHub Actions |

## Repository layout

```text
framework/              # Reusable test abstractions
tests/api/
tests/integration/
tests/contract/
tests/llm/
tests/performance/
mocks/
reporting/
dashboard/
pytest.ini
requirements.txt
.github/workflows/
```

## Quick start

```bash
git clone https://github.com/AloneRider-pixel/ai-quality-platform.git
cd ai-quality-platform
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run deterministic tests:

```bash
pytest tests/ -v
```

Load test:

```bash
locust -f tests/performance/locustfile.py --headless -u 100 -r 10 -t 60s
```

## CI model

The workflow runs smoke, API, deterministic LLM, integration, and load stages, followed by a quality gate. Credentialed live-provider tests are intentionally separate from deterministic CI.

## Evaluation integrity

Deterministic fixtures validate the test harness and regression behavior; they do not establish production model quality. A live benchmark should record provider/model, dataset version, sample count, configuration, timestamp, environment, and commit.

## Reporting

```bash
pytest tests/ -v --html=reports/report.html
docker compose up -d grafana prometheus
```

## Roadmap

- Versioned evaluation datasets and explicit regression thresholds.
- OpenTelemetry test-to-service correlation.
- Broader contract-testing integrations.
- Distributed load generation.

## Review path

Start with [verification](docs/verification.md) and [deterministic-evaluation.json](docs/deterministic-evaluation.json). Review the CI quality gate before modifying which stages are considered required.

## Maintenance standard

Keep test inputs deterministic, isolate credentials, and never convert synthetic fixture scores into production-quality claims.

## License

MIT
