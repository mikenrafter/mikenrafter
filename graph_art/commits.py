"""Turn packed graph cells into a date-to-commit-count plan."""

from __future__ import annotations

import datetime as _datetime

from .core import cell_to_date, intensity_to_commit_count


def build_commit_plan(
    placements: list[dict[str, object]], first_sunday: _datetime.date
) -> dict[_datetime.date, int]:
    plan: dict[_datetime.date, int] = {}
    for placement in placements:
        for x, y, intensity in placement["cells"]:  # type: ignore[index]
            count = intensity_to_commit_count(intensity)
            if count == 0:
                raise ValueError("commit-plan cells must have positive intensity")
            date = cell_to_date((x, y), first_sunday)
            plan[date] = plan.get(date, 0) + count
    return plan
