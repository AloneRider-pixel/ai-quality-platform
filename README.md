# AI Quality Engineering & API Automation Platform

[![CI](https://github.com/AloneRider-pixel/ai-quality-platform/actions/workflows/ci.yml/badge.svg)](https://github.com/AloneRider-pixel/ai-quality-platform/actions/workflows/ci.yml)
[![CodeQL](https://github.com/AloneRider-pixel/ai-quality-platform/actions/workflows/codeql.yml/badge.svg)](https://github.com/AloneRider-pixel/ai-quality-platform/actions/workflows/codeql.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Reusable test-engineering platform for API, integration, contract, deterministic LLM-quality, and performance validation.

## What it demonstrates

- Shared clients, fixtures, assertions, and data factories.
- Authentication, CRUD, pagination, and negative-path testing.
- Contract validation for API schemas.
- Deterministic RAG, hallucination, and prompt-regression tests.
- Locust load/stress/spike/sustained scenarios.
- HTML/JUnit reporting and Prometheus/Grafana integration.
- Fail-closed CI stages with explicit quality gates.

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

Use workload values as examples; they are not production capacity benchmarks.

## Quality-gate contract

Credentialed live-provider tests are separate from deterministic CI. Never change a required stage just to make a failing run pass. Fix the underlying test, fixture, configuration, dependency, or environment issue.

## Evaluation integrity

Deterministic fixtures validate the harness and regression behavior. They do not establish production model quality. Published AI-quality or performance results should identify provider/model, dataset version, sample count, configuration, timestamp, environment, workload, and producing commit.

## Security

Keep provider/API credentials outside the repository. Treat test payloads, mock responses, model output, and external API data as untrusted. Preserve least-privilege CI permissions and immutable action references.

## Documentation

- [Verification](docs/verification.md)
- [Deterministic evaluation](docs/deterministic-evaluation.json)
- [Engineering notes](docs/ENGINEERING_NOTES.md)

## Contribution standard

New test utilities should be deterministic where possible, failures should remain observable, and quality gates should stay tied to meaningful assertions rather than coverage-only targets.

## Roadmap

Versioned regression datasets, OpenTelemetry correlation, broader contract integrations, and distributed load generation.

## License

MIT
