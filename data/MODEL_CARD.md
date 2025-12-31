# Model Card - Safety Gate (v0.5.1)

## Model Summary
- Model: sentence-transformer embeddings + Logistic Regression classifier (v0.3 setup)
- Purpose: score user messages for boundary-risk and gate unsafe moves
- Primary artifact: `models/safe_violation_clf_embed.joblib`

## System Overview (v0.5.1)
- LLM layer: llama.cpp client using a local GGUF instruct model (external pretrained; not trained here)
- Safety layer: v0.3 embedding logistic regression classifier used as a guardrail
- Phase tracker: conservative phase inference used for gating and debug output
- Personality: randomized per session from preset profiles
- Semantic memory: fact-only memory persisted to `data/memory/`
- Safety repair: contextual safe replies that acknowledge the user before redirecting
- Bot profile selection: user-selectable bot gender with neutral preference handling

## Intended Use
- Safety-risk estimation and intervention in the practice chat loop.
- Research and evaluation within this capstone only.

## Not Intended For
- Production moderation or safety enforcement.
- Use outside the defined dating-chat practice scenarios.

## Training Data
- Labels: `data/labels_safe_move_gold.jsonl`
- Inputs: `data/samples_unlabeled.jsonl`
- Label creation: weak supervision + manual edits (see `DATASET.md`)

## Inputs and Outputs
- Input: user message (string)
- Output: `p_move` (probability), label (`SAFE`/`MOVE`), and a gating decision
  - If `MOVE` or an obvious escalation rule hits, respond with a boundary-safe repair template
  - If erotic intent is early or disallowed by phase/personality, respond with a soft deflection
  - Otherwise pass the conversation to the LLM

## Evaluation
- Legacy TF-IDF training script: `python src/train_safe_classifier.py` (baseline only)
- Validation scripts: `python src/eval_safe_on_synth_validation.py` and related variants
- Outputs: `data/results/` reports
  - SAFE expansion file (optional): `data/labels_safe_move_synth_safe_expansion.jsonl`
  - Merged training file (optional): `data/labels_safe_move_synth_merged.jsonl`

## Limitations
- Weak supervision rules can miss implicit or nuanced unsafe content.
- Safety gate can be conservative; false positives may occur in romantic/private contexts.
- LLM response quality depends on the chosen GGUF model and decoding settings.
- Phase inference and intent detection are heuristic and can misclassify tone.

## Ethical Considerations
- The system should not encourage harassment, coercion, or explicit sexual content.
- The classifier is a research artifact and may be wrong; use conservative thresholds.
