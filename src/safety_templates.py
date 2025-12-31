# src/safety_templates.py
from __future__ import annotations

import random
from typing import List


SAFE_REDIRECTS: List[str] = [
    "Totally fair—let’s keep it comfortable. I’m happy to stay here and chat. What are you up to this week?",
    "Got it. I don’t want to push. Want to switch topics—what have you been enjoying lately?",
    "No worries at all. We can keep this low-key. What kind of plans do you have for the weekend?",
    "Thanks for saying that. I’ll slow down. What’s something you’re looking forward to right now?",
]

SOFTENERS: List[str] = [
    "No pressure.",
    "Only if you feel comfortable.",
    "Totally fine either way.",
]

SOFT_DEFLECTS: List[str] = [
    "You’re fun, but let’s keep it a little slow for now. Tell me what you’re into outside of dating apps?",
    "Mmm, tempting. I like a slow burn though—what’s your ideal first date?",
    "Okay, you’ve got my attention. I’m into building a vibe first—what’s your kind of night?",
    "You’re spicy. I’m down to flirt, but let’s not sprint—what’s something that makes you smile lately?",
    "I like the energy. Let’s keep it playful for a bit—what’s a hobby you actually get lost in?",
]

EROTIC_ALLOWED_GUIDANCE = (
    "If mutual and appropriate, you may respond with a consensual adult tone. "
    "Keep it playful and suggestive, avoid explicit pornographic detail, and stay respectful."
)


def boundary_safe_reply(rng: random.Random | None = None) -> str:
    rng = rng or random.Random()
    base = rng.choice(SAFE_REDIRECTS)
    # occasionally append a softener (keeps it human, not robotic)
    if rng.random() < 0.35:
        base = f"{base} {rng.choice(SOFTENERS)}"
    return base


def soft_deflect_reply(rng: random.Random | None = None) -> str:
    rng = rng or random.Random()
    base = rng.choice(SOFT_DEFLECTS)
    if rng.random() < 0.30:
        base = f"{base} {rng.choice(SOFTENERS)}"
    return base
