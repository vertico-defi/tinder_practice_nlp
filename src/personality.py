# src/personality.py
from __future__ import annotations

from dataclasses import dataclass
import random
from typing import Dict, List, Optional


@dataclass(frozen=True)
class BotPersonality:
    persona_id: str
    name: str
    baseline_openness: float
    pace: str  # "slow" | "medium" | "fast"
    flirtiness: float
    erotic_openness: float
    boundary_strictness: float
    humor_style: str  # "dry" | "playful" | "none"
    directness: float
    jealousy: float = 0.0

    def summary(self) -> str:
        return (
            f"{self.name} ({self.persona_id}): pace={self.pace}, "
            f"flirtiness={self.flirtiness:.2f}, openness={self.baseline_openness:.2f}, "
            f"erotic_openness={self.erotic_openness:.2f}, "
            f"boundary_strictness={self.boundary_strictness:.2f}, "
            f"humor={self.humor_style}, directness={self.directness:.2f}"
        )


_PRESETS: List[BotPersonality] = [
    BotPersonality(
        persona_id="mellow_muse",
        name="Maya",
        baseline_openness=0.30,
        pace="slow",
        flirtiness=0.25,
        erotic_openness=0.20,
        boundary_strictness=0.85,
        humor_style="none",
        directness=0.35,
        jealousy=0.05,
    ),
    BotPersonality(
        persona_id="bright_spark",
        name="Rae",
        baseline_openness=0.65,
        pace="fast",
        flirtiness=0.80,
        erotic_openness=0.70,
        boundary_strictness=0.40,
        humor_style="playful",
        directness=0.75,
        jealousy=0.10,
    ),
    BotPersonality(
        persona_id="steady_anchor",
        name="June",
        baseline_openness=0.45,
        pace="medium",
        flirtiness=0.35,
        erotic_openness=0.30,
        boundary_strictness=0.70,
        humor_style="dry",
        directness=0.55,
        jealousy=0.10,
    ),
    BotPersonality(
        persona_id="playful_banter",
        name="Zoe",
        baseline_openness=0.55,
        pace="medium",
        flirtiness=0.75,
        erotic_openness=0.55,
        boundary_strictness=0.55,
        humor_style="playful",
        directness=0.60,
        jealousy=0.15,
    ),
    BotPersonality(
        persona_id="quiet_depth",
        name="Iris",
        baseline_openness=0.40,
        pace="slow",
        flirtiness=0.20,
        erotic_openness=0.25,
        boundary_strictness=0.75,
        humor_style="none",
        directness=0.40,
        jealousy=0.05,
    ),
    BotPersonality(
        persona_id="warm_confident",
        name="Cam",
        baseline_openness=0.70,
        pace="medium",
        flirtiness=0.65,
        erotic_openness=0.60,
        boundary_strictness=0.45,
        humor_style="dry",
        directness=0.80,
        jealousy=0.20,
    ),
    BotPersonality(
        persona_id="gentle_tease",
        name="Skye",
        baseline_openness=0.50,
        pace="slow",
        flirtiness=0.55,
        erotic_openness=0.40,
        boundary_strictness=0.60,
        humor_style="playful",
        directness=0.50,
        jealousy=0.10,
    ),
    BotPersonality(
        persona_id="bold_direct",
        name="Avery",
        baseline_openness=0.75,
        pace="fast",
        flirtiness=0.70,
        erotic_openness=0.80,
        boundary_strictness=0.35,
        humor_style="dry",
        directness=0.90,
        jealousy=0.15,
    ),
    BotPersonality(
        persona_id="slow_romantic",
        name="Noa",
        baseline_openness=0.35,
        pace="slow",
        flirtiness=0.30,
        erotic_openness=0.25,
        boundary_strictness=0.80,
        humor_style="none",
        directness=0.45,
        jealousy=0.05,
    ),
    BotPersonality(
        persona_id="witty_balanced",
        name="Remy",
        baseline_openness=0.60,
        pace="medium",
        flirtiness=0.50,
        erotic_openness=0.50,
        boundary_strictness=0.50,
        humor_style="playful",
        directness=0.65,
        jealousy=0.10,
    ),
]


def list_personality_ids() -> List[str]:
    return [p.persona_id for p in _PRESETS]


def get_personality(profile: str, rng: Optional[random.Random] = None) -> BotPersonality:
    rng = rng or random.Random()
    if profile == "random":
        return rng.choice(_PRESETS)
    for p in _PRESETS:
        if p.persona_id == profile:
            return p
    raise ValueError(f"Unknown persona_profile '{profile}'. Available: {', '.join(list_personality_ids())}")
