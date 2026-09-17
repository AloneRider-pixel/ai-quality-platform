# Contributing to AI Quality Platform

This repository focuses on API, integration, UI, performance, and LLM quality engineering.

## Development workflow

1. Create a focused branch from `main`.
2. Add or update tests when behavior changes.
3. Keep test data deterministic and isolate external services with mocks where practical.
4. Run linting and the relevant test suites locally before opening a pull request.
5. Never commit API keys, secrets, private datasets, or generated reports containing sensitive data.

## Quality expectations

- Keep test fixtures reusable and isolated.
- Make quality gates fail on real test failures; do not mask failures with shell fallbacks.
- Document evaluation datasets, scoring methodology, and benchmark conditions.
- Separate deterministic tests from tests requiring paid or external model APIs.

## Pull requests

Include the affected test categories, commands executed, benchmark/evaluation impact, and any CI or dependency implications.
