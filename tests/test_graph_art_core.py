#!/usr/bin/env python3
"""Red contracts for the pure contribution-graph art core.

These tests intentionally describe the public API before its implementation
exists.  The import guard turns an absent package into assertion failures so
the red phase reports missing behavior rather than a harness/import error.
"""

from __future__ import annotations

import datetime as dt
import importlib
import unittest


def load(module_name: str):
    try:
        return importlib.import_module(module_name)
    except ModuleNotFoundError as error:
        if error.name == module_name or error.name.startswith("graph_art"):
            return None
        raise


CORE = load("graph_art.core")
SHAPES = load("graph_art.shapes")
PACKING = load("graph_art.packing")
COMMITS = load("graph_art.commits")


class CoreContracts(unittest.TestCase):
    def require(self, module, name: str):
        self.assertIsNotNone(module, f"missing graph-art behavior: {name}")
        self.assertTrue(hasattr(module, name), f"missing graph-art behavior: {name}")
        return getattr(module, name)

    def test_grid_is_53_columns_by_7_weekdays(self):
        width = self.require(CORE, "GRID_WIDTH")
        height = self.require(CORE, "GRID_HEIGHT")
        self.assertEqual(width, 53)
        self.assertEqual(height, 7)

    def test_date_mapping_uses_sunday_first_week_columns(self):
        date_to_cell = self.require(CORE, "date_to_cell")
        cell_to_date = self.require(CORE, "cell_to_date")
        first_sunday = dt.date(2026, 1, 4)

        self.assertEqual(date_to_cell(first_sunday, first_sunday), (0, 0))
        self.assertEqual(date_to_cell(first_sunday + dt.timedelta(days=6), first_sunday), (0, 6))
        self.assertEqual(date_to_cell(first_sunday + dt.timedelta(days=7), first_sunday), (1, 0))
        self.assertEqual(cell_to_date((4, 3), first_sunday), dt.date(2026, 2, 4))

    def test_date_mapping_rejects_cells_outside_the_grid(self):
        cell_to_date = self.require(CORE, "cell_to_date")
        with self.assertRaises(ValueError):
            cell_to_date((53, 0), dt.date(2026, 1, 4))
        with self.assertRaises(ValueError):
            cell_to_date((0, 7), dt.date(2026, 1, 4))

    def test_intensity_is_exactly_five_levels_and_maps_to_commit_counts(self):
        intensity_to_commits = self.require(CORE, "intensity_to_commit_count")
        levels = [intensity_to_commits(level) for level in range(5)]
        self.assertEqual(levels[0], 0)
        self.assertTrue(all(isinstance(value, int) and value >= 0 for value in levels))
        self.assertEqual(levels, sorted(set(levels)))
        with self.assertRaises(ValueError):
            intensity_to_commits(-1)
        with self.assertRaises(ValueError):
            intensity_to_commits(5)

    def test_grid_preserves_empty_and_occupied_cells(self):
        grid_type = self.require(CORE, "ContributionGrid")
        grid = grid_type.empty()
        self.assertEqual(grid.get((2, 3)), 0)
        grid.set((2, 3), 4)
        self.assertEqual(grid.get((2, 3)), 4)
        self.assertNotIn((2, 3), set(grid.available_cells()))
        with self.assertRaises(ValueError):
            grid.set((53, 0), 1)


class ShapeContracts(unittest.TestCase):
    def require(self, name: str):
        self.assertIsNotNone(SHAPES, f"missing graph-art behavior: {name}")
        self.assertTrue(hasattr(SHAPES, name), f"missing graph-art behavior: {name}")
        return getattr(SHAPES, name)

    def test_five_starter_shapes_are_available(self):
        shape_names = self.require("STARTER_SHAPES")
        self.assertEqual(
            tuple(shape_names),
            ("cube", "diamond", "pyramid", "staircase", "wedge"),
        )

    def test_shapes_rasterize_to_small_shaded_integer_sprites(self):
        rasterize = self.require("rasterize_shape")
        for name in ("cube", "diamond", "pyramid", "staircase", "wedge"):
            with self.subTest(shape=name):
                sprite = rasterize(name)
                self.assertTrue(sprite)
                self.assertLessEqual(len(sprite), 7)
                self.assertTrue(all(len(row) == len(sprite[0]) for row in sprite))
                self.assertLessEqual(len(sprite[0]), 7)
                values = {value for row in sprite for value in row}
                self.assertTrue(values <= {0, 1, 2, 3, 4})
                self.assertIn(0, values)
                self.assertGreaterEqual(len(values - {0}), 2)

    def test_unknown_shape_is_rejected(self):
        rasterize = self.require("rasterize_shape")
        with self.assertRaises(ValueError):
            rasterize("octahedron")


class PackingContracts(unittest.TestCase):
    def require(self, name: str):
        self.assertIsNotNone(PACKING, f"missing graph-art behavior: {name}")
        self.assertTrue(hasattr(PACKING, name), f"missing graph-art behavior: {name}")
        return getattr(PACKING, name)

    def test_packing_is_deterministic_and_stays_in_available_cells(self):
        grid_type = self.require_from_core("ContributionGrid")
        pack_shapes = self.require("pack_shapes")
        grid = grid_type.empty()
        grid.set((0, 0), 4)
        grid.set((52, 6), 2)
        names = ("cube", "diamond", "pyramid", "staircase", "wedge")

        first = pack_shapes(grid, names, seed=17)
        second = pack_shapes(grid, names, seed=17)
        self.assertEqual(first, second)

        occupied = set()
        for placement in first:
            cells = placement["cells"]
            self.assertTrue(cells)
            for x, y, intensity in cells:
                self.assertIn(x, range(53))
                self.assertIn(y, range(7))
                self.assertIn(intensity, range(1, 5))
                self.assertEqual(grid.get((x, y)), 0)
                self.assertNotIn((x, y), occupied)
                occupied.add((x, y))

    def require_from_core(self, name: str):
        self.assertIsNotNone(CORE, f"missing graph-art behavior: {name}")
        self.assertTrue(hasattr(CORE, name), f"missing graph-art behavior: {name}")
        return getattr(CORE, name)


class CommitPlanContracts(unittest.TestCase):
    def require(self, name: str):
        self.assertIsNotNone(COMMITS, f"missing graph-art behavior: {name}")
        self.assertTrue(hasattr(COMMITS, name), f"missing graph-art behavior: {name}")
        return getattr(COMMITS, name)

    def test_commit_plan_maps_cells_to_dates_and_positive_counts(self):
        build_plan = self.require("build_commit_plan")
        first_sunday = dt.date(2026, 1, 4)
        placements = [
            {"shape": "cube", "cells": ((0, 0, 1), (1, 0, 3), (1, 1, 4))},
        ]
        plan = build_plan(placements, first_sunday)
        self.assertEqual(
            plan,
            {
                dt.date(2026, 1, 4): 1,
                dt.date(2026, 1, 11): 3,
                dt.date(2026, 1, 12): 4,
            },
        )
        self.assertTrue(all(isinstance(count, int) and count > 0 for count in plan.values()))

    def test_commit_plan_rejects_zero_intensity_cells(self):
        build_plan = self.require("build_commit_plan")
        with self.assertRaises(ValueError):
            build_plan([{"shape": "cube", "cells": ((0, 0, 0),)}], dt.date(2026, 1, 4))


if __name__ == "__main__":
    unittest.main()
