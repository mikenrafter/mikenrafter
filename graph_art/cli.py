"""Command-line entry point for deterministic contribution-graph art."""

from __future__ import annotations

import argparse
import datetime as _datetime
import json
from pathlib import Path

from .commits import build_commit_plan
from .core import ContributionGrid, cell_to_date
from .packing import pack_shapes
from .shapes import STARTER_SHAPES


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="graph-packing",
        description="Pack shaded geometric sprites into a GitHub contribution grid.",
    )
    parser.add_argument(
        "--shape",
        action="append",
        dest="shapes",
        choices=STARTER_SHAPES,
        help="Shape to place; may be repeated (defaults to one of each starter shape).",
    )
    parser.add_argument("--seed", type=int, default=0, help="Deterministic packing seed.")
    parser.add_argument(
        "--first-sunday",
        type=_datetime.date.fromisoformat,
        default=_datetime.date(2026, 1, 4),
        metavar="YYYY-MM-DD",
        help="Date represented by grid cell (0, 0).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        metavar="PATH",
        help="Write the JSON commit plan to PATH instead of stdout.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    shape_names = args.shapes or list(STARTER_SHAPES)
    placements = pack_shapes(ContributionGrid.empty(), shape_names, seed=args.seed)
    plan = build_commit_plan(placements, args.first_sunday)
    payload = {
        "first_sunday": args.first_sunday.isoformat(),
        "seed": args.seed,
        "placements": placements,
        "commit_plan": {date.isoformat(): count for date, count in sorted(plan.items())},
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
