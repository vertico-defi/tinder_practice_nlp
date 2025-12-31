# Dataset Notes

This document describes the datasets in `data/` and how they are generated.

## Core Files
- `data/personas.json`: persona profiles.
- `data/contexts.jsonl`: scenario contexts referencing personas and chat history.
- `data/samples_unlabeled.jsonl`: user message samples to be scored or labeled.
- `data/labels_template.jsonl`: rubric labels template (Step 1).
- `data/labels_gold_example.jsonl`: small example of filled labels.

## Safety and Move Labels (v0.2)
- `data/labels_safe_move_gold_template.jsonl`: labeling template for SAFE and MOVE.
- `data/labels_safe_move_gold.jsonl`: materialized labels (weak supervision or manual edits).
- `data/labels_safe_move_synth_validation.jsonl`: synthetic validation set for SAFE and MOVE.
- `data/labels_safe_move_synth_safe_expansion.jsonl`: synthetic SAFE expansions for benign intimacy-adjacent language.
- `data/labels_safe_move_synth_merged.jsonl`: merged base + SAFE expansion (training convenience).

v0.5.2 reuses the v0.3 training/eval assets; no new labeled datasets were introduced.
Archived synthetic train/binary artifacts and scripts live under `archive/v0_3_experiments/`.

## Results
- `data/results/`: evaluation outputs (batch reports, validation summaries).
- `data/logs/`: chat episode logs (created by chat scripts).
- `data/memory/`: per-session semantic memory (runtime-generated).

## Schema Summary
- `personas.json`:
  - `persona_id`, `name`, `bio`, `interests`, `style`
- `contexts.jsonl`:
  - `context_id`, `use_case`, `persona_id`, `chat_history`, `partner_last_message`
- `samples_unlabeled.jsonl`:
  - `sample_id`, `context_id`, `use_case`, `user_text`
- `labels_safe_move_*`:
  - `sample_id`, `use_case`, `category`, `user_text`, `SAFE`, `MOVE`, `notes`
- `labels_template.jsonl` / `labels_gold_example.jsonl`:
  - `sample_id`, `ENG`, `CTX`, `TONE`, `CLAR`, `SAFE`, `MOVE`, `notes`

## Generation
- Step 1 dataset generation: `python src/make_step1_data.py`
- SAFE/MOVE label template: `python src/make_safe_move_labels.py`
- Weak supervision materialization: `python src/auto_label_safe_move.py`
- SAFE expansion set: `python src/make_safe_move_synth_safe_expansion.py`
- Merge SAFE expansion with base synth set: `python src/merge_safe_move_synth_sets.py`

Archived synthetic train/validation scripts live under `archive/v0_3_experiments/`.

## Versioning Guidance
- Record dataset hashes and row counts when regenerating files.
- Keep `labels_safe_move_gold_template.jsonl` as the source of truth for manual edits.
