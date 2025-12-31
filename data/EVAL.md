# Evaluation Notes

This document summarizes evaluation scripts and outputs.

## Batch Evaluation
- Run batch scoring: `python src/run_batch_v0.py`
- Report aggregation: `python src/report_batch_results.py`
- Output examples: `data/results/v0_batch_results.jsonl`

## Safety Classifier Evaluation
- `python src/eval_safe_on_synth_validation.py`
- `python src/eval_safe_on_synth_validation_embed.py`
Archived binary variants live under `archive/v0_3_experiments/`.

Outputs are written to `data/results/` with versioned filenames.

## v0.5 System-Level Evaluation
- The safety classifier metrics remain the v0.3 synthetic validation evaluation.
- For v0.5, manual smoke tests verified phase debug output, personality selection, memory persistence, and gate behavior on escalation prompts.
- No new benchmark results are claimed beyond the existing `data/results/` reports.

## Reporting Conventions
- Track script version, dataset version, and model artifact used per run.
- Record seed values if you run multiple trials.
