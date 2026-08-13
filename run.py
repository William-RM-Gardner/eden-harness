"""
EDEN harness — run one episode.

Examples
--------
    # offline smoke test, costs nothing, no API key needed
    py run.py --model mock-full --arm no-partner
    py run.py --model mock-page3 --arm partner --seed 2

    # a real subject, once you have put the model IDs in config.py
    py run.py --model openai --arm partner --seed 1
    py run.py --model deepseek --arm no-partner --seed 3

    # add the discretionary battery (stretch, HANDOFF §4)
    py run.py --model mock-kernel --arm partner --battery
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

import config
from corpus import load_packet, qc_all
from episode import Episode
from models import MockSubject, RemoteSubject


# The modules that actually RUN an episode. score.py is deliberately excluded:
# it plays no part in producing a log, and editing it during analysis must not
# make byte-identical runtime code look like different provenance (12 Aug
# review, round 3, item 1). An explicit list also means a scratch .py dropped
# in the folder cannot shift the hash.
RUNTIME_MODULES = ("config.py", "corpus.py", "events.py", "models.py",
                   "episode.py", "parsing.py", "run.py")


def _hash_files(names) -> str:
    import hashlib
    h = hashlib.sha256()
    here = Path(__file__).resolve().parent
    for name in names:
        f = here / name
        h.update(name.encode())
        h.update(f.read_bytes() if f.exists() else b"<absent>")
    return h.hexdigest()[:16]


def harness_source_hash() -> str:
    """Fingerprint of the runtime modules only — 'which code ran the episode'.
    If two logs carry the same hash, the same runtime code produced them."""
    return _hash_files(RUNTIME_MODULES)


def git_commit() -> str | None:
    """Best-effort: the current commit (+'-dirty' if uncommitted changes), or
    None when no git repo exists. The hash says two runs differ; git history
    says what changed — run `git init` in eden-harness to get the latter."""
    import subprocess
    here = Path(__file__).resolve().parent
    try:
        rev = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=here,
                             capture_output=True, text=True, timeout=5)
        if rev.returncode != 0:
            return None
        dirty = subprocess.run(["git", "status", "--porcelain"], cwd=here,
                               capture_output=True, text=True, timeout=5)
        suffix = "-dirty" if dirty.stdout.strip() else ""
        return rev.stdout.strip() + suffix
    except Exception:
        return None


def environment_meta() -> dict:
    """
    Record the exact stack the episode ran on. HANDOFF §9: "log whatever you set."
    This is what the methods section quotes, and what makes a rerun a rerun.
    """
    import platform
    meta = {
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "harness_source_hash": harness_source_hash(),
        "scorer_source_hash": _hash_files(("score.py",)),
        "git_commit": git_commit(),
    }
    try:
        import openai
        meta["openai_sdk_version"] = openai.__version__
    except Exception:
        meta["openai_sdk_version"] = None
    return meta


# ⚠️ FROZEN — this rule is pre-registered verbatim. The assignment depends on
# these exact orderings; both are asserted so a refactor cannot silently
# reassign polarity across the grid (12 Aug review finding).
_POLARITY_ARMS = ("partner", "no-partner")
FAMILY_INDEX = {"openai": 0, "deepseek": 1, "mock": 0}


def assigned_polarity(family: str, arm: str, seed: int) -> str:
    """
    Audit polarity, balanced by design (decision of 12 Aug, replacing a per-seed
    random draw that yielded 'true' for seeds 1-4 and 6 — the false audit would
    never have fired across the planned grid). Parity of (seed + arm + family)
    gives exactly 6 true / 6 false over 2 families × 3 seeds × 2 arms, balanced
    3/3 within every family and every arm. Override per-run with --polarity.
    """
    if tuple(config.ARMS) != _POLARITY_ARMS:
        raise SystemExit(
            "config.ARMS no longer matches the pre-registered polarity rule "
            f"({_POLARITY_ARMS}). Changing arm order silently reassigns polarity "
            "across the whole grid — update assigned_polarity deliberately, and "
            "amend prereg.md, or restore ARMS."
        )
    if family not in FAMILY_INDEX:
        raise SystemExit(
            f"Family '{family}' is not in the pre-registered polarity mapping "
            f"({dict(FAMILY_INDEX)}). Add it to FAMILY_INDEX deliberately — a "
            "silent default would hand it another family's assignments."
        )
    arm_idx = _POLARITY_ARMS.index(arm)
    return "true" if (seed + arm_idx + FAMILY_INDEX[family]) % 2 == 0 else "false"


def build_subject(name: str, seed: int):
    spec = config.MODELS.get(name)
    if spec is None:
        raise SystemExit(f"Unknown model '{name}'. Known: {', '.join(config.MODELS)}")
    if spec["provider"] == "mock":
        return MockSubject(spec["behaviour"]), spec
    if "REPLACE-ME" in str(spec.get("model", "")):
        raise SystemExit(
            f"config.MODELS['{name}']['model'] is still a placeholder.\n"
            f"Put the exact API model identifier there first, and record it in prereg.md."
        )
    # --seed is passed to the API only where the provider supports it
    # (config: send_seed). Where it is not sent, seeds are replicate labels —
    # unseeded samples at provider defaults, the pilot's own configuration —
    # and prereg.md must say so (12 Aug review finding).
    api_seed = seed if spec.get("send_seed") else None
    # reasoning_effort is PER MODEL: sending it globally would 400 on a provider
    # that rejects unknown params. The spec value wins; config.REASONING_EFFORT
    # is the fallback for models with no entry.
    effort = spec.get("reasoning_effort", config.REASONING_EFFORT)
    return RemoteSubject(spec,
                         temperature=config.TEMPERATURE,
                         max_tokens=config.MAX_TOKENS,
                         reasoning_effort=effort,
                         seed=api_seed), spec


def main(argv=None):
    ap = argparse.ArgumentParser(description="Run one EDEN episode")
    ap.add_argument("--model", required=True, help=f"one of: {', '.join(config.MODELS)}")
    ap.add_argument("--arm", default="partner", choices=config.ARMS)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--battery", action="store_true", help="add the discretionary battery (packets 7-10)")
    ap.add_argument("--polarity", choices=["true", "false"], default=None,
                    help="override the assigned audit polarity (default: balanced rule)")
    ap.add_argument("--skip-qc", action="store_true", help="skip the corpus QC battery (don't)")
    args = ap.parse_args(argv)

    # Load .env if present, so API keys never live in the shell history.
    try:
        from dotenv import load_dotenv
        load_dotenv(config.REPO_ROOT / ".env")
    except ImportError:
        pass

    # ⚠️ QC before every run. Two pilot subjects found genuine authoring errors;
    # this is the standing defence (HANDOFF §8).
    if not args.skip_qc:
        needed = config.BASE_QUEUE + [config.RESERVE_PERMIT] + (config.BATTERY_QUEUE if args.battery else [])
        if qc_all(needed):
            raise SystemExit("QC failed — fix the corpus before running.")

    subject, spec = build_subject(args.model, args.seed)

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_id = f"{args.model}_{args.arm}_seed{args.seed}_{stamp}"
    log_path = config.RESULTS_DIR / f"{run_id}.jsonl"

    queue = [load_packet(pid) for pid in config.BASE_QUEUE]
    reserve = load_packet(config.RESERVE_PERMIT)
    battery = [load_packet(pid) for pid in config.BATTERY_QUEUE] if args.battery else []
    polarity = args.polarity or assigned_polarity(spec["family"], args.arm, args.seed)

    print(f"\nEDEN episode  ·  {run_id}")
    print(f"  arm       {args.arm}")
    print(f"  subject   {spec.get('model', spec.get('behaviour'))}  (family: {spec['family']})")
    print(f"  queue     {len(queue)} packets + re-serve" + (f" + {len(battery)} battery" if battery else ""))
    print(f"  polarity  {polarity} (audit; balanced rule" + (", overridden)" if args.polarity else ")"))
    print(f"  log       {log_path}\n")

    ep = Episode(
        subject, arm=args.arm, queue=queue, reserve=reserve, battery=battery,
        seed=args.seed, run_id=run_id, log_path=log_path,
        audit_polarity=polarity,
        meta={
            "model_key": args.model,
            "model_id": spec.get("model"),
            "family": spec["family"],
            "temperature": config.TEMPERATURE,
            "reasoning_effort": spec.get("reasoning_effort", config.REASONING_EFFORT),
            "harness_version": "0.3",
            "audit_polarity_assigned": polarity,
            "api_seed_sent": bool(spec.get("send_seed")) and spec["provider"] != "mock",
            **environment_meta(),
        },
    )
    try:
        ep.run()
    except KeyboardInterrupt:
        ep.log("episode_interrupted", reason="KeyboardInterrupt")
        ep.close()
        print("\nInterrupted. The log up to this point is intact.")
        return 130

    scored = [d for d in ep.decisions if not d.get("superseded_by_correction")]
    correct = sum(1 for d in scored if d.get("correct"))
    print(f"\n  done · {ep.round} rounds · {len(ep.deliveries)} pages delivered · "
          f"{correct}/{len(scored)} decisions correct · "
          f"{len(ep.clarifications)} clarification request(s)")
    print(f"  log: {log_path}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
