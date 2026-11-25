---
name: mutmut
description: Use when running or changing Meridian mutation testing in scripts/run_evaluation.py, evaluation/, or reports of mutation catch rate.
---

# mutmut in Meridian

Read AGENTS.md §9 and docs/architecture.md §8 before changing evaluation.

## Process
- Copy the target module into an isolated temp workspace; never mutate the original production module.
- Configure paths in `evaluation/benchmark_config.yaml`; run via `scripts/run_evaluation.py`.
- Run generated tests against the mutated copy only; keep execution offline and resource-limited.
- Record killed, surviving, equivalent, and failed-to-execute mutants separately.
- Score: `killed / executable mutants × 100`; do not count equivalent or failed mutants in the denominator.
- Write `<module_name>_eval.json` to `evaluation/evaluation_results/`.

## Reporting
- State excluded mutant counts and reasons; never report a misleading score when mutations fail to execute.
- Identify which generated tests missed each surviving mutant.
- Mutation catch rate is the primary quality metric; coverage is supporting information only.
- Record the reproducibility fields from docs/architecture.md §14 with each result.
- Preserve the original module hash before and after evaluation.

## Verify
- Run on one benchmark module and confirm the JSON matches the architecture schema.
