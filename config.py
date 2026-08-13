"""
EDEN harness — configuration.

Everything you might reasonably want to change lives here. Nothing else in the
repo should need editing to run a different model, arm, or seed.

Spec anchors: HANDOFF-Harness-Build-Brief §2, §4, §9 · MASTER-2 §12.7, §12.12.
"""

from __future__ import annotations

import os
from pathlib import Path

# --------------------------------------------------------------------------
# PATHS
# --------------------------------------------------------------------------
# The repo lives at ...\Apart\eden-harness, and the corpus at ...\Apart\Chatbot_EDA\Corpus,
# so the default is one level up and across. Override with the EDEN_CORPUS_DIR
# environment variable if you ever move either one.

REPO_ROOT = Path(__file__).resolve().parent
CORPUS_DIR = Path(
    os.environ.get("EDEN_CORPUS_DIR", REPO_ROOT.parent / "Chatbot_EDA" / "Corpus")
)
RESULTS_DIR = Path(os.environ.get("EDEN_RESULTS_DIR", REPO_ROOT / "results"))

# --------------------------------------------------------------------------
# SUBJECT MODELS
# --------------------------------------------------------------------------
# Do NOT run Claude as a subject (HANDOFF §2). OpenAI and DeepSeek only —
# the two families the pilot ran.
#
# Model IDs decided 13 Aug (Will): top-tier subjects from each family — that is
# where lab effort concentrates and what pushes the field. Record both in
# prereg.md. Confirm each against the live /models listing before the first
# analysed run; if a provider exposes a variant string (e.g. a -preview
# suffix), use the listed string and update here.

MODELS = {
    # --- real subjects -------------------------------------------------
    "openai": {
        "provider": "openai",
        "model": "gpt-5.6-sol",                # the pilot's family/tier: ChatGPT 5.6 Sol
        "base_url": None,                       # default OpenAI endpoint
        "api_key_env": "OPENAI_API_KEY",
        "family": "openai",
        "send_seed": True,     # OpenAI accepts a seed param (best-effort determinism)
        "reasoning_effort": "high",  # matches sessions 1b/5 (Effort High). Set to
                                     # None for provider default; either way logged.
    },
    "deepseek": {
        "provider": "openai",                   # DeepSeek is OpenAI-API-compatible
        "model": "deepseek-v4-pro",            # top-tier pick (13 Aug). ⚠️ Confirm
                                                # against /models: the changelog
                                                # listed Pro's official release as
                                                # pending — if the listing shows a
                                                # variant string, use that one.
                                                # Limitations note: the hand pilot
                                                # ran the consumer surface (V4-Flash
                                                # era); the API subject is V4-Pro.
        "base_url": "https://api.deepseek.com",
        "api_key_env": "DEEPSEEK_API_KEY",
        "family": "deepseek",
        "send_seed": False,    # not confirmed supported; flip to True only after
                               # verifying the API accepts it without erroring
        "reasoning_effort": None,   # do not send; unknown-param 400 risk
    },
    # --- offline stand-ins, for testing the harness without spending money ---
    # These are not subjects and never appear in results. They exist so the
    # whole protocol can be exercised deterministically before the first API call.
    "mock-full": {"provider": "mock", "behaviour": "full_reader", "family": "mock"},
    "mock-page3": {"provider": "mock", "behaviour": "page3_only", "family": "mock"},
    "mock-kernel": {"provider": "mock", "behaviour": "kernel", "family": "mock"},
    "mock-miss-a": {"provider": "mock", "behaviour": "full_reader_misses_a", "family": "mock"},
    "mock-waiver-flip": {"provider": "mock", "behaviour": "waiver_flip", "family": "mock"},
}

# --------------------------------------------------------------------------
# SAMPLING
# --------------------------------------------------------------------------
# The pilot ran consumer defaults. HANDOFF §9: "log whatever you set."
# TEMPERATURE = None means "send no temperature parameter, take the provider default",
# which is the closest API analogue of what the pilot actually did.

TEMPERATURE: float | None = None
MAX_TOKENS: int | None = None

# Reasoning effort / thinking mode is a recorded config variable in every
# session (MASTER-2 §12.7). Set to None if the provider does not accept it.
REASONING_EFFORT: str | None = None

# --------------------------------------------------------------------------
# EPISODE SHAPE
# --------------------------------------------------------------------------
# HANDOFF §4: one protocol, the base episode — 6 packets, ~15-20 rounds.
# Queue length is a config parameter, not a constant (MASTER-2 §10b).

BASE_QUEUE = [
    "MC-2026-04411",   # Step 2  · clean       · onboarding, one-time R-2 correction allowed here only
    "MC-2026-04423",   # Step 3  · landmine A  · absence detection
    "MC-2026-04431",   # Step 4  · clean       · partner arrives before this one
    "MC-2026-04440",   # Step 6  · clean       · under deadline
    "MC-2026-04448",   # Step 8  · clean       · silence
    "MC-2026-04455",   # Step 9  · landmine B  · consistency checking
]
RESERVE_PERMIT = "MC-2026-04461"   # Step 11c, served from packet-6-reserve.txt

# Stretch (HANDOFF §4): the discretionary battery, packets 7-10 after the waiver.
# Off by default — turn on with --battery once the base episode is banked.
BATTERY_QUEUE = ["MC-2026-04468", "MC-2026-04476", "MC-2026-04483", "MC-2026-04490"]

PAGES_PER_PACKET = 16
QUEUE_SIZE_STATED_TO_SUBJECT = 8   # verbatim from MASTER-4 Step 1; see events.py

# Safety rails. A runaway loop burns tokens silently, so both are hard stops.
MAX_ROUNDS_PER_PACKET = 40
MAX_ROUNDS_PER_EPISODE = 400

# --------------------------------------------------------------------------
# ARMS
# --------------------------------------------------------------------------
# HANDOFF §4: two arms only.
#   partner     — C1, Agent E exempt and present
#   no-partner  — C3, the baseline. No Agent E, no dashboard, no deadline.
#
# In no-partner, MASTER-4 Part 6 session 1 routes 1→2→3→8→9→10→12. Steps 11a
# and 11b are unrunnable there (both name Agent E), but 11c (waiver — a primary
# instrument, MASTER-2 §5A V3b) and 11d (inventory/grounds — "every episode, all
# conditions", §12.9) must still run. So no-partner = 1,2,3,8,9,10,11c,11d,12.

ARMS = ("partner", "no-partner")
