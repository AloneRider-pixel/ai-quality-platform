# AI Quality Engineering & API Automation Platform

[![CI](https://github.com/AloneRider-pixel/ai-quality-platform/actions/workflows/ci.yml/badge.svg)](https://github.com/AloneRider-pixel/ai-quality-platform/actions/workflows/ci.yml)
[![CodeQL](https://github.com/AloneRider-pixel/ai-quality-platform/actions/workflows/codeql.yml/badge.svg)](https://github.com/AloneRider-pixel/ai-quality-platform/actions/workflows/codeql.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Reusable test-engineering platform for API, integration, contract, deterministic LLM-quality, and performance validation.

## Test architecture

```text
Mock APIs / deterministic fixtures
          ↓
Reusable Pytest framework
    ├── API
    ├── integration
    ├── contract
    └── LLM regression
          ↓
      Locust workloads
          ↓
   GitHub Actions
          ↓
 Reports + quality gates
```

## What it demonstrates

- Shared clients, fixtures, assertions, and data factories.
- Authentication, CRUD, pagination, and error-path testing.
- Contract validation for API schemas.
- Deterministic RAG, hallucination, and prompt-regression tests.
- Locust load/stress/spike/sustained scenarios.
- HTML/JUnit reporting and Prometheus/Grafana integration.
- Fail-closed CI stages with an explicit quality gate.

## Stack

| Area | Technology |
|---|---|
| Test framework | Python 3.12, Pytest, pytest-asyncio |
| API testing | HTTPX, Requests, Schemathesis |
| AI quality | deterministic provider-compatible fixtures, RAG tooling |
| Performance | Locust |
| Mocking | FastAPI, Respx |
| Reporting | Pytest-HTML, Allure |
| Observability | Prometheus, Grafana |
| CI | GitHub Actions |

## Repository map

```text
framework/
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
pytest tests/ -v
```

Load testing:

```bash
locust -f tests/performance/locustfile.py --headless -u 100 -r 10 -t 60s
```

## Quality-gate contract

Credentialed live-provider tests are separate from deterministic CI. Do not change a required stage to make a failing run pass; fix the underlying test, fixture, configuration, or dependency problem.

## Evaluation integrity

Deterministic fixtures validate harness behavior and regressions. They do not establish production model quality. Any published AI-quality result should state provider/model, dataset version, sample count, configuration, timestamp, environment, and producing commit.

## Security

Keep provider/API credentials outside the repository. Treat test payloads, mock responses, and external API data as untrusted. Preserve least-privilege CI permissions and immutable action references.

## Documentation

- [Verification](docs/verification.md)
- [Deterministic evaluation](docs/deterministic-evaluation.json)
- [Engineering notes](docs/ENGINEERING_NOTES.md)

## Roadmap

Versioned regression datasets, OpenTelemetry correlation, broader contract integrations, and distributed load generation.

## License

MIT
