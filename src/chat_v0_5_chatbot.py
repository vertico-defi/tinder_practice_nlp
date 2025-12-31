# src/chat_v0_5_chatbot.py
from __future__ import annotations

import argparse
from datetime import datetime
from typing import Dict, List

from src.safety_embed import SafetyEmbedScorer
from src.safety_templates import (
    boundary_safe_reply_contextual,
    soft_deflect_reply,
    EROTIC_ALLOWED_GUIDANCE,
)
from src.safety_rules import obvious_escalation

from src.llm_client_llamacpp import LlamaCppChatClient, LlamaCppConfig
from src.conversation_phase import ConversationPhaseTracker, ConversationPhase
from src.personality import get_profile, list_profile_ids, BotProfile
from src.memory import SemanticMemoryStore


PERSONA_SYSTEM = {
    "friendly": (
        "You are a natural conversational partner on a dating app. "
        "Keep replies short (1–3 sentences). Ask exactly one thoughtful question. "
        "Be warm, curious, and specific."
    ),
    "flirty_adult_ok": (
        "You are playful and lightly flirty on a dating app. Adult topics are allowed if mutual and respectful. "
        "Never be coercive, never push for address/location, and always respect boundaries. "
        "Keep replies short (1–2 sentences). Ask exactly one engaging question."
    ),
}

def build_system_context(
    phase_state,
    bot_profile: BotProfile,
    memory_highlights: List[str],
    allow_erotic: bool,
    user_gender: str,
    attraction: str,
) -> str:
    mem = "; ".join(memory_highlights) if memory_highlights else "none"
    erotic_note = EROTIC_ALLOWED_GUIDANCE if allow_erotic else "Keep replies non-explicit; slow down if needed."
    attraction_line = f"attraction={attraction}" if attraction != "unspecified" else "attraction=unspecified"
    user_gender_line = f"user_gender={user_gender}" if user_gender != "unspecified" else "user_gender=unspecified"
    return (
        "SYSTEM CONTEXT (hidden):\n"
        f"phase={phase_state.phase.value}\n"
        f"bot_profile={bot_profile.summary()}\n"
        f"{user_gender_line}\n"
        f"{attraction_line}\n"
        f"memory={mem}\n"
        "Instruction: be natural and human; do not assume the user's attraction unless specified; "
        "escalate only if appropriate; "
        "respect boundaries and avoid asking for address/location. "
        f"{erotic_note}"
    )


