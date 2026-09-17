# 🧪 AI Quality Engineering & API Automation Platform

[![CI](https://github.com/AloneRider-pixel/ai-quality-platform/actions/workflows/ci.yml/badge.svg)](https://github.com/AloneRider-pixel/ai-quality-platform/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Test engineering platform for APIs, AI/LLM applications, browser flows, and performance.**

> **Portfolio focus:** Pytest architecture + API automation + LLM evaluation + contract testing + performance engineering + CI/CD.

## Architecture

```text
APIs / LLM endpoints / web apps
              ↓
       Pytest framework
       ├── API tests
       ├── integration tests
       ├── contract tests
       ├── LLM evaluations
       └── Playwright UI tests
              ↓
        Locust load tests
              ↓
       GitHub Actions CI
              ↓
   Reports + quality metrics
```

## What this project demonstrates

### Test architecture
- Reusable fixtures, clients, assertions, and data factories.
- API coverage for CRUD, validation, authentication, pagination, and error handling.
- Integration tests for multi-service workflows.
- Contract testing for schema compatibility.
- Playwright-based browser automation.

### AI/LLM quality
- RAG evaluation for faithfulness, relevance, recall, and precision.
- Hallucination checks.
- Prompt-regression tests against golden cases.
- Embedding-based semantic comparison.
- Content-safety scoring.

### Performance engineering
- Locust-based load, stress, spike, and sustained testing.
- P50/P95/P99 latency tracking.
- Configurable load profiles for repeatable experiments.

### CI/CD and reporting
- Parallelized GitHub Actions testing.
- HTML/JSON and Allure reporting.
- Prometheus/Grafana quality dashboards.
- Failure notifications for CI workflows.

## Test matrix

The repository is organized around multiple test layers rather than a single end-to-end suite:

| Layer | Example scope |
|---|---|
| API | CRUD, auth, validation, pagination |
| Integration | End-to-end service workflows |
| LLM | RAG, hallucination, prompt regression |
| Contract | Schema/backward-compatibility checks |
| UI | Browser workflows with Playwright |
| Performance | Load, stress, spike, latency |

## Technology stack

| Layer | Technology |
|---|---|
| Test framework | Python 3.11, Pytest, Pytest-Asyncio |
| API | Requests, HTTPX, Schemathesis |
| AI quality | OpenAI, LangChain, RAGAS |
| UI | Playwright |
| Performance | Locust |
| Mocking | FastAPI, Respx |
| Reporting | Pytest-HTML, Allure |
| Observability | Prometheus, Grafana |
| CI/CD | GitHub Actions |
| Test data | Faker, Factory Boy |

## Repository structure

```text
ai-quality-platform/
├── framework/                  # Reusable test framework
├── tests/
│   ├── api/
│   ├── integration/
│   ├── llm/
│   ├── ui/
│   ├── contract/
│   └── performance/
├── mocks/                      # Mock API / LLM services
├── reporting/                  # Reports and metric collection
├── dashboard/                  # Grafana + Prometheus
├── conftest.py
├── pytest.ini
├── requirements.txt
└── .github/workflows/ci.yml
```

## Local development

### Setup

```bash
git clone https://github.com/AloneRider-pixel/ai-quality-platform.git
cd ai-quality-platform
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

### Run tests

```bash
pytest tests/ -v
pytest tests/api/ -v
pytest tests/llm/ -v
```

### Run a load test

```bash
locust -f tests/performance/locustfile.py --headless -u 100 -r 10 -t 60s
```

## Quality reporting

```bash
pytest tests/ -v --html=reports/report.html
```

For the dashboard stack:

```bash
docker-compose up -d grafana prometheus
```

## Important benchmark practice

The test counts and performance scenarios in this repository should be treated as **test-suite scope**, not external product-quality claims. Published benchmark numbers should include the dataset, environment, workload, tool versions, and reproducible commands.

## Roadmap

- Versioned LLM evaluation datasets and regression thresholds.
- OpenTelemetry integration for test-to-service correlation.
- Consumer-driven contract testing.
- Distributed load generation.
- CI quality gates based on configurable SLO thresholds.

## License

MIT
