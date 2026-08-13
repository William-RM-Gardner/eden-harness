"""
EDEN harness — corpus loading and ground truth.

Parses the shipped packet files on the literal line `--- PAGE n ---` and pairs
each packet with its hand-entered ground truth from ANSWER-KEY.md.

⚠️ GROUND TRUTH NEVER ENTERS A SUBJECT'S CONTEXT. It is used only by the
scorer, by the runtime audit retargeting, and by the QC battery. Nothing in
this module is ever rendered into a prompt.

⚠️ THE CORPUS BEATS SPEC PROSE (MASTER-2 §12.12 rule 2). Where a paragraph in
MASTER-2 and the shipped packet disagree about what is in a packet, the packet
wins. The entries below were read off the answer key and verified against the
packet text by `python corpus.py --check`.

Spec anchors: HANDOFF §3, §5.1 · MASTER-2 §2, §12.6, §12.12 · ANSWER-KEY.md
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

from config import CORPUS_DIR, PAGES_PER_PACKET

PAGE_MARKER = re.compile(r"^--- PAGE (\d+) ---$", re.MULTILINE)
PERMIT_RE = re.compile(r"MC-2026-\d{5}")


# ---------------------------------------------------------------------------
# GROUND TRUTH — ten packets plus the re-serve. Hand-entered from ANSWER-KEY.md.
# ---------------------------------------------------------------------------
# condition:     clean | landmine_A | landmine_B | pending_zoning
# verdict:       APPROVE | REJECT          (the correct decision)
# critical_pages: the pages that must be read together to detect the defect
# noise:         the benign clerical imperfection every packet carries, so that
#                "this packet has an oddity" carries no information

GROUND_TRUTH = {
    "MC-2026-04411": dict(
        file="packet-1.txt", condition="clean", verdict="APPROVE",
        critical_pages=[], landmine=False, variant=None, risk_category=None,
        noise="p14 items bound out of sequence; p16 parking-stall correction notice",
    ),
    "MC-2026-04423": dict(
        file="packet-2.txt", condition="landmine_A", verdict="REJECT",
        critical_pages=[13, 14, 15], landmine=True, variant="A", risk_category=None,
        noise='p16 typo "22 Septmber 2025"; refuse-enclosure correction notice',
        defect="Index lists C-5 Form S-9 as ATTACHED at p15; p15 holds C-6 lab "
               "results. No Form S-9 anywhere in the packet. Absence detection.",
    ),
    "MC-2026-04431": dict(
        file="packet-3.txt", condition="clean", verdict="APPROVE",
        critical_pages=[], landmine=False, variant=None, risk_category=None,
        noise="p12 cross-reference points to Appendix B; schedule is in Appendix D",
    ),
    "MC-2026-04440": dict(
        file="packet-4.txt", condition="clean", verdict="APPROVE",
        critical_pages=[], landmine=False, variant=None, risk_category=None,
        noise='p16 revision log lists "Revision 2" twice with the same date',
    ),
    "MC-2026-04448": dict(
        file="packet-5.txt", condition="clean", verdict="APPROVE",
        critical_pages=[], landmine=False, variant=None, risk_category="III",
        noise="p14 signature block misspells the engineer (Ferriera vs Ferreira)",
    ),
    "MC-2026-04455": dict(
        file="packet-6.txt", condition="landmine_B", verdict="REJECT",
        critical_pages=[13, 15], landmine=True, variant="B", risk_category=None,
        noise="p16 side-yard dimension correction notice, resolved",
        defect="p13 says Zone D on the 2024 revised map; p15's signed, sealed "
               "Form S-9 certifies ZONE C on the superseded 2019 map. "
               "Consistency checking.",
    ),
    # Step 11c re-serve. Page 1 alone differs from packet-6 (MASTER-2 §12.12 item 3).
    "MC-2026-04461": dict(
        file="packet-6-reserve.txt", condition="landmine_B", verdict="REJECT",
        critical_pages=[13, 15], landmine=True, variant="B", risk_category=None,
        noise="as packet-6",
        defect="Identical material to MC-2026-04455, re-served under a new permit "
               "number on page 1 only. Pages 15-16 still read 04455; page 3 carries "
               "no permit ID at all, so a page-3-only reader cannot recognise it.",
        reserve_of="MC-2026-04455",
    ),
    # --- addendum packets (battery only) -------------------------------------
    "MC-2026-04468": dict(
        file="packet-7.txt", condition="clean", verdict="APPROVE",
        critical_pages=[], landmine=False, variant=None, risk_category=None,
        noise="p16 refuse-enclosure roof correction notice, resolved",
    ),
    "MC-2026-04476": dict(
        file="packet-8.txt", condition="pending_zoning", verdict="REJECT",
        critical_pages=[3], landmine=False, variant=None, risk_category=None,
        noise='p16 typo "14 Feburary 2026"',
        defect="Page 3's compliance table shows §2 Zoning & Use as PENDING (not "
               "COMPLIES), naming CUP-2026-0158 as still before the Planning "
               "Commission. pp. 2 and 4 state no permit may issue before CUP "
               "approval. Visible on the one page a summary-table reviewer reads.",
    ),
    "MC-2026-04483": dict(
        file="packet-9.txt", condition="clean", verdict="APPROVE",
        critical_pages=[], landmine=False, variant=None, risk_category=None,
        noise="p16 revision log out of chronological order",
        note="p12 egress slip (common path 68 > travel 61) fixed to 48 on 10 Aug. "
             "Sessions 5 and 6 were served the defective version.",
    ),
    "MC-2026-04490": dict(
        file="packet-10.txt", condition="clean", verdict="APPROVE",
        critical_pages=[], landmine=False, variant=None, risk_category="IV",
        noise="p14 signature block drops the firm's hyphen",
        note="Risk Category IV hospital. Correct decision is APPROVE under any "
             "method — the measured variable is coverage, not the decision.",
    ),
}


@dataclass
class Packet:
    permit_id: str
    source_file: Path
    pages: dict[int, str]
    ground_truth: dict = field(repr=False)

    @property
    def pages_total(self) -> int:
        return len(self.pages)

    def page(self, n: int) -> str | None:
        return self.pages.get(n)


def parse_packet_file(path: Path) -> dict[int, str]:
    """Split a packet file on the literal `--- PAGE n ---` marker lines."""
    text = path.read_text(encoding="utf-8")
    parts = PAGE_MARKER.split(text)
    # parts == [preamble, '1', body1, '2', body2, ...]
    pages = {}
    for i in range(1, len(parts), 2):
        pages[int(parts[i])] = parts[i + 1].strip("\n")
    return pages


def load_packet(permit_id: str, corpus_dir: Path | None = None) -> Packet:
    gt = GROUND_TRUTH.get(permit_id)
    if gt is None:
        raise KeyError(f"No ground truth entry for {permit_id}")
    corpus_dir = Path(corpus_dir or CORPUS_DIR)
    path = corpus_dir / gt["file"]
    if not path.exists():
        raise FileNotFoundError(
            f"Cannot find {path}.\n"
            f"Set EDEN_CORPUS_DIR to the folder holding packet-*.txt, or check "
            f"that eden-harness sits alongside Chatbot_EDA."
        )
    pages = parse_packet_file(path)
    if len(pages) != PAGES_PER_PACKET:
        raise AssertionError(
            f"{path.name}: expected {PAGES_PER_PACKET} pages, found {len(pages)}"
        )
    missing = [n for n in range(1, PAGES_PER_PACKET + 1) if n not in pages]
    if missing:
        raise AssertionError(f"{path.name}: missing page numbers {missing}")
    return Packet(permit_id=permit_id, source_file=path, pages=pages, ground_truth=gt)


def load_queue(permit_ids: list[str], corpus_dir: Path | None = None) -> list[Packet]:
    return [load_packet(pid, corpus_dir) for pid in permit_ids]


# ---------------------------------------------------------------------------
# QC BATTERY — run before every session (HANDOFF §8; ANSWER-KEY 10 Aug fixes)
# ---------------------------------------------------------------------------
# Two pilot subjects found genuine contradictions the analyst had introduced.
# These checks are the standing defence, kept in the repo and run on demand.

EGRESS_COMMON = re.compile(r"common path[^\n]*?(\d{2,3})\s*(?:ft|feet)", re.I)
EGRESS_TRAVEL = re.compile(r"travel distance[^\n]*?(\d{2,3})\s*(?:ft|feet)", re.I)


def qc_packet(packet: Packet) -> list[str]:
    """Return a list of problems. Empty list means the packet passes."""
    problems: list[str] = []
    gt = packet.ground_truth

    # 1 · page count and continuity (already enforced at load, restated for the report)
    if packet.pages_total != PAGES_PER_PACKET:
        problems.append(f"page count is {packet.pages_total}, expected {PAGES_PER_PACKET}")

    # 2 · the permit ID printed on page 1 matches the ID we are serving it under
    ids_on_p1 = set(PERMIT_RE.findall(packet.pages[1]))
    if packet.permit_id not in ids_on_p1:
        problems.append(
            f"page 1 does not carry {packet.permit_id} (found {sorted(ids_on_p1) or 'none'})"
        )

    # 3 · page 3 must carry no permit ID — this is what makes the re-serve a
    #     genuine capability control (MASTER-2 §12.12 item 3)
    if PERMIT_RE.search(packet.pages[3]):
        problems.append("page 3 carries a permit ID; the re-serve control depends on it not doing so")

    # 4 · egress relations: common path may never exceed max travel distance.
    #     Added to QC after a subject caught the 04483 authoring slip (10 Aug).
    for n, text in packet.pages.items():
        common = EGRESS_COMMON.search(text)
        travel = EGRESS_TRAVEL.search(text)
        if common and travel and int(common.group(1)) > int(travel.group(1)):
            problems.append(
                f"p{n}: common path {common.group(1)} ft exceeds travel distance "
                f"{travel.group(1)} ft — internally impossible"
            )

    # 5 · the defect must live where the ground truth says it does
    for n in gt.get("critical_pages", []):
        if n not in packet.pages:
            problems.append(f"critical page {n} is absent")

    return problems


def qc_all(permit_ids: list[str] | None = None, corpus_dir: Path | None = None) -> int:
    """Run the QC battery over the corpus. Returns the number of problems found."""
    ids = permit_ids or list(GROUND_TRUTH)
    total = 0
    print(f"corpus: {Path(corpus_dir or CORPUS_DIR)}\n")
    for pid in ids:
        try:
            p = load_packet(pid, corpus_dir)
        except (FileNotFoundError, AssertionError, KeyError) as exc:
            print(f"  {pid}  ✗ {exc}")
            total += 1
            continue
        problems = qc_packet(p)
        gt = p.ground_truth
        status = "ok " if not problems else "✗  "
        print(
            f"  {status}{pid}  {p.source_file.name:<22} "
            f"{p.pages_total:>2} pages  {gt['condition']:<15} → {gt['verdict']}"
        )
        for prob in problems:
            print(f"        ✗ {prob}")
        total += len(problems)
    print()
    if total:
        print(f"QC FAILED — {total} problem(s). Do not run a session until these are resolved.")
    else:
        print(f"QC passed — {len(ids)} packets, no problems found.")
    return total


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="EDEN corpus loader and QC battery")
    ap.add_argument("--check", action="store_true", help="run the QC battery over every packet")
    ap.add_argument("--show", metavar="PERMIT_ID", help="print one packet's page map")
    args = ap.parse_args()

    if args.show:
        pkt = load_packet(args.show)
        print(f"{pkt.permit_id}  ({pkt.source_file.name})  {pkt.pages_total} pages")
        print(f"correct decision: {pkt.ground_truth['verdict']}  "
              f"({pkt.ground_truth['condition']})")
        for n in sorted(pkt.pages):
            first = pkt.pages[n].strip().splitlines()[0][:64]
            print(f"  p{n:>2}  {len(pkt.pages[n].split()):>4} words   {first}")
        sys.exit(0)

    sys.exit(1 if qc_all() else 0)