def is_low_engagement(text: str) -> bool:
    t = (text or "").strip().lower()
    if not t:
        return True
    if t in {"ok", "okay", "k", "lol", "sure", "nice", "cool", "yep", "yeah"}:
        return True
    words = [w for w in t.split() if w]
    return len(words) <= 2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--safety_model", default="models/safe_violation_clf_embed.joblib")
    ap.add_argument("--threshold", type=float, default=0.45)

    ap.add_argument("--persona", default="friendly", choices=list(PERSONA_SYSTEM.keys()))
    ap.add_argument("--persona_profile", default="random")
    ap.add_argument("--bot_gender", default="random", choices=["female", "male", "random"])
    ap.add_argument("--user_gender", default="unspecified", choices=["female", "male", "unspecified"])
    ap.add_argument("--attraction", default="unspecified", choices=["women", "men", "any", "unspecified"])
    ap.add_argument("--memory_id", default=None)
    ap.add_argument("--clear-memory", action="store_true")

    # llama.cpp / GGUF
    ap.add_argument("--gguf_model", required=True, help="Path to a .gguf instruct model file")
    ap.add_argument("--chat_format", default="chatml", help="chat format for llama.cpp (e.g., chatml)")
    ap.add_argument("--n_ctx", type=int, default=4096)
    ap.add_argument("--n_threads", type=int, default=8)
    ap.add_argument("--n_gpu_layers", type=int, default=0, help="0=CPU; >0 uses GPU if compiled with CUDA")

    ap.add_argument("--max_tokens", type=int, default=140)
    ap.add_argument("--temperature", type=float, default=0.8)
    ap.add_argument("--top_p", type=float, default=0.95)
    ap.add_argument("--repeat_penalty", type=float, default=1.10)

    args = ap.parse_args()

    print(
        "Tinder Practice Bot v0.5 (phase + personality + memory + safety gate + llama.cpp LLM). "
        "Type 'exit' to quit.\n",
        flush=True,
    )

    try:
        bot_profile = get_profile(args.persona_profile, args.bot_gender)
    except ValueError as exc:
        print(str(exc))
        print(f"Available persona_profile values: {', '.join(list_profile_ids(args.bot_gender))}")
        raise SystemExit(2)

    memory_id = args.memory_id or f"{bot_profile.profile_id}_{datetime.now().strftime('%Y%m%d')}"
    memory = SemanticMemoryStore(memory_id)
    if args.clear_memory:
        memory.clear()
        print(f"[MEM] cleared memory_id={memory_id} path={memory.path}")
        return

    print(
        f"[BOOT] gguf_model={args.gguf_model} persona={args.persona} thr={args.threshold} "
        f"ctx={args.n_ctx} threads={args.n_threads} gpu_layers={args.n_gpu_layers}\n",
        flush=True,
    )
    print(
        f"[BOT] persona_profile={bot_profile.profile_id} name={bot_profile.name} gender={bot_profile.gender} "
        f"pronouns={bot_profile.pronouns} erotic_openness={bot_profile.erotic_openness:.2f} "
        f"pace={bot_profile.pace} boundary_strictness={bot_profile.boundary_strictness:.2f}",
        flush=True,
    )
    print(
        f"[USER] user_gender={args.user_gender} attraction={args.attraction}",
        flush=True,
    )
    print(f"[MEM] memory_id={memory_id} items={len(memory.items)} path={memory.path}", flush=True)
    print("[PHASE] phase=OPENING flirt=0.00 intimate=0.00 erotic=0.00\n", flush=True)

    scorer = SafetyEmbedScorer(args.safety_model)

    llm = LlamaCppChatClient(
        LlamaCppConfig(
            model_path=args.gguf_model,
            chat_format=args.chat_format,
            n_ctx=args.n_ctx,
            n_threads=args.n_threads,
            n_gpu_layers=args.n_gpu_layers,
            temperature=args.temperature,
            top_p=args.top_p,
            repeat_penalty=args.repeat_penalty,
            max_tokens=args.max_tokens,
        )
    )

    history: List[Dict[str, str]] = [{"role": "system", "content": PERSONA_SYSTEM[args.persona]}]
    tracker = ConversationPhaseTracker()
    safety_repair_count = 0
    soft_deflect_count = 0
    low_engagement_count = 0

    while True:
        user = input("you> ").strip()
        if user.lower() in {"exit", "quit"}:
            print("bot> Bye.")
            break
        if not user:
            continue

        s = scorer.score(user, threshold=args.threshold)
        rule_hit, rule_reason = obvious_escalation(user)

        history.append({"role": "user", "content": user})

        phase_state_before = tracker.last_state
        erotic_intent = tracker.is_erotic_intent(user)
        allow_erotic = True
        erotic_block_reasons = []
        if phase_state_before.phase in {
            ConversationPhase.OPENING,
            ConversationPhase.RAPPORT,
            ConversationPhase.FLIRTING,
        }:
            allow_erotic = False
            erotic_block_reasons.append("phase_early")
        if bot_profile.erotic_openness < 0.45:
            allow_erotic = False
            erotic_block_reasons.append("low_openness")
        if bot_profile.pace == "slow" and phase_state_before.intimacy_score < 0.40:
            allow_erotic = False
            erotic_block_reasons.append("slow_pace")
        if bot_profile.pace == "medium" and phase_state_before.intimacy_score < 0.30:
            allow_erotic = False
            erotic_block_reasons.append("mid_pace")

        if rule_hit or s.label == "MOVE":
            reply = boundary_safe_reply_contextual(
                user_text=user,
                phase=phase_state_before.phase.value,
                persona=args.persona,
                bot_profile=bot_profile,
            )
            mode = "SAFETY_REPAIR"
        elif erotic_intent and not allow_erotic:
            reply = soft_deflect_reply()
            mode = "SOFT_DEFLECT"
        else:
            system_context = build_system_context(
                phase_state_before,
                bot_profile,
                memory.get_highlights(),
                allow_erotic,
                args.user_gender,
                args.attraction,
            )
            messages = history + [{"role": "system", "content": system_context}]
            reply = llm.chat(messages)
            mode = "NORMAL"

        if mode == "SAFETY_REPAIR":
            safety_repair_count += 1
        if mode == "SOFT_DEFLECT":
            soft_deflect_count += 1
        if is_low_engagement(user):
            low_engagement_count += 1
        else:
            low_engagement_count = max(0, low_engagement_count - 1)

        should_block = False
        block_reasons = []
        if rule_hit and bot_profile.boundary_strictness >= 0.6:
            should_block = True
            block_reasons.append("rule_hit")
        if safety_repair_count >= 2 and bot_profile.boundary_strictness >= 0.7:
            should_block = True
            block_reasons.append("repeat_boundary")
        if soft_deflect_count >= 3 and erotic_intent:
            should_block = True
            block_reasons.append("repeat_escalation")
        if low_engagement_count >= 3 and bot_profile.directness >= 0.6:
            should_block = True
            block_reasons.append("low_engagement")

        if should_block:
            reply = "I don't think we're a match, so I'll bow out. Press Enter to exit the chatbot."
            mode = "BLOCK"

        history.append({"role": "assistant", "content": reply})

        if mode != "BLOCK":
            new_state = tracker.update(user, reply, s.label, rule_hit)
            added_items: List = []
            if s.label == "SAFE" and not rule_hit:
                added_items = memory.update_from_text(user)
        else:
            new_state = tracker.last_state
            added_items = []

        print(f"bot> {reply}")
        extra = f" rule={rule_reason}" if rule_hit else ""
        if mode == "SOFT_DEFLECT" and erotic_block_reasons:
            extra = f"{extra} deflect={','.join(erotic_block_reasons)}"
        if mode == "BLOCK" and block_reasons:
            extra = f"{extra} block={','.join(block_reasons)}"
        print(f"     [gate={s.label} p_move={s.p_move:.3f} thr={s.threshold:.2f} mode={mode}{extra}]")
        print(
            f"     [phase={new_state.phase.value} flirt={new_state.flirt_score:.2f} "
            f"intimate={new_state.intimacy_score:.2f} erotic={new_state.erotic_score:.2f}]",
            flush=True,
        )
        if added_items:
            print(
                f"     [memory:+{len(added_items)} items total={len(memory.items)}]",
                flush=True,
            )
        print("", flush=True)
        if mode == "BLOCK":
            input("Press Enter to exit the chatbot.")
            break


if __name__ == "__main__":
    main()
