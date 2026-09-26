# Evidence and reproducibility policy

This repository demonstrates test engineering and quality infrastructure. A passing CI job is evidence that the configured checks passed; it is not evidence of production model quality or application performance.

## Published measurements

Any performance, coverage, reliability, or model-quality number should identify the dataset or workload, test configuration, tool versions, sample count, environment, and commit. Keep the generated report as a CI artifact when practical.

## Synthetic fixtures

Mock services, deterministic fixtures, and seeded test data make regression tests reproducible. Synthetic results must remain explicitly labeled as synthetic and must not be presented as live-provider or production measurements.

## Benchmark boundaries

Live-provider benchmarks should be explicitly opt-in and should publish their methodology and provenance. Required CI must not depend on private credentials or external systems unless the repository is intentionally an integration-test project.

## Review rule

Every quantitative README claim should be traceable to code, a reproducible command or workflow, and documented experimental conditions.
