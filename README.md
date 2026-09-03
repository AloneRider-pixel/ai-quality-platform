# 🧪 AI Quality Engineering & API Automation Platform

**Comprehensive testing platform** for APIs, AI/LLM applications, and performance — with automated quality dashboards and CI/CD integration.

---

## 🏗️ Architecture

```
Application APIs / LLM Endpoints
           ↓
    PyTest Framework
    (Fixtures + Helpers)
           ↓
  ┌────────┼────────┬──────────┐
  ↓        ↓        ↓          ↓
API     Integration  LLM Eval   UI
Tests   Tests        Tests     Tests
  │        │        │          │
  └────────┼────────┴──────────┘
           ↓
    Locust Load Tests
           ↓
    GitHub Actions CI/CD
           ↓
  ┌────────┴────────┐
  ↓                  ↓
Test Reports     Grafana
(HTML/JSON)     Dashboard
```

---

## ✨ Features

### Testing Framework
- **Reusable PyTest Framework** — Base classes, fixtures, helpers, assertions
- **API Test Suite** — CRUD, validation, error handling, pagination tests
- **Integration Tests** — End-to-end workflow testing across services
- **Regression Suite** — Automated regression detection with change impact analysis
- **Contract Testing** — API schema validation and backward compatibility checks
- **UI Automation** — Playwright-based browser testing

### AI/LLM Quality
- **RAG Evaluation** — Faithfulness, relevance, recall, precision metrics
- **Hallucination Tests** — NLI-based detection of fabricated responses
- **Prompt Regression** — Golden set testing for prompt changes
- **Semantic Similarity** — Embedding-based response comparison
- **Toxicity & Bias** — Content safety scoring

### Performance
- **Load Testing** — Locust-based HTTP load tests
- **Stress Testing** — Breakpoint identification
- **Spike Testing** — Sudden load surge handling
- **Latency Profiling** — P50/P95/P99 distribution tracking

### Infrastructure
- **Mock Services** — FastAPI-based mock servers for isolated testing
- **Test Data Generation** — Factory pattern with Faker
- **CI/CD Pipeline** — GitHub Actions with parallel test execution
- **HTML Reports** — Rich test reports with screenshots and traces
- **Quality Dashboard** — Real-time Grafana dashboard with test metrics
- **Alerting** — Slack/email notifications on test failures

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | Python 3.11, PyTest 7.x, PyTest-Asyncio |
| API Testing | Requests, HTTPX, Schemathesis |
| AI Testing | OpenAI, LangChain, RAGAS |
| UI Testing | Playwright |
| Load Testing | Locust |
| Mock Services | FastAPI, Respx |
| CI/CD | GitHub Actions |
| Reporting | PyTest-HTML, Allure |
| Dashboard | Grafana, Prometheus |
| Data | Faker, Factory Boy |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker (for mock services)

### 1. Clone & Setup

```bash
git clone https://github.com/AloneRider-pixel/ai-quality-platform.git
cd ai-quality-platform
pip install -r requirements.txt
playwright install chromium
```

### 2. Run All Tests

```bash
# Full test suite
pytest tests/ -v --html=reports/report.html

# API tests only
pytest tests/api/ -v

# LLM evaluation only
pytest tests/llm/ -v

# Load tests
locust -f tests/performance/locustfile.py --headless -u 100 -r 10 -t 60s
```

### 3. View Reports

```bash
open reports/report.html
```

### 4. Start Dashboard

```bash
docker-compose up -d grafana prometheus
# Open http://localhost:3000
```

---

## 📁 Project Structure

```
ai-quality-platform/
├── framework/                  # Reusable testing framework
│   ├── base_test.py            # Base test classes
│   ├── api_client.py           # HTTP client wrapper
│   ├── assertions.py           # Custom assertions
│   ├── fixtures.py             # Shared PyTest fixtures
│   ├── data_factories.py       # Test data generators
│   └── reporters.py            # Custom reporting
├── tests/
│   ├── api/                    # API test suites
│   │   ├── test_orders.py
│   │   ├── test_products.py
│   │   ├── test_auth.py
│   │   └── test_pagination.py
│   ├── integration/            # Integration tests
│   │   ├── test_order_flow.py
│   │   └── test_user_journey.py
│   ├── llm/                    # LLM/AI quality tests
│   │   ├── test_rag_evaluation.py
│   │   ├── test_hallucination.py
│   │   ├── test_prompt_regression.py
│   │   └── test_toxicity.py
│   ├── ui/                     # UI automation
│   │   └── test_web_pages.py
│   ├── contract/               # Contract testing
│   │   └── test_api_contracts.py
│   └── performance/            # Load tests
│       ├── locustfile.py
│       └── k6_scripts.js
├── mocks/                      # Mock services
│   ├── mock_api.py
│   └── mock_llm.py
├── reporting/                  # Report generation
│   ├── html_report.py
│   └── metrics_collector.py
├── dashboard/                  # Grafana dashboard
│   ├── docker-compose.yml
│   ├── prometheus.yml
│   └── grafana/
├── conftest.py                 # Root PyTest config
├── pytest.ini                  # PyTest configuration
├── requirements.txt
├── .github/workflows/ci.yml   # CI/CD pipeline
└── README.md
```

---

## 📊 Test Categories

| Category | Count | Description |
|----------|-------|-------------|
| API Tests | 50+ | CRUD, validation, auth, pagination, error handling |
| Integration Tests | 20+ | End-to-end workflows across services |
| LLM Tests | 30+ | RAG eval, hallucination, prompt regression |
| Contract Tests | 15+ | Schema validation, backward compatibility |
| UI Tests | 10+ | Page loads, forms, navigation |
| Load Tests | 5+ | Sustained, spike, stress scenarios |

---

## 📝 License

MIT
