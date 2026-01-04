# NLP Capstone Dating Chat Practice Simulator

## Overview
This repository contains a dating-chat practice simulator and safety-aware coaching pipeline for an NLP capstone. The current work progresses from heuristic scoring to a learned safety intervention model (see `CHANGELOG.md`).

## Status
- v0.2: Learned safety intervention with TF-IDF + Logistic Regression for unsafe content detection.
- v0.4: Two-layer offline chatbot (llama.cpp LLM + v0.3 embedding safety gate).
- v0.6.0: Real profile cards, style planner, and trust-tiered safety layered on the offline chatbot.
- Datasets and evaluation scripts live under `data/` and `src/`.

## Repo Layout
- `data/`: personas, contexts, samples, labels, and results.
- `models/`: trained classifier artifacts (may be generated).
- `src/`: data generation, training, chat, and evaluation scripts.
- `resources/`: scope notes and planning documents.

## Quickstart (common entrypoints)
Use the script help (`--help`) for full options.
- Chat loop: `python src/chat_v0_2.py`
- Offline chatbot (v0.6.0): `python -m src.chat_v0_5_chatbot --gguf_model models/gguf/Phi-3-mini-4k-instruct-q4.gguf --bot_gender random --attraction unspecified`
- Train safety classifier: `python src/train_safe_classifier.py`
- Batch run: `python src/run_batch_v0.py`
- Report results: `python src/report_batch_results.py`

In-chat profile commands: `/profile`, `/pics`, `/name`, `/switch`.

Note: several scripts require `scikit-learn` and `joblib` even though `requirements.txt` is currently minimal.

## Documentation
- `README_STEP1.md`: Step 1 scope and metrics.
- `DATASET.md`: dataset files and schemas.
- `MODEL_CARD.md`: model intent, training data, and limitations.
- `EVAL.md`: evaluation scripts and outputs.
- `CHANGELOG.md`: versioned changes.

## Reproducibility Notes
- Pin Python version and dependencies before final evaluation.
- Track dataset and model versions (hashes, sizes, and provenance) when generating new artifacts.
- Prefer deterministic seeds for training and evaluation scripts.

## Data Locations
- Synthetic validation set: `data/labels_safe_move_synth_validation.jsonl`
- SAFE expansion set: `data/labels_safe_move_synth_safe_expansion.jsonl`
- Merged training set: `data/labels_safe_move_synth_merged.jsonl`
- Evaluation reports: `data/results/`
- Source files: `data/personas.json`, `data/contexts.jsonl`, `data/samples_unlabeled.jsonl`, `data/labels_safe_move_gold.jsonl`
- Generated outputs: `data/results/`, `data/logs/`, `data/memory/`, and `models/`
