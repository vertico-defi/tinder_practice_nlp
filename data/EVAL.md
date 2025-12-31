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
Optional SAFE expansion data lives at `data/labels_safe_move_synth_safe_expansion.jsonl`.
Merged training data (base + SAFE expansion) is at `data/labels_safe_move_synth_merged.jsonl`.

## v0.5.2 System-Level Evaluation
- The safety classifier metrics remain the v0.3 synthetic validation evaluation.
- For v0.5.2, manual smoke tests verified trust-tier logging, identity lock, reality guard behavior, and contextual safety repair.
- No new benchmark results are claimed beyond the existing `data/results/` reports.

## Retraining Note
- To retrain with the merged SAFE expansion set:
  - `python -m src.train_safe_classifier_embed --train_jsonl data/labels_safe_move_synth_merged.jsonl --out_model models/safe_violation_clf_embed.joblib`

## Reporting Conventions
- Track script version, dataset version, and model artifact used per run.
- Record seed values if you run multiple trials.
