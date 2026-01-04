#!/usr/bin/env python3
import argparse
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

import joblib
import numpy as np


def read_jsonl(path: Path) -> List[Dict[str, Any]]:
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def parse_int(v: Any, field: str) -> int:
    try:
        return int(v)
    except Exception as exc:
        raise ValueError(f"Could not parse '{field}' as int: {v}") from exc


def derive_y(rows: List[Dict[str, Any]], move_key: str, move_threshold: int) -> np.ndarray:
    y = []
    for r in rows:
        mv = parse_int(r.get(move_key), move_key)
        y.append(1 if mv >= move_threshold else 0)
    return np.array(y, dtype=np.int32)


def confusion_counts(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, int]:
    tp = int(np.sum((y_true == 1) & (y_pred == 1)))
    tn = int(np.sum((y_true == 0) & (y_pred == 0)))
    fp = int(np.sum((y_true == 0) & (y_pred == 1)))
    fn = int(np.sum((y_true == 1) & (y_pred == 0)))
    return {"tp": tp, "tn": tn, "fp": fp, "fn": fn}


def metrics_from_conf(conf: Dict[str, int]) -> Dict[str, float]:
    tp, tn, fp, fn = conf["tp"], conf["tn"], conf["fp"], conf["fn"]
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) else 0.0
    acc = (tp + tn) / (tp + tn + fp + fn) if (tp + tn + fp + fn) else 0.0
    return {"precision": precision, "recall": recall, "f1": f1, "accuracy": acc}


def predict_p_move(model_artifact: Any, texts: List[str]) -> np.ndarray:
    if isinstance(model_artifact, dict) and model_artifact.get("type") == "embed_lr":
        from sentence_transformers import SentenceTransformer

        embedder = SentenceTransformer(model_artifact["sentence_transformer"])
        X = embedder.encode(
            texts,
            batch_size=64,
            show_progress_bar=False,
            convert_to_numpy=True,
            normalize_embeddings=bool(model_artifact.get("normalize_embeddings", True)),
        )
        clf = model_artifact["logreg"]
        return clf.predict_proba(X)[:, 1]

    if hasattr(model_artifact, "predict_proba"):
        return model_artifact.predict_proba(texts)[:, 1]

    raise ValueError("Unsupported model artifact format. Expected embed_lr dict or sklearn-like estimator.")


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    ap = argparse.ArgumentParser(description="Final v0.6.0 evaluation runner.")
    ap.add_argument("--in_path", default=str(root / "data/labels_safe_move_synth_validation.jsonl"))
    ap.add_argument("--model_path", default=str(root / "models/safe_violation_clf_embed.joblib"))
    ap.add_argument("--out_path", default=str(root / "data/results/final_v0_6_report.json"))
    ap.add_argument("--threshold", type=float, default=0.45, help="Decision threshold on p(MOVE)")
    ap.add_argument("--text_key", default="user_text")
    ap.add_argument("--move_key", default="MOVE")
    ap.add_argument("--move_threshold", type=int, default=2, help="Ground-truth mapping: MOVE if MOVE>=threshold")
    ap.add_argument("--uc_key", default="use_case")
    args = ap.parse_args()

    rows = read_jsonl(Path(args.in_path))
    if not rows:
        raise ValueError(f"No rows found in {args.in_path}")

    texts = [str(r.get(args.text_key, "")).strip() for r in rows]
    y_true = derive_y(rows, move_key=args.move_key, move_threshold=args.move_threshold)

    model = joblib.load(args.model_path)
    p_move = predict_p_move(model, texts)
    y_pred = (p_move >= args.threshold).astype(np.int32)

    overall_conf = confusion_counts(y_true, y_pred)
    overall_metrics = metrics_from_conf(overall_conf)

    per_uc = {}
    if args.uc_key in rows[0]:
        buckets = defaultdict(list)
        for r, yt, yp in zip(rows, y_true.tolist(), y_pred.tolist()):
            buckets[str(r.get(args.uc_key, "UNKNOWN"))].append((yt, yp))
        for uc, pairs in buckets.items():
            yt = np.array([p[0] for p in pairs], dtype=np.int32)
            yp = np.array([p[1] for p in pairs], dtype=np.int32)
            conf = confusion_counts(yt, yp)
            per_uc[uc] = {
                "n": int(len(pairs)),
                "confusion": conf,
                "metrics": metrics_from_conf(conf),
            }

    report = {
        "version": "v0.6.0",
        "dataset": {
            "path": str(Path(args.in_path)),
            "n_total": int(len(rows)),
            "n_scored": int(len(y_true)),
            "label_rule": f"MOVE>= {args.move_threshold} => MOVE(1), else SAFE(0)",
        },
        "model": {
            "path": str(Path(args.model_path)),
            "type": "embed_lr" if isinstance(model, dict) else type(model).__name__,
        },
        "threshold": float(args.threshold),
        "counts": {"confusion": overall_conf},
        "metrics": overall_metrics,
        "by_use_case": per_uc,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    out_path = Path(args.out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    print("=== final v0.6.0 report ===")
    print(f"Scored n={report['dataset']['n_scored']} rows at threshold={args.threshold}")
    print(f"Overall confusion: {overall_conf}")
    print(
        f"Precision={overall_metrics['precision']:.3f} "
        f"Recall={overall_metrics['recall']:.3f} "
        f"F1={overall_metrics['f1']:.3f} "
        f"Acc={overall_metrics['accuracy']:.3f}"
    )
    print(f"Wrote report to: {out_path}")


if __name__ == "__main__":
    main()
