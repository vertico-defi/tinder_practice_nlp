# Step 1 — Scope and Success Metrics (Capstone NLP)

## Purpose
This repository defines a platform-agnostic dating-chat practice simulator dataset and evaluation rubric for an NLP capstone project.

## In Scope
- 4 use cases: cold open, keep-going, suggest-date, boundary moment
- Unit: user message scored in context of persona profile + chat history
- Rubric: 6 dimensions (0–2 each), total 0–12, normalized to OCQ in [0,1]
- Data stored in JSON/JSONL for reproducibility

## Out of Scope / Constraints
- No app integration or scraping
- No coaching for harassment, coercion, manipulation, or explicit sexual content
- Store only synthetic IDs; no personal identifiers

## Rubric Dimensions
ENG (Engagement), CTX (Context use), TONE (Tone/politeness),
CLAR (Clarity), SAFE (Boundary/safety), MOVE (Forward motion)

## Metrics
- OCQ = (ENG+CTX+TONE+CLAR+SAFE+MOVE)/12
- ENG_score = ENG/2
- CTX_score = CTX/2
- Safety violation flag = 1 if SAFE==0 else 0
- Dataset-level: mean/median OCQ, violation rate, by-use-case breakdown

## Files
- data/personas.json: persona profiles
- data/contexts.jsonl: context situations by use case
- data/samples_unlabeled.jsonl: user message samples to annotate
- data/labels_template.jsonl: annotation template aligned by sample_id
- data/labels_gold_example.jsonl: a small example of completed labels

## Reproducible generation
`./src/make_step1_data.py` writes the Step 1 dataset files.
`./src/score_report.py` computes metrics from a labeled file.
