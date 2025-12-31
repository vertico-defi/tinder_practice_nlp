# src/memory.py
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple


@dataclass
class MemoryItem:
    key: str
    value: str
    confidence: float
    last_seen: str

    def as_dict(self) -> Dict[str, str]:
        return {
            "key": self.key,
            "value": self.value,
            "confidence": self.confidence,
            "last_seen": self.last_seen,
        }


_PREF_PATTERNS: List[Tuple[str, str]] = [
    (r"\bi (really )?(like|love|enjoy|prefer|adore)\s+([^.!?]{2,60})", "likes"),
    (r"\bi'?m into\s+([^.!?]{2,60})", "likes"),
    (r"\bmy favorite\s+([^.!?]{2,40})\s+is\s+([^.!?]{2,60})", "favorite"),
    (r"\bi (work as|work in|do)\s+(a |an )?([^.!?]{2,60})", "job"),
    (r"\bi'?m (a|an)\s+([^.!?]{2,60})", "job"),
]

_BLOCKLIST = re.compile(
    r"\b(address|street|st\.|road|rd\.|ave|avenue|blvd|lane|ln\.|apt|suite|unit|zip|postal|postcode|phone|number|email|snap|insta)\b",
    re.IGNORECASE,
)


def _now_iso() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


def _clean_value(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip(" .,!?:;\"'")


def _is_safe_value(value: str) -> bool:
    if len(value) < 2:
        return False
    if _BLOCKLIST.search(value):
        return False
    if re.search(r"@|https?://|www\.", value, re.IGNORECASE):
        return False
    if re.search(r"\d{3,}", value):
        return False
    return True


class SemanticMemoryStore:
    def __init__(self, memory_id: str, root: Optional[Path] = None):
        self.memory_id = memory_id
        self.root = root or (Path(__file__).resolve().parents[1] / "data" / "memory")
        self.root.mkdir(parents=True, exist_ok=True)
        self.path = self.root / f"{memory_id}.json"
        self.items: List[MemoryItem] = []
        self._load()

    def _load(self) -> None:
        if not self.path.exists():
            return
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            raw = []
        self.items = [
            MemoryItem(
                key=i["key"],
                value=i["value"],
                confidence=float(i.get("confidence", 0.6)),
                last_seen=i.get("last_seen", _now_iso()),
            )
            for i in raw
            if isinstance(i, dict) and "key" in i and "value" in i
        ]

    def save(self) -> None:
        payload = [i.as_dict() for i in self.items]
        self.path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def clear(self) -> None:
        self.items = []
        if self.path.exists():
            self.path.unlink()

    def update_from_text(self, user_text: str) -> List[MemoryItem]:
        added: List[MemoryItem] = []
        for pattern, key in _PREF_PATTERNS:
            for match in re.finditer(pattern, user_text, flags=re.IGNORECASE):
                groups = [g for g in match.groups() if g]
                value = _clean_value(groups[-1]) if groups else ""
                if not _is_safe_value(value):
                    continue
                item = self._upsert(key, value)
                if item:
                    added.append(item)
        if added:
            self.save()
        return added

    def _upsert(self, key: str, value: str) -> Optional[MemoryItem]:
        now = _now_iso()
        for item in self.items:
            if item.key == key and item.value.lower() == value.lower():
                item.last_seen = now
                item.confidence = max(item.confidence, 0.6)
                return None
        new_item = MemoryItem(key=key, value=value, confidence=0.6, last_seen=now)
        self.items.append(new_item)
        return new_item

    def get_highlights(self, k: int = 3) -> List[str]:
        sorted_items = sorted(self.items, key=lambda i: i.last_seen, reverse=True)
        highlights = [f"{i.key}: {i.value}" for i in sorted_items[:k]]
        return highlights
