# src/response_planner.py
from __future__ import annotations

from dataclasses import dataclass
import random
from typing import List, Optional

from src.conversation_phase import ConversationPhase
from src.personality import BotProfile


@dataclass
class StylePlan:
    plan: str
    ask_question: bool
    disclosure: Optional[str] = None
    story: Optional[str] = None
    tease: Optional[str] = None


def _roll(rng: random.Random, rate: float) -> bool:
    return rng.random() < max(0.0, min(1.0, rate))


def _short_input(text: str) -> bool:
    words = [w for w in (text or "").split() if w]
    return len(words) <= 5


def plan_response(
    user_text: str,
    phase: ConversationPhase,
    profile: BotProfile,
    last_asked_question: bool,
    rng: random.Random,
) -> StylePlan:
    ask_question = _roll(rng, profile.question_rate)
    if last_asked_question and not _short_input(user_text):
        ask_question = False

    disclosure = profile.pick_disclosure(rng) if _roll(rng, profile.self_disclosure_rate) else None
    story = profile.pick_story(rng) if _roll(rng, profile.storytelling_rate) else None
    tease = profile.pick_tease(rng) if _roll(rng, profile.humor_rate) else None

    plan = "reflect_only"
    if story:
        plan = "mini_story"
    elif tease and profile.flirtiness >= 0.4 and phase in {
        ConversationPhase.RAPPORT,
        ConversationPhase.FLIRTING,
        ConversationPhase.INTIMATE,
    }:
        plan = "playful_tease"
    elif disclosure and ask_question:
        plan = "reflect + self_disclose + question"
    elif disclosure:
        plan = "reflect + self_disclose"
    elif ask_question:
        plan = "reflect + question"

    return StylePlan(plan=plan, ask_question=ask_question, disclosure=disclosure, story=story, tease=tease)
