# v0.6.0 Presentation Outline

## 1. Title + One-Sentence Summary
- Project name and goal: offline dating-chat practice simulator with safety-aware evaluation.

## 2. Problem and Motivation
- Why practice conversations offline.
- Risks of unsafe escalation and the need for evaluation.

## 3. System Overview
- Offline LLM chat loop (llama.cpp + GGUF).
- Persona profiles + profile cards.
- Style planner + trust/phase gating.
- Safety gate (learned classifier).

## 4. Data and Rubric
- Synthetic use cases (UC1-UC4).
- Rubric dimensions: ENG, CTX, TONE, CLAR, SAFE, MOVE.
- Labeling and MOVE proxy for safety violations.

## 5. Evaluation Method
- Final evaluation command and fixed dataset.
- Thresholding and confusion-matrix metrics.
- Per-use-case breakdown.

## 6. Results (v0.6.0)
- Overall precision/recall/F1/accuracy.
- UC3 vs UC4 comparison (one chart).

## 7. Demo / Example Interaction
- Short transcript showing trust/phase behavior.
- Safety deflection example.

## 8. Limitations
- Heuristic phase detection.
- Synthetic validation scope.
- Conservative safety thresholding.

## 9. Future Work (if allowed)
- Broader datasets and human eval.
- Calibrated safety thresholds by persona.

## 10. Closing
- Final statement: v0.6.0 is frozen and reproducible.
