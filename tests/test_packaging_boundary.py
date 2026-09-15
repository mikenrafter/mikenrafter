#!/usr/bin/env python3
"""Red contracts for the mikenrafter scout-module packaging boundary.

These tests intentionally describe the flake layout consumed by phoe-nix before
the packaging implementation exists.  Missing files are reported as ordinary
assertion failures so the red phase remains useful without importing Nix or
nix-scout.
"""

from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
MODULES = ROOT / "modules"
PACKING = MODULES / "graph-packing"
SNAKE = MODULES / "graph-snake"


def read_contract(path: pathlib.Path, testcase: unittest.TestCase) -> str:
    testcase.assertTrue(path.is_file(), f"missing packaging contract file: {path}")
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def assert_flakelet_default(testcase: unittest.TestCase, text: str, module: str) -> None:
    testcase.assertRegex(
        text,
        r"(?s)flakelets\s*=\s*\{.*?\bdefault\b",
        f"{module} flake must export flakelets.default",
    )


class TopLevelFlakeContracts(unittest.TestCase):
    def test_root_declares_the_mikenrafter_flake(self):
        text = read_contract(ROOT / "flake.nix", self)
        self.assertRegex(text, r"(?i)mikenrafter")
        self.assertRegex(text, r"(?s)description\s*=\s*[^;]*mikenrafter")

    def test_root_exposes_the_two_scout_module_flakelets(self):
        text = read_contract(ROOT / "flake.nix", self)
        self.assertIn("graph-packing", text)
        self.assertIn("graph-snake", text)


class ModuleFlakeContracts(unittest.TestCase):
    def test_graph_packing_has_flakelet_and_settings(self):
        text = read_contract(PACKING / "flake.nix", self)
        read_contract(PACKING / "settings.nix", self)
        assert_flakelet_default(self, text, "graph-packing")

    def test_graph_snake_has_flakelet_and_settings(self):
        text = read_contract(SNAKE / "flake.nix", self)
        read_contract(SNAKE / "settings.nix", self)
        assert_flakelet_default(self, text, "graph-snake")


class GraphPackingExportContracts(unittest.TestCase):
    def test_graph_packing_exports_named_runnable_cli_package(self):
        text = read_contract(PACKING / "flake.nix", self)
        self.assertRegex(text, r"(?s)packages?\s*=.*graph-packing")
        self.assertRegex(
            text,
            r"(?s)(apps|programs|executable|bin)\s*=.*graph-packing",
            "graph-packing must expose a runnable CLI/package",
        )

    def test_graph_packing_export_is_wired_to_graph_art_code(self):
        text = read_contract(PACKING / "flake.nix", self)
        self.assertRegex(text, r"graph_art|graph-art|graph_packing|graph-packing")


class GraphSnakeExportContracts(unittest.TestCase):
    def test_graph_snake_exports_generator_package(self):
        text = read_contract(SNAKE / "flake.nix", self)
        self.assertRegex(text, r"(?s)packages?\s*=.*(?:snake|graph-snake)")
        self.assertRegex(text, r"(?i)generator|svg|snake")

    def test_graph_snake_exports_service_contract(self):
        text = read_contract(SNAKE / "flake.nix", self)
        self.assertRegex(
            text,
            r"(?i)service|systemd|scout",
            "graph-snake must expose its migrated service contract",
        )


if __name__ == "__main__":
    unittest.main()
