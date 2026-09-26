# Verification & Evidence

| Area | Evidence | Reproduction |
|---|---|---|
| API regression | tests/api/ | pytest tests/api/ -v |
| Integration regression | tests/integration/ | pytest tests/integration/ -v with the mock API |
| LLM regression | tests/llm/ | pytest tests/llm/ -v; responses are deterministic fixtures |
| UI/contract scope | tests/ui/ and tests/contract/ | Run the targeted suites with their required services |
| Performance harness | tests/performance/ | Locust scenario commands documented in README |
| Static security analysis | .github/workflows/codeql.yml | CodeQL |
| Workflow supply-chain posture | .github/workflows/scorecard.yml | OpenSSF Scorecard |

## Evidence policy

The default CI suite must stay deterministic. Any live-provider benchmark is a separate measurement and must include the model/provider, dataset version, denominator, run configuration, environment, timestamp, and application commit.

Synthetic fixtures are explicitly labeled and must never be presented as production LLM performance.